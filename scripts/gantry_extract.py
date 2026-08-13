#!/usr/bin/env python3
"""gantry extract — deterministic parser: client repo truth -> state.json.

stdlib only. No wall-clock, no randomness, no network. Same client commit +
same adapter ==> byte-identical output. See docs/03-pipeline.md.

Two homes (scripts/adopt.sh decides):
  - observer side: run from the gantry repo over any client checkout
      python3 scripts/gantry_extract.py --client ADAPTER --root CLIENT ...
  - adopted client: copied into <client>/tools/gantry_extract.py and COMMITTED
    there, so the client carries its own GRAPH.md builder. Computes paths from
    arguments only — the same file works from either home.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

EXTRACTOR_VERSION = "0.4.2"
SCHEMA_VERSION = "0.2"
DEP_TYPES = {"blocks", "awaits-stamp", "defers-to", "informs"}

ID_RE = re.compile(r"^(constraint|part|seam|gate|phase|workorder|hold|stamp):[a-z0-9][a-z0-9-]*$")
HUMAN_GATED_TYPES = {"ambiguity", "freeze-request", "amendment-proposal"}
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


def slugify(text: str, max_len: int = 48) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[`*_]", "", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    text = re.sub(r"-+", "-", text)
    if len(text) > max_len:
        cut = text[:max_len]
        text = cut.rpartition("-")[0] if "-" in cut else cut
    return text


# ---------------------------------------------------------------- tracker ----

ISSUE_H1_RE = re.compile(r"^#\s+#(\d{4})\s+—\s+(.+)$")
ISSUE_META_RE = re.compile(r"^type:\s*(\S+)\s+status:\s*(\S+)")
ISSUE_REFS_RE = re.compile(r"^refs:\s*(.*?)\s+opened:\s*(.+?)\s+closed-by:\s*(.+)$")
ISSUE_DEPS_RE = re.compile(r"^deps:\s*(.+)$")
REF_TOKEN_RE = re.compile(r"\[([^\]]+)\]")
GATE_TOKEN_RE = re.compile(r"^[ma]\d+$")


def parse_issue(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    issue = {"file": path.name, "body": text}
    for line in lines[:6]:
        m = ISSUE_H1_RE.match(line)
        if m:
            issue["number"], issue["label"] = m.group(1), m.group(2).strip()
        m = ISSUE_META_RE.match(line)
        if m:
            issue["type"], issue["status"] = m.group(1), m.group(2)
        m = ISSUE_DEPS_RE.match(line)
        if m:
            issue["deps_line"] = m.group(1).strip()
        m = ISSUE_REFS_RE.match(line)
        if m:
            tokens = []
            for grp in REF_TOKEN_RE.findall(m.group(1)):
                tokens.extend(t.strip() for t in grp.split(",") if t.strip())
            issue["refs"] = tokens
            issue["opened"] = m.group(2).strip()
            issue["closed_by"] = m.group(3).strip()
    required = {"number", "label", "type", "status"}
    missing = required - issue.keys()
    if missing:
        return None, f"{path.name}: unparsable header (missing {sorted(missing)})"
    issue.setdefault("refs", [])
    issue.setdefault("closed_by", "")
    slug = re.sub(r"^\d{4}-", "", path.stem)
    if issue["type"] == "ambiguity":
        slug = re.sub(r"^ambiguity-", "", slug)
    issue["slug"] = slug
    return issue, None


# ------------------------------------------------------------------- plan ----

CONSTRAINT_RE = re.compile(r"^(\d{1,3})\.\s+(.*)$")
BOLD_NAME_RE = re.compile(r"^\*\*(.+?)\*\*\s*(.*)$")
GROUP_RE = re.compile(r"^###\s+(C-[A-Z]+)")


def parse_constraints(plan_path: Path, overrides: dict):
    """Numbered items inside plan section 2. Returns {number: (slug, label, group)}."""
    lines = plan_path.read_text(encoding="utf-8").splitlines()
    in_s2 = False
    group = None
    out = {}
    for line in lines:
        if line.startswith("## 2."):
            in_s2 = True
            continue
        if in_s2 and re.match(r"^## \d", line):
            break
        if not in_s2:
            continue
        g = GROUP_RE.match(line)
        if g:
            group = g.group(1)
            continue
        m = CONSTRAINT_RE.match(line)
        if not m:
            continue
        num, text = m.group(1), m.group(2).strip()
        b = BOLD_NAME_RE.match(text)
        if b:
            name = b.group(1).rstrip(".")
            label = name
        else:
            name = " ".join(text.split()[:6])
            label = re.sub(r"[`*]", "", text)[:117] + ("…" if len(text) > 117 else "")
        slug = overrides.get(num) or slugify(name)
        out[num] = (slug, label[:120], group)
    return out


# ------------------------------------------------------------------ seams ----

SEAM_ROW_RE = re.compile(r"^\s*\|\s*(S\d)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$")


def parse_seams(kickoff_path: Path):
    """Rows of the doctrine-8 seam table. Returns {S#: (name, impls, freeze_event)}."""
    out = {}
    for line in kickoff_path.read_text(encoding="utf-8").splitlines():
        m = SEAM_ROW_RE.match(line)
        if m and m.group(1) not in out:
            out[m.group(1)] = (
                re.sub(r"[`]", "", m.group(2)),
                m.group(3),
                m.group(4),
            )
    return out


# -------------------------------------------------------------- proposals ----

PROPOSAL_SECTION_RE = re.compile(r"^##\s+(constraints|seams|issues)$")
PROPOSAL_BULLET_RE = re.compile(r"^\s*-\s+(.+)$")
PROPOSAL_ISSUE_H1_RE = re.compile(r"^#(\d{4})\s+—\s+(.+)$")


def parse_proposals(path: Path, warnings: list) -> dict:
    """Parse the curated proposals file (adapter key "proposals").

    PROPOSED CONTENT is on the table but NOT part of the graph: it never
    enters state.json or the REV — the digest's "proposed" annex is the only
    place it renders (SPEC §6). Grammar mirrors the core grammars so promotion
    is a copy into plan.md / seams.md / issues/, not a rewrite:

        ## constraints
        - **name.** claim a test could check.

        ## seams
        - **S3 name.** impls now → later; freeze at M4

        ## issues
        - #1001 — hold: title
          type: ambiguity        status: open
          refs: [2]   opened: seed

    Returns {constraints: [...], seams: [...], issues: [...]} — each a dict
    for the digest annex. Anything unparsable warns (nothing silently dropped).
    """
    out = {"constraints": [], "seams": [], "issues": []}
    text = path.read_text(encoding="utf-8").splitlines()
    section = None
    pending = None  # (lines,) for a multi-line issue entry
    meta_re = re.compile(r"\s*" + ISSUE_META_RE.pattern.lstrip("^"))
    refs_re = re.compile(r"\s*" + ISSUE_REFS_RE.pattern.lstrip("^"))

    def flush_pending():
        nonlocal pending
        if pending:
            lines = pending
            num = label = typ = status = refs = None
            for line in lines:
                m = PROPOSAL_ISSUE_H1_RE.match(line)
                if m:
                    num, label = m.group(1), m.group(2).strip()
                m = meta_re.match(line)
                if m:
                    typ, status = m.group(1), m.group(2)
                m = refs_re.match(line)
                if m:
                    refs = m.group(1).strip()
                elif refs is None:
                    m2 = re.match(r"^\s*refs:\s*(.+?)\s+opened:", line)
                    if m2:
                        refs = m2.group(1).strip()
            if not num or not label:
                warnings.append(f"{path.name}: unparsable proposed issue (no "
                                f"'#NNNN — title'): {lines[0][:60]!r}")
            else:
                out["issues"].append({"number": num, "label": label, "type": typ,
                                      "status": status, "refs": refs or ""})
            pending = None

    for line in text:
        sm = PROPOSAL_SECTION_RE.match(line)
        if sm:
            flush_pending()
            section = sm.group(1)
            continue
        bm = PROPOSAL_BULLET_RE.match(line)
        if bm:
            flush_pending()
            if section == "constraints":
                m = BOLD_NAME_RE.match(bm.group(1))
                if m:
                    out["constraints"].append(
                        {"name": m.group(1).rstrip("."), "text": m.group(2).strip()})
                else:
                    warnings.append(f"{path.name}: proposed constraint without "
                                    f"**bold name**: {line.strip()[:60]!r}")
            elif section == "seams":
                m = BOLD_NAME_RE.match(bm.group(1))
                if m:
                    out["seams"].append(
                        {"name": m.group(1).rstrip("."), "text": m.group(2).strip()})
                else:
                    warnings.append(f"{path.name}: proposed seam without "
                                    f"**bold name**: {line.strip()[:60]!r}")
            elif section == "issues":
                pending = [bm.group(1)]
            else:
                warnings.append(f"{path.name}: proposal outside a section "
                                f"(## constraints|seams|issues): {line.strip()[:60]!r}")
        elif section == "issues" and pending is not None and line.strip():
            pending.append(line)
    flush_pending()
    return out


# ----------------------------------------------------------------- digest ----

STAMP_RE = re.compile(r"@ [0-9a-f]{7,40}(\+dirty)? · REV [0-9a-f]{12}")


def render_digest(doc: dict) -> str:
    """GRAPH.md — a very concise graph digest for an LLM working on the client
    codebase. One line per open item; details live in the issue files. To change
    this file, change the issues and re-run extract."""
    ents = {e["id"]: e for e in doc["entities"]}

    def short(eid):
        e = ents.get(eid)
        if not e:
            return eid
        for b in e["bindings"]:
            if b["source"].startswith("plan"):
                return b["ref"] if b["ref"][:1].isdigit() else None
            if b["source"] == "seam-table" and not b["ref"].startswith("freeze"):
                return b["ref"]
            if b["source"] == "tracker" and e["kind"] in ("workorder", "hold"):
                return b["ref"]
        return eid.split(":", 1)[1]

    def tracker_no(e):
        for b in e["bindings"]:
            if b["source"] == "tracker":
                return b["ref"]
        return "?"

    gf = doc["generated_from"]
    lines = [
        f"# GRAPH — {gf['repo']} @ {gf['commit'][:7]}"
        f"{'+dirty' if gf.get('dirty') else ''} · REV {doc['hash'][:12]}",
        "# generated by gantry extract — do NOT hand-edit; to change it, change the",
        "# issues and re-run extract. Detail lives in the issue files; this is the map.",
        "",
    ]
    gates = [e for e in doc["entities"] if e["kind"] == "gate"]
    latched = [e["id"].split(":")[1] for e in gates if e["status"].get("gate") == "latched"]
    gopen = [e["id"].split(":")[1] for e in gates if e["status"].get("gate") != "latched"]
    phases = [e["id"].split(":")[1] for e in doc["entities"] if e["kind"] == "phase"]
    lines.append(f"gates latched: {' '.join(sorted(latched))} · open: {' '.join(sorted(gopen))}"
                 f" · phases open: {' '.join(sorted(phases))}")
    for stab in ("provisional", "frozen"):
        ss = sorted(short(e["id"]) for e in doc["entities"]
                    if e["kind"] == "seam" and e["status"].get("stability") == stab)
        if ss:
            lines.append(f"seams {stab}: {' '.join(ss)}")
    lines.append("")
    lines.append("open items (kind · refs → upstream anchors):")
    open_items = [e for e in doc["entities"] if e["kind"] in ("workorder", "hold")
                  and (e["status"].get("work") == "open" or e["status"].get("decision") == "open")]
    for e in sorted(open_items, key=tracker_no):
        refs = [short(r["target"]) for r in e["relations"] if r["type"] == "refs"]
        refs = [r for r in refs if r]
        gatedmark = " ⛭human" if e["status"].get("closure_authority") == "human" else ""
        lines.append(f"  {tracker_no(e)} {e['kind']:9s} {e['id'].split(':', 1)[1]}"
                     f"{gatedmark} → {','.join(refs) if refs else '(floating)'}")
    deps = []
    for e in doc["entities"]:
        for r in e["relations"]:
            if r["type"] in DEP_TYPES:
                deps.append(f"  {short(e['id'])} —{r['type']}→ {short(r['target'])}"
                            f" [{r.get('provenance', '?')}]")
    if deps:
        lines.append("")
        lines.append("dependency edges (blocks = must resolve first):")
        lines.extend(sorted(deps))
    closed = sorted(tracker_no(e) for e in doc["entities"] if e["kind"] in ("workorder", "hold")
                    and (e["status"].get("work") == "closed" or e["status"].get("decision") == "resolved"))
    lines.append("")
    lines.append(f"closed/resolved: {' '.join(closed) if closed else 'none'}")
    return "\n".join(lines) + "\n"


def render_proposals_annex(proposals: dict) -> str:
    """The proposed-content annex — on the table, NOT part of the graph. Never
    in state.json, never in the REV; the digest shows it so an agent can see
    what a human is weighing. Promotion = copy into the core truth (plan.md /
    seams.md / issues/), where it becomes graph state and renders in the core
    sections."""
    if not any(proposals.values()):
        return ""
    lines = [
        "## proposed — tentative, on the table, NOT part of the graph",
        "# When accepted: copy into plan.md / seams.md / issues/ and re-run extract.",
        "",
    ]
    if proposals.get("constraints"):
        lines.append("proposed constraints (no number yet — assigned at promotion):")
        for c in proposals["constraints"]:
            lines.append(f"  - {c['name']}: {c['text']}")
        lines.append("")
    if proposals.get("seams"):
        lines.append("proposed seams:")
        for s in proposals["seams"]:
            lines.append(f"  - {s['name']}: {s['text']}")
        lines.append("")
    if proposals.get("issues"):
        lines.append("proposed issues (not real tracker items until filed):")
        for i in proposals["issues"]:
            gated = " ⛭human" if (i.get("type") or "") in HUMAN_GATED_TYPES else ""
            lines.append(f"  - #{i['number']} {i['label']}{gated}"
                         f" ({i.get('type') or '?'} · refs {i.get('refs') or '—'})")
        lines.append("")
    return "\n".join(lines) + "\n"


def write_digest(doc: dict, path: Path):
    path.write_text(render_digest(doc), encoding="utf-8")


# ------------------------------------------------------------------- main ----

def canonical_hash(doc: dict) -> str:
    body = {k: v for k, v in doc.items() if k != "hash"}
    canon = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    canon = unicodedata.normalize("NFC", canon)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True, help="adapter json")
    ap.add_argument("--root", required=True, help="client repo root")
    ap.add_argument("--out", required=True, help="state.json path")
    ap.add_argument("--deps", help="reviewed dependency edges json (proposed/confirmed) to merge")
    ap.add_argument("--digest", help="GRAPH.md digest path (default: alongside --out)")
    ap.add_argument("--check", action="store_true",
                    help="build into memory and compare the fresh GRAPH.md against the "
                         "committed one; write nothing, exit 1 on drift (CI gate). The "
                         "header commit stamp (@ <sha>[+dirty] · REV) is normalized, so "
                         "hook-refreshed digests pass.")
    args = ap.parse_args()

    adapter = json.loads(Path(args.client).read_text(encoding="utf-8"))
    root = Path(args.root)
    warnings, entities = [], {}

    def add(ent):
        if not ID_RE.match(ent["id"]):
            warnings.append(f"BAD ID dropped: {ent['id']}")
            return
        if ent["id"] in entities:
            warnings.append(f"DUPLICATE ID dropped: {ent['id']}")
            return
        ent.setdefault("relations", [])
        ent.setdefault("aliases", [])
        ent.setdefault("supersedes", [])
        entities[ent["id"]] = ent

    # constraints
    constraints = parse_constraints(root / adapter["plan"], adapter.get("constraint_slug_overrides", {}))
    plan_source = adapter["plan_source"]
    num_to_cid = {}
    for num, (slug, label, group) in constraints.items():
        cid = f"constraint:{slug}"
        num_to_cid[num] = cid
        bindings = [{"source": plan_source, "ref": num}]
        if group:
            bindings.append({"source": plan_source, "ref": group})
        add({"id": cid, "kind": "constraint", "label": label,
             "status": {"closure_authority": "human"}, "bindings": bindings})

    # seams (stability resolved after issues)
    seams = parse_seams(root / adapter["kickoff"])
    seam_ids = {}
    for snum, (name, impls, freeze_event) in seams.items():
        slug = adapter["seam_slugs"].get(snum)
        if not slug:
            warnings.append(f"seam {snum} has no slug in adapter; skipped")
            continue
        sid = f"seam:{slug}"
        seam_ids[snum] = sid
        add({"id": sid, "kind": "seam", "label": f"{name} ({impls})"[:120],
             "status": {"stability": "provisional"},
             "bindings": [{"source": "seam-table", "ref": snum},
                          {"source": "seam-table", "ref": f"freeze: {freeze_event}"}]})

    # parts (adapter-declared; pointers only, no status claims)
    for part in adapter.get("parts", []):
        add({"id": part["id"], "kind": "part", "label": part["label"][:120],
             "status": {}, "bindings": part.get("bindings", [])})

    def resolve_ref(tok):
        tok = tok.strip()
        if tok.isdigit():
            cid = num_to_cid.get(tok)
            if not cid:
                warnings.append(f"ref [{tok}]: constraint not found in plan parse")
            return cid
        if re.match(r"^S\d$", tok):
            return seam_ids.get(tok)
        if GATE_TOKEN_RE.match(tok.lower()):
            return f"gate:{tok.lower()}"
        pm = re.match(r"^[Pp]hase([A-Za-z0-9]+)$", tok)
        if pm:
            return f"phase:{pm.group(1).lower()}"
        if re.match(r"^Q\d+$", tok):
            slug = adapter.get("q_holds", {}).get(tok)
            if slug:
                return f"hold:{slug}"
            warnings.append(f"ref [{tok}]: open question with no hold issue; skipped")
            return None
        warnings.append(f"ref [{tok}]: unrecognized token; skipped")
        return None

    # tracker
    tracker = root / adapter["tracker_dir"]
    issue_min = adapter.get("issue_min", 0) or 0
    issues = []
    for path in sorted(tracker.glob("[0-9][0-9][0-9][0-9]-*.md")):
        issue, err = parse_issue(path)
        if err:
            warnings.append(err)
            continue
        if issue_min and int(issue["number"]) < issue_min:
            warnings.append(f"#{issue['number']}: below issue_min {issue_min:04d} — "
                            f"this repo's issues are numbered from {issue_min:04d} "
                            f"(copied-in history is fine; new issues must stay at or above it)")
        issues.append(issue)

    frozen_seams = set()
    issue_selfids = []
    # entity id -> issue source text, for the viewer's reader pane. Deliberately
    # a SIDECAR: issue prose is not graph state, so editing it must not move the
    # REV. Never fed into canonical_hash().
    bodies = {}

    def bind_body(eid, issue):
        bodies.setdefault(eid, {"file": f"{adapter['tracker_dir']}/{issue['file']}",
                                "number": issue["number"], "title": issue["label"],
                                "type": issue["type"], "text": issue["body"]})

    for issue in issues:
        human = issue["type"] in HUMAN_GATED_TYPES
        closed = issue["status"] == "closed"
        if closed and human and SHA_RE.match(issue["closed_by"]):
            warnings.append(f"#{issue['number']}: human-gated type closed by bare sha "
                            f"({issue['closed_by']}) — rendered OPEN (invariant 2)")
            closed = False

        kind = "hold" if issue["type"] == "ambiguity" else "workorder"
        self_id = f"{kind}:{issue['slug']}"
        status = {"closure_authority": "human" if human else "mechanical"}
        if kind == "hold":
            status["decision"] = "resolved" if closed else "open"
        else:
            status["work"] = "closed" if closed else "open"

        bindings = [{"source": "tracker", "ref": f"#{issue['number']}"}]
        if closed and SHA_RE.match(issue["closed_by"]):
            bindings.append({"source": "git", "ref": issue["closed_by"]})
        bind_body(self_id, issue)

        relations = []
        for tok in issue["refs"]:
            target = resolve_ref(tok)
            if target and target != self_id:
                relations.append({"type": "refs", "target": target, "provenance": "parsed"})

        # milestone issues also yield their gate / phase entity
        first = issue["slug"].split("-")[0]
        if issue["type"] == "milestone" and GATE_TOKEN_RE.match(first):
            gid = f"gate:{first}"
            gstatus = {"gate": "latched" if closed else "open",
                       "closure_authority": "mechanical"}
            gbind = [{"source": "tracker", "ref": f"#{issue['number']}"}]
            if closed and SHA_RE.match(issue["closed_by"]):
                gbind.append({"source": "git", "ref": issue["closed_by"]})
            glabel = re.sub(r"^[MA]\d+:\s*", "", issue["label"])
            if gid not in entities:
                add({"id": gid, "kind": "gate", "label": f"{first.upper()} — {glabel}"[:120],
                     "status": gstatus, "bindings": gbind})
            bind_body(gid, issue)
            if not any(r["target"] == gid for r in relations):
                relations.append({"type": "refs", "target": gid, "provenance": "parsed"})
        elif issue["type"] == "milestone" and first.startswith("phase"):
            pid = f"phase:{first.removeprefix('phase')}"
            if ID_RE.match(pid) and pid not in entities:
                add({"id": pid, "kind": "phase", "label": issue["label"][:120],
                     "status": {"gate": "latched" if closed else "open"},
                     "bindings": [{"source": "tracker", "ref": f"#{issue['number']}"}]})
            if ID_RE.match(pid):
                bind_body(pid, issue)
            if ID_RE.match(pid) and not any(r["target"] == pid for r in relations):
                relations.append({"type": "refs", "target": pid, "provenance": "parsed"})

        if issue["type"] == "freeze-request" and closed:
            for tok in issue["refs"]:
                if re.match(r"^S\d$", tok):
                    frozen_seams.add(tok)

        if not relations:
            warnings.append(f"#{issue['number']}: no resolvable refs — floating scaffold (invariant 1)")

        add({"id": self_id, "kind": kind, "label": issue["label"][:120],
             "status": status, "bindings": bindings, "relations": relations})
        issue_selfids.append((issue, self_id))

    for snum in frozen_seams:
        if snum in seam_ids:
            entities[seam_ids[snum]]["status"]["stability"] = "frozen"

    # stratum 2: issue-body #NNNN cross-links -> `mentions` edges (deterministic)
    num_to_eid = {issue["number"]: sid for issue, sid in issue_selfids}
    for issue, sid in issue_selfids:
        have = {(r["type"], r["target"]) for r in entities[sid]["relations"]}
        for num in sorted(set(re.findall(r"#(\d{4})", issue["body"]))):
            if num == issue["number"]:
                continue
            target = num_to_eid.get(num)
            if not target:
                warnings.append(f"#{issue['number']}: body mentions #{num} — no such issue")
                continue
            if ("mentions", target) in have or ("refs", target) in have:
                continue
            entities[sid]["relations"].append(
                {"type": "mentions", "target": target, "provenance": "parsed"})
            have.add(("mentions", target))

    # author-declared deps: lines (contract section 5) -> parsed dependency edges
    for issue, sid in issue_selfids:
        line = issue.get("deps_line")
        if not line:
            continue
        have = {(r["type"], r["target"]) for r in entities[sid]["relations"]}
        for clause in (c.strip() for c in line.split(";") if c.strip()):
            parts = clause.split()
            typ, targets = parts[0], [t.strip(",") for t in parts[1:]]
            if typ not in DEP_TYPES:
                warnings.append(f"#{issue['number']}: deps clause '{clause}': unknown type")
                continue
            if not targets:
                warnings.append(f"#{issue['number']}: deps clause '{clause}': no targets")
            for tok in targets:
                if tok.startswith("#"):
                    target = num_to_eid.get(tok.lstrip("#"))
                    if not target:
                        warnings.append(f"#{issue['number']}: deps target {tok}: no such issue")
                        continue
                else:
                    target = resolve_ref(tok)
                    if not target:
                        continue
                if target == sid or (typ, target) in have:
                    continue
                entities[sid]["relations"].append(
                    {"type": typ, "target": target, "provenance": "parsed"})
                have.add((typ, target))

    # merge reviewed dependency edges (proposed/confirmed; never invented here)
    if args.deps:
        for i, dep in enumerate(json.loads(Path(args.deps).read_text(encoding="utf-8"))):
            src, typ, target = dep.get("from"), dep.get("type"), dep.get("target")
            if typ not in DEP_TYPES:
                warnings.append(f"deps[{i}]: type '{typ}' not a dependency type; skipped")
                continue
            if src not in entities or target not in entities:
                warnings.append(f"deps[{i}]: {src} -> {target}: unknown entity; skipped")
                continue
            if dep.get("provenance") not in ("proposed", "confirmed"):
                warnings.append(f"deps[{i}]: provenance must be proposed|confirmed; skipped")
                continue
            rel = {"type": typ, "target": target, "provenance": dep["provenance"]}
            if dep.get("evidence"):
                rel["evidence"] = dep["evidence"][:300]
            existing = {(r["type"], r["target"]) for r in entities[src]["relations"]}
            if (typ, target) not in existing:
                entities[src]["relations"].append(rel)

    # relation target check (invariant: no dangling edges without a warning)
    for ent in entities.values():
        for rel in ent["relations"]:
            if rel["target"] not in entities:
                warnings.append(f"{ent['id']}: relation -> missing entity {rel['target']}")

    commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    # dirty = uncommitted changes (staged, unstaged, or untracked) under the
    # extract INPUT paths only — other noise in the client tree doesn't count.
    input_paths = [adapter["tracker_dir"], adapter["plan"], adapter["kickoff"]]
    proposals = {}
    if adapter.get("proposals"):
        prop_path = root / adapter["proposals"]
        if prop_path.exists():
            proposals = parse_proposals(prop_path, warnings)
            if not Path(adapter["proposals"]).is_absolute():
                input_paths.append(adapter["proposals"])
        else:
            warnings.append(f"proposals: {prop_path} declared in adapter but missing — skipped")
    porcelain = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--"] + input_paths,
        capture_output=True, text=True, check=True).stdout.strip()
    dirty = bool(porcelain)

    doc = {
        "schema_version": SCHEMA_VERSION,
        "generated_from": {"repo": adapter["client"], "commit": commit,
                           "dirty": dirty,
                           "extractor_version": EXTRACTOR_VERSION},
        "entities": sorted(entities.values(), key=lambda e: e["id"]),
        "hash": "",
    }
    doc["hash"] = canonical_hash(doc)

    out_path = Path(args.out)
    digest_path = Path(args.digest) if args.digest else out_path.parent / "GRAPH.md"
    digest_text = render_digest(doc) + render_proposals_annex(proposals)

    if args.check:
        if warnings:
            print(f"\nwarnings ({len(warnings)}):", file=sys.stderr)
            for w in warnings:
                print(f"  - {w}", file=sys.stderr)
        if not digest_path.exists():
            print(f"GRAPH.md missing: {digest_path} — run extract first", file=sys.stderr)
            return 1
        norm = lambda s: STAMP_RE.sub("@ <stamp>", s, count=1)
        if norm(digest_text) != norm(digest_path.read_text(encoding="utf-8")):
            print(f"GRAPH.md is stale — re-run extract "
                  f"(fresh REV {doc['hash'][:12]} vs {digest_path})", file=sys.stderr)
            return 1
        print(f"GRAPH.md up to date — REV {doc['hash'][:12]}")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    digest_path.write_text(digest_text, encoding="utf-8")

    # sidecar: issue source text for the viewer's reader pane (not graph state,
    # not hashed — see bind_body). Only ids that exist in the graph.
    bodies_path = out_path.parent / "bodies.json"
    bodies_out = {"schema_version": SCHEMA_VERSION, "state_hash": doc["hash"],
                  "bodies": {k: v for k, v in sorted(bodies.items()) if k in entities}}
    bodies_path.write_text(json.dumps(bodies_out, indent=2, sort_keys=True,
                                      ensure_ascii=False) + "\n", encoding="utf-8")

    kinds = {}
    for e in entities.values():
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    print(f"state.json written: {out_path}")
    print(f"bodies.json written: {bodies_path}  ({len(bodies_out['bodies'])} readable entities)")
    print(f"REV {doc['hash'][:12]}  @ client {commit[:7]}{'+dirty' if dirty else ''}")
    print(f"entities: {sum(kinds.values())}  " +
          "  ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    print(f"constraints parsed from plan: {len(constraints)}")
    if warnings:
        print(f"\nwarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    raise SystemExit(main())
