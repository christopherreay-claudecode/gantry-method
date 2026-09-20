#!/usr/bin/env python3
"""mmt — render a MindMapTreeFormat-0.1 tree as a local, linked web page.

Every @address becomes an anchor, every ->@address a link to it, and every
external token — #NNNN, R7, U3, c17, [3], S1, m2, Q1, U4/W2/H3, §6.1, a
path[:line], a commit hash — becomes a link into a line-numbered rendering of
the document that defines it, resolved across one or more repositories
("roots"). Level-1 conformance (spec §9) is linted at the same time.

stdlib only · deterministic · writes a file:// site for one reader. Never
published anywhere (see designDocs/MindMapTreeFormat-0.1.md §12 and the
no-artifacts rule).

    mmt.py TREE.mmt                       # roots: cwd
    mmt.py TREE.mmt --root core=../cubeOnSKOS --root ui=../cubeOnSKOS-ui
    mmt.py - < answer.txt --out .site/mmt --open
    mmt.py TREE.md                        # first ```mmt fenced block in a .md
    mmt.py TREE.mmt --strict              # exit 1 on any L1 lint finding

Tokens may carry a root prefix — core:#1013, ui:#0011, gantry:scripts/mmt.py —
otherwise the first root that defines the token wins (roots in the order given).

Six token kinds are generic to every gantry repo and built in: #NNNN issues, c17/[17]
constraints, S1 seams, m2/g1/Q1 gates+holds, path[:line], commit sha. Everything else a
repo wants linkable — rule lines in CLAUDE.md, contract headings, plan sections — is that
repo's own vocabulary, declared in its .gantry/adapter.json and read per root (#0020):

    "mmt_tokens": [ {"kind": "rule", "glob": "CLAUDE.md",
                     "line": "^([A-Z]\\d{1,2})\\s{2,}(.+)$", "token": "{1}", "label": "{2}",
                     "match": "[A-Z]\\d{1,2}"} ],      # match: the shape, so unknown ones are reported unresolved
    "mmt_edges":  ["depends", "serves", "proves", "blocks", "contradicts", "same-as", "owner", "evidence"],
    "mmt_links":  {"patent": "https://patents.google.com/patent/{id}"}   # namespaces → URL templates (#0029)

A tree may also declare its own, in a LINKS: foot of markdown reference definitions:

    LINKS:
      [rfc]: https://www.rfc-editor.org/rfc/rfc{id}      # a namespace: rfc:9110 in the body
      [spec-live]: https://example.org/spec/s8           # an anchor: spec-live in the body

Lookup is most specific first: the tree's LINKS: → the adapter's mmt_links → mmt_roots → generic.
External targets are linked, never fetched or stored.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ------------------------------------------------------------------ symbols --


@dataclass
class Root:
    name: str
    path: Path
    sym: dict[str, dict] = field(default_factory=dict)   # token -> {path,line,label,kind}
    docs: dict[str, str] = field(default_factory=dict)   # rel path -> html file name
    commits: dict[str, str] = field(default_factory=dict)  # short sha -> full sha
    adapter: dict = field(default_factory=dict)             # .gantry/adapter.json, if any
    shapes: list[str] = field(default_factory=list)        # "match" regexes of declared token kinds

    def add(self, tok: str, path: str, line: int, label: str, kind: str) -> None:
        self.sym.setdefault(tok, {"path": path, "line": line, "label": label.strip(), "kind": kind})

    def lines(self, rel: str) -> list[str]:
        return (self.path / rel).read_text(encoding="utf-8", errors="replace").splitlines()

    def has(self, rel: str) -> bool:
        return (self.path / rel).is_file()


def collect(root: Root) -> None:
    R = root
    ad = R.path / ".gantry/adapter.json"
    if ad.exists():
        try:
            R.adapter = json.load(open(ad))
        except Exception:
            R.adapter = {}
    if R.has("plan.md"):                                     # c17 / [17] constraints
        for i, ln in enumerate(R.lines("plan.md"), 1):
            m = re.match(r"^(\d{1,2})\.\s+\*\*(.+?)\*\*", ln)
            if m:
                R.add(f"c{m.group(1)}", "plan.md", i, m.group(2), "constraint")
                R.add(f"[{m.group(1)}]", "plan.md", i, m.group(2), "constraint")
    if R.has("seams.md"):                                    # S1 seams
        for i, ln in enumerate(R.lines("seams.md"), 1):
            m = re.match(r"^\|\s*(S\d)\s*\|\s*(.+?)\s*\|", ln)
            if m:
                R.add(m.group(1), "seams.md", i, m.group(2), "seam")
    for p in sorted((R.path / "issues").glob("[0-9][0-9][0-9][0-9]-*.md")):   # #NNNN issues
        rel = str(p.relative_to(R.path))
        title = ""
        for ln in R.lines(rel)[:3]:
            h = re.match(r"^#\s+#\d{4}\s+[—-]+\s+(.+)$", ln)
            if h:
                title = h.group(1)
                break
        R.add("#" + p.name[:4], rel, 1, title or p.stem, "issue")
    st = R.path / ".gantry/out/state.json"                   # m0 g1 gates · Q1 holds
    if st.exists():
        try:
            ents = json.load(open(st))["entities"]
        except Exception:
            ents = []
        for e in ents:
            if e.get("kind") != "gate":
                continue
            tok = e["id"].split(":", 1)[1]
            ref = next((b["ref"] for b in e.get("bindings", []) if b["ref"].startswith("#")), None)
            if ref and ref in R.sym:
                s = R.sym[ref]
                R.add(tok, s["path"], s["line"], e.get("label", tok), "gate")
        ad = R.path / ".gantry/adapter.json"
        if ad.exists():
            for qtok, target in json.load(open(ad)).get("q_holds", {}).items():
                ent = next((e for e in ents if e["id"] == f"hold:{target}"), None)
                ref = ent and next((b["ref"] for b in ent.get("bindings", []) if b["ref"].startswith("#")), None)
                if ref and ref in R.sym:
                    s = R.sym[ref]
                    R.add(qtok, s["path"], s["line"], ent.get("label", qtok), "hold")
    collect_declared(R)


def collect_declared(R: Root) -> None:
    """The repo's own token kinds — `mmt_tokens` in its adapter (#0020). Each entry: kind ·
    glob (relative to the root) · line (regex; group 1 is the token, group 2 the label unless
    `token`/`label` templates say otherwise) · optional `match` (the token shape, so a token of
    this kind that no line defines is still reported as unresolved rather than passed as text)."""
    for spec in R.adapter.get("mmt_tokens", []) or []:
        try:
            line_re = re.compile(spec["line"])
        except (KeyError, re.error) as e:
            print(f"root {R.name}: mmt_tokens entry {spec.get('kind', '?')}: bad 'line' regex ({e})", file=sys.stderr)
            continue
        tok_t, lab_t = spec.get("token", "{1}"), spec.get("label", "{2}")
        if spec.get("match"):
            R.shapes.append(spec["match"])
        for p in sorted(R.path.glob(spec.get("glob", ""))):
            if not p.is_file():
                continue
            rel = str(p.relative_to(R.path))
            for i, ln in enumerate(R.lines(rel), 1):
                m = line_re.match(ln)
                if not m:
                    continue
                g = [m.group(0), *m.groups()]
                fmt = lambda s: re.sub(r"\{(\d+)\}", lambda x: (g[int(x.group(1))] or "") if int(x.group(1)) < len(g) else "", s)
                R.add(fmt(tok_t), rel, i, re.sub(r"\*\*", "", fmt(lab_t)), spec.get("kind", "token"))


def git(root: Root, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(root.path), *args], capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    return r.stdout if r.returncode == 0 else None


# -------------------------------------------------------------------- tree --

TREE_PREFIX = re.compile(r"^[\s│├└─]*")
GLYPHS = "=~?!x"


@dataclass
class Node:
    n: int            # line number in the tree
    depth: int
    addr: str | None
    glyph: str | None
    text: str         # the node's text without prefix/addr/glyph
    raw: str          # the full original line


LINKS_HEAD = re.compile(r"^\s*LINKS:\s*$")
LINK_DEF = re.compile(r"^\s*\[([\w.\-]+)\]:\s*(\S+)\s*$")     # markdown reference definition, verbatim


def parse_links(src: str) -> tuple[dict[str, str], int]:
    """The tree's LINKS: foot (#0029): markdown reference definitions, one per line, after a line
    that is exactly `LINKS:`. -> ({name: url-or-template}, line number of LINKS: or 0).
    A url containing `{id}` declares a namespace (`patent:US1` in the body); one without is a
    one-off anchor referenced by bare name."""
    links, start = {}, 0
    for n, raw in enumerate(src.splitlines(), 1):
        if not start:
            if LINKS_HEAD.match(raw):
                start = n
            continue
        m = LINK_DEF.match(raw)
        if m:
            links[m.group(1)] = m.group(2)
    return links, start


def parse_tree(src: str) -> list[Node]:
    nodes = []
    _, foot = parse_links(src)
    for n, raw in enumerate(src.splitlines(), 1):
        if foot and n >= foot:
            break
        if not raw.strip():
            continue
        pre = TREE_PREFIX.match(raw).group(0)
        depth = (pre.count("├") + pre.count("└") + pre.count("│") + (pre.count("─") == 0 and 0)) if pre.strip() else 0
        if pre.strip() and "─" in pre:
            depth = len(pre.rstrip()) // 3 + 1
        body = raw[len(pre):]
        addr = glyph = None
        m = re.match(r"@([\w.\-]+)\s*", body)
        if m:
            addr, body = m.group(1), body[m.end():]
        m = re.match(r"([=~?!x])(?=\s)", body)
        if m:
            glyph, body = m.group(1), body[m.end():].lstrip()
        nodes.append(Node(n, depth, addr, glyph, body, raw))
    return nodes


def extract_tree(text: str) -> str:
    """A .md may hold the tree in the first ```mmt (or bare ```) fence that contains tree characters."""
    fences = re.findall(r"```(?:mmt|text|)\n(.*?)```", text, re.S)
    for f in fences:
        if re.search(r"[├└]", f) or f.lstrip().startswith("@"):
            return f
    return text


# -------------------------------------------------------------------- lint --


BARE_ISSUE = re.compile(r"#(?:[a-z][a-z0-9]{0,11}-)?\d{4}")   # #0011 · #a1-0003 — the tracker's own forms


def lint(nodes: list[Node], edges: list[str] | None = None, roots: list[str] | None = None) -> tuple[list[str], list[str]]:
    """-> (level-1 findings, notes). Notes: a ->@x [type] outside the subject root's `mmt_edges`
    vocabulary (spec §5, §8) — level-2 territory, reported but never fatal.
    Level 1 includes: every issue token carries a root prefix (core:#1013) — there is no default
    root for an issue number, because every repository has a #0001."""
    out, notes = [], []
    addrs = {n.addr for n in nodes if n.addr}
    hint = " · ".join(f"{r}:#NNNN" for r in (roots or [])) or "<root>:#NNNN"
    for n in nodes:
        bare = [m.group(0) for m in re.finditer(r"(?<![\w:/#§@\-])" + BARE_ISSUE.pattern + r"(?![\w])", n.text)]
        if bare:
            out.append(f"L{n.n}: {' '.join(bare)} — issue number with no root prefix; write {hint}")
    seen: set[str] = set()
    for n in nodes:
        if n.addr:
            if n.addr in seen:
                out.append(f"L{n.n}: @{n.addr} declared twice")
            seen.add(n.addr)
        for ref in re.findall(r"->@([\w.\-]+)", n.text):
            if ref not in addrs and not re.search(rf"->@{re.escape(ref)}\s*\[todo\]", n.text):
                out.append(f"L{n.n}: ->@{ref} has no node (legal; mark [todo] to silence)")
        if n.glyph == "?" and not re.search(r"owner|->@you|->@\w+\s*\[owner\]|—\s*\S", n.text):
            out.append(f"L{n.n}: ? names no owner")
        if n.glyph == "?" and "→" not in n.text and "->" not in n.text:
            out.append(f"L{n.n}: ? names no consequence (branch→what changes)")
        if n.glyph == "!" and not re.search(r"^\s*[\w.\-/ ]+:\s+\S", n.text):
            out.append(f"L{n.n}: ! lacks 'actor: artefact'")
        if n.glyph == "x" and "->@" not in n.text:
            out.append(f"L{n.n}: x names no ->@unblocker")
        if re.match(r"[=~?!x]\s", n.text):
            out.append(f"L{n.n}: stacked glyphs — nest instead")
        if URL_RE.search(n.text) or MD_LINK_RE.search(n.text):
            notes.append(f"L{n.n}: a URL in the reading line — prefer a named link: define it under LINKS: (#0029)")
        if edges:
            for ref, typ in re.findall(r"->@([\w.\-]+)\s*\[([\w\-]+)\]", n.text):
                if typ not in edges and typ != "todo":
                    notes.append(f"L{n.n}: ->@{ref} [{typ}] is not in mmt_edges ({', '.join(edges)})")
    return out, notes


# ------------------------------------------------------------------ linkify --

GENERIC_TOKENS = (
    r"#\d{4}"
    r"|c\d{1,2}(?!\d)|\[\d{1,2}\]"    # constraints
    r"|S\d{1,2}(?!\d)"                 # seams
    r"|[mg]\d(?!\d)|Q\d{1,2}(?!\d)"    # gates · holds
    r"|[0-9a-f]{7,40}"                # commit
)


def token_re(roots: list[Root]) -> re.Pattern:
    """The generic six, plus every declared kind's shape and every declared symbol (longest
    first), so a root's own vocabulary is matched exactly as it declared it."""
    alts = [GENERIC_TOKENS]
    alts += [s for r in roots for s in r.shapes]
    syms = sorted({k for r in roots for k in r.sym if not re.fullmatch(GENERIC_TOKENS, k)}, key=lambda s: (-len(s), s))
    alts += [re.escape(s) for s in syms]
    return re.compile(r"(?<![\w/#§@\-])((?:[a-z][\w\-]*:)?)(" + "|".join(alts) + r")(?![\w])")


PATH_RE = re.compile(
    r"(?<![\w/@\-])((?:[a-z][\w\-]*:)?)((?:[\w.\-]+/)+[\w.\-]+\.[a-z]{1,5}|(?:CLAUDE|GRAPH|README|SPEC|plan|seams)\.md)(?::(\d+))?\b"
)
REF_RE = re.compile(r"->@([\w.\-]+)")
ADDR_RE = re.compile(r"^(\s*)@([\w.\-]+)")


URL_RE = re.compile(r"(?<![\w\"'=(\[])(https?://[^\s<>\"'()\[\]]+[^\s<>\"'()\[\].,;:!?])")
MD_LINK_RE = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")


class Site:
    def __init__(self, roots: list[Root], out: Path, links: dict[str, str] | None = None):
        self.roots, self.out = roots, out
        self.by_name = {r.name: r for r in roots}
        self.todo: list[tuple[Root, str]] = []      # docs to render
        self.unresolved: dict[str, int] = {}
        self.token_re = token_re(roots)
        # link table, most specific first (#0029): the tree's LINKS: foot over the subject
        # root's adapter mmt_links. {id} → a namespace; no {id} → a one-off anchor.
        self.links: dict[str, str] = dict((roots[0].adapter.get("mmt_links") or {}) if roots else {})
        self.links.update(links or {})
        self.namespaces = {k for k, v in self.links.items() if "{id}" in v}
        self.anchors = {k for k, v in self.links.items() if "{id}" not in v}
        alts = []
        if self.namespaces:
            alts.append("(?:" + "|".join(re.escape(k) for k in sorted(self.namespaces, key=len, reverse=True)) + r"):([^\s<>\"'()\[\],;·]+)")
        if self.anchors:
            alts.append("(" + "|".join(re.escape(k) for k in sorted(self.anchors, key=len, reverse=True)) + r")(?![\w\-])")
        self.link_re = re.compile(r"(?<![\w/#§@\-:\[])(" + "|".join(alts) + ")") if alts else None

    def external(self, m: re.Match) -> tuple[str, str] | None:
        """-> (href, label) for a namespace token or an anchor name matched by link_re."""
        whole = m.group(1)
        ns, _, ident = whole.partition(":")
        if ns in self.namespaces and ident:
            return self.links[ns].replace("{id}", ident), f"{ns}: {ident}"
        if whole in self.anchors:
            return self.links[whole], whole
        return None

    def slug(self, root: Root, rel: str) -> str:
        return root.name + "__" + re.sub(r"[^\w.]+", "__", rel) + ".html"

    grow = True   # False while rendering doc pages: link only to already-wanted docs

    def want(self, root: Root, rel: str) -> str | None:
        if rel not in root.docs:
            if not self.grow:
                return None
            root.docs[rel] = self.slug(root, rel)
            self.todo.append((root, rel))
        return root.docs[rel]

    def cands(self, prefix: str) -> list[Root]:
        if prefix:
            r = self.by_name.get(prefix[:-1])
            return [r] if r else []
        return self.roots

    def resolve_tok(self, prefix: str, tok: str) -> tuple[str, str, str] | None:
        """-> (href, kind, title)"""
        for r in self.cands(prefix):
            s = r.sym.get(tok)
            if s and r.has(s["path"]):
                d = self.want(r, s["path"])
                if d:
                    return f"doc/{d}#L{s['line']}", s["kind"], f"{r.name}: {s['label']}"
        if re.fullmatch(r"[0-9a-f]{7,40}", tok):
            for r in self.cands(prefix):
                full = r.commits.get(tok) or (git(r, "rev-parse", "--verify", "-q", tok + "^{commit}") or "").strip()
                if full:
                    r.commits[tok] = full
                    d = self.want(r, f"commit/{full[:12]}")
                    if d:
                        return f"doc/{d}", "commit", f"{r.name}: {full[:12]}"
        return None

    def lookup(self, prefix: str, tok: str) -> tuple[str, str] | None:
        """-> (root name, kind) for a token, touching no pages (L2 export, #0021)."""
        if prefix and prefix[:-1] in self.namespaces:
            return prefix[:-1], "link"
        for r in self.cands(prefix):
            s = r.sym.get(tok)
            if s:
                return r.name, s["kind"]
        if re.fullmatch(r"[0-9a-f]{7,40}", tok):
            for r in self.cands(prefix):
                if r.commits.get(tok):
                    return r.name, "commit"
        return None

    def resolve_path(self, prefix: str, rel: str, line: str | None) -> str | None:
        for r in self.cands(prefix):
            if r.has(rel):
                d = self.want(r, rel)
                if d:
                    return f"doc/{d}" + (f"#L{line}" if line else "")
        return None

    def linkify(self, esc: str, depth: str, *, tree: bool) -> str:
        def path(m):
            h = self.resolve_path(m.group(1), m.group(2), m.group(3))
            if not h:
                return m.group(0)
            return f'<a class="p" href="{depth}{h}">{m.group(0)}</a>'

        def tok(m):
            if BARE_ISSUE.fullmatch(m.group(2)) and not m.group(1):
                # an issue number without a root is ambiguous by construction (every repo has a
                # #0001): no default root, never linked — the lint names it (spec §5b)
                if tree:
                    self.unresolved[m.group(0) + " (no root prefix)"] = 1
                return m.group(0)
            r = self.resolve_tok(m.group(1), m.group(2))
            if not r:
                if tree and not re.fullmatch(r"[0-9a-f]{7,40}", m.group(2)):
                    self.unresolved[m.group(0)] = self.unresolved.get(m.group(0), 0) + 1
                return m.group(0)
            h, kind, title = r
            return f'<a class="t {kind}" href="{depth}{h}" title="{html.escape(title)}">{m.group(0)}</a>'

        held: list[str] = []

        def hold(a: str) -> str:
            held.append(a)
            return f"\x00{len(held) - 1}\x00"

        def md(m):
            return hold(f'<a class="x" href="{html.escape(m.group(2))}" rel="noopener">{m.group(1)}</a>')

        def url(m):
            return hold(f'<a class="x" href="{html.escape(m.group(1))}" rel="noopener">{m.group(1)}</a>')

        def ext(m):
            r = self.external(m)
            if not r:
                return m.group(0)
            href, label = r
            return hold(f'<a class="x" href="{html.escape(href)}" rel="noopener" title="{html.escape(label)}">{m.group(0)}</a>')

        s = MD_LINK_RE.sub(md, esc)
        s = URL_RE.sub(url, s)
        if self.link_re:
            s = self.link_re.sub(ext, s)
        s = PATH_RE.sub(path, s)
        s = self.token_re.sub(tok, s)
        if tree:
            s = REF_RE.sub(lambda m: f'-&gt;<a class="r" href="#{m.group(1)}">@{m.group(1)}</a>', s.replace("-&gt;@", "->@"))
        s = re.sub(r"\x00(\d+)\x00", lambda m: held[int(m.group(1))], s)
        return s

    # ---- pages
    def render_tree(self, name: str, src: str, nodes: list[Node], findings: list[str]) -> Path:
        rows = []
        _, foot = parse_links(src)
        for n, raw in enumerate(src.splitlines(), 1):
            esc = html.escape(raw)
            if foot and n >= foot:                  # the LINKS: foot: definitions, URL linked, nothing else matched
                line = URL_RE.sub(lambda m: f'<a class="x" href="{html.escape(m.group(1))}" rel="noopener">{m.group(1)}</a>', esc)
                rows.append(f'<span class="ln foot">{line}</span>')
                continue
            m = ADDR_RE.match(re.sub(r"^[\s│├└─]*", lambda x: "", raw))
            line = self.linkify(esc, "", tree=True)
            am = re.search(r"@([\w.\-]+)", raw)
            if am and re.match(r"^[\s│├└─]*@", raw):
                line = line.replace(f"@{am.group(1)}", f'<a id="{am.group(1)}" class="a" href="#{am.group(1)}">@{am.group(1)}</a>', 1)
            line = re.sub(r"^((?:[\s│├└─]|&[a-z]+;)*(?:<a[^>]*>@[^<]*</a>\s*)?)([=~?!x])(?=\s)", r'\1<b class="g g\2">\2</b>', line)
            rows.append(f'<span class="ln">{line}</span>')
        counts = {}
        for n in nodes:
            if n.glyph:
                counts[n.glyph] = counts.get(n.glyph, 0) + 1
        legend = " · ".join(f'<b class="g g{g}">{g}</b> {c}' for g, c in sorted(counts.items()))
        lint_html = "".join(f"<li>{html.escape(f)}</li>" for f in findings) or "<li>clean</li>"
        unres = ", ".join(html.escape(t) for t in sorted(self.unresolved)) or "none"
        body = (
            f'<p class="legend">{legend} · {len(nodes)} nodes · {sum(1 for n in nodes if n.addr)} addresses</p>'
            f'<pre class="tree">{"".join(r + chr(10) for r in rows)}</pre>'
            f"<h2>level-1 lint</h2><ul>{lint_html}</ul>"
            f"<h2>unresolved tokens</h2><p>{unres}</p>"
            f"<h2>roots</h2><ul>" + "".join(f"<li>{html.escape(r.name)} → {html.escape(str(r.path))} · {len(r.sym)} symbols</li>" for r in self.roots)
            + "".join(f"<li>{html.escape(k)}: → {html.escape(v)} · external, not snapshotted</li>" for k, v in sorted(self.links.items())) + "</ul>"
        )
        p = self.out / "index.html"                 # self.out is this tree's own directory
        p.write_text(page(name, body, "../"), encoding="utf-8")
        return p

    def render_docs(self) -> None:
        (self.out / "doc").mkdir(parents=True, exist_ok=True)
        self.grow = False                          # one hop: only documents the tree itself reaches are rendered
        for root, rel in list(self.todo):
            if rel.startswith("commit/"):
                full = next((f for f in root.commits.values() if f.startswith(rel[7:])), rel[7:])
                text = git(root, "show", "--stat", "--patch", "--no-color", full) or "(commit not readable)"
                ls = text.splitlines()[:600]
                cls = ""
            else:
                ls = root.lines(rel)
                cls = "md" if rel.endswith(".md") else ""
            rows = []
            for n, ln in enumerate(ls, 1):
                esc = html.escape(ln)
                h = " h" if (cls == "md" and ln.startswith("#")) else ""
                rows.append(f'<div class="l" id="L{n}"><span class="n"><a href="#L{n}">{n}</a></span>'
                            f'<span class="c{h}">{self.linkify(esc, "../", tree=False)}</span></div>')
            self.store_page(self.out / "doc" / root.docs[rel],
                            page(f"{root.name}: {rel}", f'<div class="src">{"".join(rows)}</div>', "../../"))

    def store_page(self, link: Path, content: str) -> None:
        """Content-addressed, the Nix way: the page lives ONCE in <site>/store/<sha256>.html and
        the tree's doc/ entry is a symlink to it. Two trees that saw the same version of a document
        share one file; a document that changed is visibly a different hash. Browsers resolve a
        page's relative links against the symlink path, so ../../index.html and doc/ siblings hold."""
        data = content.encode("utf-8")
        digest = hashlib.sha256(data).hexdigest()
        store = self.out.parent / "store"
        store.mkdir(parents=True, exist_ok=True)
        blob = store / f"{digest}.html"
        if not blob.exists():
            blob.write_bytes(data)
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(os.path.relpath(blob, link.parent))


def gc_store(site_root: Path) -> int:
    """Remove store blobs no tree's doc/ symlink points at. -> number removed."""
    store = site_root / "store"
    if not store.is_dir():
        return 0
    live = set()
    for lnk in site_root.glob("*/doc/*.html"):
        if lnk.is_symlink():
            live.add(lnk.resolve())
    n = 0
    for blob in store.glob("*.html"):
        if blob.resolve() not in live:
            blob.unlink(); n += 1
    return n


CSS = """
:root{--bg:#fbfbfd;--fg:#16181f;--mu:#5a5f6e;--ln:#b8bcc9;--rule:#e2e4ec;--sf:#f1f2f7;
--rule-c:#2b4a8b;--constraint-c:#6a3d9a;--seam-c:#0b6e5c;--issue-c:#8a5a0c;--gate-c:#8a5a0c;--hold-c:#9e2b2b;
--plan-c:#2b4a8b;--contract-c:#0b6e5c;--commit-c:#5a5f6e;--p-c:#2b4a8b;--a-c:#0b6e5c}
@media(prefers-color-scheme:dark){:root{--bg:#0f1117;--fg:#e6e8ef;--mu:#969cac;--ln:#4a5060;--rule:#252935;--sf:#171a22;
--rule-c:#89a7e4;--constraint-c:#c29ae8;--seam-c:#6fbf93;--issue-c:#dca94b;--gate-c:#dca94b;--hold-c:#e5837a;
--plan-c:#89a7e4;--contract-c:#6fbf93;--commit-c:#969cac;--p-c:#89a7e4;--a-c:#6fbf93}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
header{padding:1rem 1.4rem;border-bottom:1px solid var(--rule);display:flex;gap:1.4rem;align-items:baseline;flex-wrap:wrap}
header b{font-size:1.05rem}header a{color:var(--mu);text-decoration:none}
main{padding:1rem 1.4rem 4rem;max-width:1200px}
pre.tree{background:var(--sf);border:1px solid var(--rule);padding:.8rem 1rem;overflow-x:auto;line-height:1.55;white-space:pre-wrap;text-wrap:auto;overflow-wrap:anywhere}
a.t,a.p,a.r,a.a{text-decoration:none;border-bottom:1px dotted currentColor;color:var(--commit-c)}
a.rule{color:var(--rule-c)}a.constraint{color:var(--constraint-c)}a.seam{color:var(--seam-c)}a.issue{color:var(--issue-c)}
a.gate{color:var(--gate-c)}a.hold{color:var(--hold-c)}a.plan{color:var(--plan-c)}a.contract{color:var(--contract-c)}
a.commit{color:var(--commit-c)}a.p{color:var(--p-c)}a.r,a.a{color:var(--a-c)}a.a{font-weight:600}a.x{color:var(--hold-c);border-bottom-style:dashed}
a:hover{border-bottom-style:solid}.ln:target,.l:target{background:rgba(220,169,75,.22)}
b.g{display:inline-block;min-width:1em;text-align:center;border-radius:3px;padding:0 .2em}
b.g\\={color:#0b6e5c}b.g\\~{color:#5a5f6e}b.g\\?{color:#9e2b2b}b.g\\!{color:#8a5a0c}b.gx{color:#9e2b2b;background:rgba(158,43,43,.12)}
.src{border:1px solid var(--rule);background:var(--sf)}.src .l{display:flex;min-height:1.5em}
.src .n{flex:0 0 4.2em;text-align:right;padding-right:.9em;color:var(--ln);user-select:none;border-right:1px solid var(--rule)}
.src .n a{color:inherit;text-decoration:none}.src .c{padding-left:.9em;white-space:pre-wrap;word-break:break-word;flex:1}.src .h{font-weight:600}
h2{font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;color:var(--mu);margin:2rem 0 .6rem}
.legend{color:var(--mu)}
"""


def export_edges(site: Site, nodes: list[Node], name: str) -> dict:
    """Level-2 shape (spec §9, §11): nodes with their containment parent, typed ->@ edges, and
    §5b token edges (node → root:token) — a tree as the typed edge list state.json already is."""
    by_addr = {n.addr: n.n for n in nodes if n.addr}
    stack: list[tuple[int, int]] = []          # (depth, line)
    out_nodes, edges = [], []
    for n in nodes:
        while stack and stack[-1][0] >= n.depth:
            stack.pop()
        parent = stack[-1][1] if stack else None
        stack.append((n.depth, n.n))
        toks = []
        if site.link_re:
            for m in site.link_re.finditer(n.text):
                r = site.external(m)
                if r:
                    toks.append({"token": m.group(0), "root": m.group(1).partition(":")[0] if ":" in m.group(1) else "links", "kind": "link"})
                    edges.append({"from": n.n, "to": m.group(0), "type": "mentions", "line": n.n, "href": r[0]})
        for m in site.token_re.finditer(n.text):
            hit = site.lookup(m.group(1), m.group(2))
            if hit:
                toks.append({"token": m.group(0), "root": hit[0], "kind": hit[1]})
                edges.append({"from": n.n, "to": f"{hit[0]}:{m.group(2)}", "type": "mentions", "line": n.n})
        for ref, typ in re.findall(r"->@([\w.\-]+)\s*(?:\[([\w\-]+)\])?", n.text):
            edges.append({"from": n.n, "to": by_addr.get(ref), "to_addr": ref, "type": typ or None, "line": n.n})
        out_nodes.append({"n": n.n, "addr": n.addr, "glyph": n.glyph, "depth": n.depth, "parent": parent,
                          "text": n.text.strip(), "tokens": toks})
    dim = next((n.text[4:].strip() for n in nodes if n.text.startswith("DIM:")), None)
    return {"tree": name, "dim": dim, "roots": [r.name for r in site.roots], "nodes": out_nodes, "edges": edges}


def page(title: str, body: str, depth: str) -> str:
    return (f"<!doctype html><meta charset=utf-8><title>{html.escape(title)}</title><style>{CSS}</style>"
            f"<header><b>{html.escape(title)}</b><a href=\"{depth}index.html\">index</a></header><main>{body}</main>")


STAMP_NAME = re.compile(r"^(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})-(.+)$")


def write_index(site_root: Path) -> None:
    """Newest first, labelled by directory name (yyyymmdd-HHMMSS-<slug> from tools/g tree new);
    trees without a stamp sort after those, by name. Each tree is its own directory —
    <site>/<stem>/index.html + <site>/<stem>/doc/ — a snapshot of what it pointed at."""
    def key(n):
        m = STAMP_NAME.match(n)
        return (0, "".join(m.groups()[:6])) if m else (1, n)
    trees = sorted((d.name for d in site_root.iterdir() if d.is_dir() and (d / "index.html").exists()), key=key, reverse=True)
    rows = [f'<li><a class="p" href="{html.escape(n)}/index.html">{html.escape(n)}</a></li>' for n in trees]
    (site_root / "index.html").write_text(page("MindMapTrees", "<ul>" + "".join(rows) + "</ul>", ""), encoding="utf-8")


# -------------------------------------------------------------------- main --


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tree", help="a .mmt file, a .md with a ```mmt fence, or - for stdin")
    ap.add_argument("--root", action="append", default=[], metavar="NAME=PATH", help="a repository to resolve tokens in (repeatable, ordered)")
    ap.add_argument("--out", default=None, help="site root (default: <first root>/.site/mmt); this tree renders into <site>/<name>/")
    ap.add_argument("--name", default=None, help="page name (default: tree file stem, or 'tree')")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any level-1 lint finding")
    ap.add_argument("--open", action="store_true", help="open the page with xdg-open")
    ap.add_argument("--edges", metavar="FILE", help="also write the level-2 export (nodes · containment · typed ->@ edges · token edges) as JSON")
    ap.add_argument("--gc", action="store_true", help="after rendering, remove <site>/store/ pages no tree points at")
    a = ap.parse_args(argv)

    roots: list[Root] = []
    for spec in a.root or [f"{Path.cwd().name}={Path.cwd()}"]:
        name, _, path = spec.partition("=")
        if not path:
            name, path = Path(name).resolve().name, name
        roots.append(Root(name, Path(path).resolve()))
    for r in roots:
        if not r.path.is_dir():
            print(f"root {r.name}: {r.path} is not a directory", file=sys.stderr); return 2
        collect(r)

    if a.tree == "-":
        text, name = sys.stdin.read(), a.name or "tree"
    else:
        tp = Path(a.tree)
        text, name = tp.read_text(encoding="utf-8"), a.name or tp.stem
        if tp.suffix == ".md":
            text = extract_tree(text)
    src = text.strip("\n")
    nodes = parse_tree(src)
    findings, notes = lint(nodes, roots[0].adapter.get("mmt_edges") or None, [r.name for r in roots])

    site_root = Path(a.out) if a.out else roots[0].path / ".site" / "mmt"
    out = site_root / name                       # one directory per tree: its page + its doc/ snapshot
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    tree_links, _ = parse_links(src)
    site = Site(roots, out, tree_links)
    pg = site.render_tree(name, src, nodes, findings)
    site.render_docs()
    write_index(site_root)
    if a.gc:
        n = gc_store(site_root)
        if n:
            print(f"  store: {n} unreferenced page(s) removed")
    if a.edges:
        Path(a.edges).write_text(json.dumps(export_edges(site, nodes, name), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(pg)
    print(f"  {len(nodes)} nodes · {sum(len(r.docs) for r in roots)} documents rendered · "
          f"{len(site.unresolved)} unresolved tokens · {len(findings)} lint findings")
    for f in findings:
        print("  lint:", f)
    for f in notes:
        print("  note:", f)
    for t in sorted(site.unresolved):
        print("  unresolved:", t)
    if a.open:
        subprocess.Popen(["xdg-open", str(pg)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return 1 if (a.strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
