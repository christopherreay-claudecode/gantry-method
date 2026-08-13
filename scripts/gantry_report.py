#!/usr/bin/env python3
"""gantry_report — emit a Typst state-report fragment from a client's graph.

Reads a gantry client's adapter + derived state.json and emits a Typst
fragment (a "current gantry state" section) for inclusion in a corporate
report. Deterministic: same client commit + same adapter -> byte-identical
output. Stdlib only, no network.

The fragment is DERIVED DATA (SPEC §6 doctrine): it restates graph entities
with their constraint numbers and the graph REV; it is never a source of
truth. Regenerate it; do not hand-edit it. If the underlying truth moves,
the report must be re-generated from the same commit.

Usage:
  python3 scripts/gantry_report.py \
      --client <client>/.gantry/adapter.json --root <client> \
      --out <client>/tools/typst/sample-report/state.typ \
      [--title "Patent programme — status"] [--author "CCS"] [--date "2026-08-13"]
"""
import argparse
import json
import sys
from pathlib import Path

TYPES = ("blocks", "defers-to", "informs", "awaits-stamp")


def esc(s: str) -> str:
    for a, b in (("\\", "\\\\"), ("#", "\\#"), ("$", "\\$"), ('"', '\\"'), ("\n", " ")):
        s = s.replace(a, b)
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True, help="adapter JSON path")
    ap.add_argument("--root", required=True, help="client repo root")
    ap.add_argument("--out", required=True, help="output .typ fragment path")
    ap.add_argument("--title", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--date", default="")
    args = ap.parse_args()

    root = Path(args.root)
    try:
        adapter = json.loads(Path(args.client).read_text(encoding="utf-8"))
    except OSError as e:
        sys.exit(f"gantry_report: cannot read adapter {args.client}: {e}")

    state_path = root / ".gantry" / "out" / "state.json"
    if not state_path.exists():
        sys.exit(
            f"gantry_report: no derived state at {state_path}\n"
            "run the extractor first, e.g.:\n"
            f"  python3 tools/gantry_extract.py --client {args.client} "
            f"--root {root} --out {state_path} --digest {root / 'GRAPH.md'}"
        )
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except OSError as e:
        sys.exit(f"gantry_report: cannot read {state_path}: {e}")

    gen = state.get("generated_from", {})
    rev = state.get("hash", "")[:12]
    commit = gen.get("commit", "")[:8]
    extractor = gen.get("extractor_version", "?")
    dirty = gen.get("dirty", False)
    plan = adapter.get("plan_source", "?")
    client = adapter.get("client", "?")

    seam_slug_to_s = {v: k for k, v in adapter.get("seam_slugs", {}).items()}

    def short(eid: str) -> str:
        kind, _, slug = eid.partition(":")
        if kind == "constraint":
            for b in by_id[eid].get("bindings", []):
                if b["source"] == plan and b["ref"].isdigit():
                    return b["ref"]
            return slug
        if kind == "seam":
            return seam_slug_to_s.get(slug, slug)
        if kind in ("gate", "phase", "hold"):
            return slug
        if kind == "workorder":
            for b in by_id[eid].get("bindings", []):
                if b["source"] == "tracker":
                    return b["ref"]
            return slug
        return eid

    by_id = {e["id"]: e for e in state["entities"]}

    constraints = []
    gates = []
    holds = []
    seams = []
    phases = []
    workorders = []
    edges = []

    for e in state["entities"]:
        bindings = {b["source"]: b["ref"] for b in e.get("bindings", [])}
        kind = e["kind"]
        if kind == "constraint":
            num = ""
            group = ""
            for b in e.get("bindings", []):
                if b["source"] == plan:
                    if b["ref"].isdigit():
                        num = b["ref"]
                    elif b["ref"].startswith("C-"):
                        group = b["ref"]
            if num.isdigit():
                constraints.append((int(num), group, e["label"]))
        elif kind == "gate":
            gates.append((e["id"], e["label"], e["status"].get("gate", "?")))
        elif kind == "hold":
            holds.append((e["id"], e["label"], e["status"].get("decision", "?")))
        elif kind == "seam":
            freeze = next(
                (b["ref"].removeprefix("freeze: ") for b in e.get("bindings", [])
                 if b["source"] == "seam-table" and b["ref"].startswith("freeze: ")),
                "",
            )
            seams.append((e["id"], e["label"], e["status"].get("stability", "?"), freeze))
        elif kind == "phase":
            phases.append((e["id"], e["label"], e["status"].get("gate", "?")))
        elif kind == "workorder":
            workorders.append((e["id"], e["label"], e["status"].get("work", "?")))
        for r in e.get("relations", []):
            if r["type"] in TYPES:
                edges.append((e["id"], r["type"], r["target"], r.get("provenance", "?")))

    constraints.sort()
    gates.sort(key=lambda t: t[0])
    holds.sort(key=lambda t: t[0])
    seams.sort(key=lambda t: seam_slug_to_s.get(t[0].partition(":")[2], t[0]))
    phases.sort(key=lambda t: t[0])
    workorders.sort(key=lambda t: t[0])
    edges = sorted(set(edges))

    def table(headers, rows):
        out = ["#table("]
        out.append("  columns: (" + ", ".join(["auto"] * (len(headers) - 1) + ["1fr"]) + "),")
        for h in headers:
            out.append(f"  [*{esc(h)}*],")
        for r in rows:
            cells = list(r)
            cells[-1] = esc(cells[-1])
            for c in cells[:-1]:
                out.append(f"  [{esc(str(c))}],")
            out.append(f"  [{cells[-1]}],")
        out.append(")")
        return "\n".join(out)

    lines = []
    lines.append("// ============================================================")
    lines.append("// gantry state report — GENERATED DERIVED DATA. Do not hand-edit.")
    lines.append("// Regenerate:")
    lines.append(f"//   python3 tools/gantry_report.py --client <adapter> --root <repo> \\")
    lines.append(f"//       --out <this file>")
    lines.append(f"// state source: {esc(client)} @ {commit} (dirty: {str(dirty).lower()})")
    lines.append(f"//               extractor {extractor} · plan {esc(plan)} · REV {rev}")
    lines.append("// ============================================================")
    lines.append("")
    lines.append("== Current gantry state")
    lines.append("")
    lines.append(
        f"plan {esc(plan)} · REV {rev} · commit {commit} · generated by "
        "gantry_report.py · derived from state.json, never hand-edited"
    )
    lines.append("")

    lines.append("=== Constraints (the plan, amendment-only)")
    lines.append("")
    lines.append(table(["No", "Group", "Constraint"],
                       [(n, g, l) for n, g, l in constraints]))
    lines.append("")

    lines.append("=== Gates and phases")
    lines.append("")
    lines.append(table(["Gate", "Status"], [(short(i), s) for i, _, s in gates]))
    lines.append("")
    if phases:
        lines.append(table(["Phase", "Status"], [(short(i), s) for i, _, s in phases]))
        lines.append("")

    lines.append("=== Holds (open questions — human sign-off only)")
    lines.append("")
    lines.append(table(["Hold", "Decision"], [(short(i), s) for i, _, s in holds]))
    lines.append("")

    lines.append("=== Seams (substitution points)")
    lines.append("")
    lines.append(table(["Seam", "Stability", "Freeze event"],
                       [(short(i), s, f) for i, _, s, f in seams]))
    lines.append("")

    open_wo = [(i, l) for i, l, s in workorders if s == "open"]
    if open_wo:
        lines.append("=== Open workorders")
        lines.append("")
        rows = []
        for i, l in open_wo:
            refs = [short(r["target"]) for r in by_id[i].get("relations", [])
                    if r["type"] == "refs"]
            rows.append((short(i), l, ", ".join(refs)))
        lines.append(table(["Item", "Workorder", "Refs"], rows))
        lines.append("")

    if edges:
        lines.append("=== Dependency edges")
        lines.append("")
        for a, t, b, p in edges:
            lines.append(f"- {esc(short(a))} —{esc(t)}→ {esc(short(b))} [{esc(p)}]")
        lines.append("")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"gantry_report: wrote {out_path}")
    print(f"  plan {plan} · REV {rev} · {len(constraints)} constraints, "
          f"{len(gates)} gates, {len(holds)} holds, {len(seams)} seams, "
          f"{len(workorders)} workorders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
