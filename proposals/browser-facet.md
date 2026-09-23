# browser facet — a gantry project owns its browsers as widgets

**Status:** discussion (2026-09-23) · **Refs (candidate):** [2] never overwrite · [10] self-hosting · a new
constraint group `C-BROWSER` if this lands in gantry's plan, or its own plan if it lands beside gantry ·
**Next step:** Tier-1 beats below are drafts; the operator confirms/edits them, THEN constraints, THEN issues.

## situation (what is true on this machine today)

- `~/browserProfiles/<name>/chromium/` — ~95 Brave/Chromium user-data-dirs, one per project. Credentials,
  sessions, extensions live there. No launcher convention; a profile is a directory.
- `~/context/personal/browserProfileBackups/` — a git-crypt repo with `extract-browser-state.py` run daily by
  a systemd user timer (`browser-state-backup.timer`, 03:@MINUTE@ UTC, host and VM staggered). It copies each
  profile, reads ONLY `History` (SQLite) and `Sessions/Session_*` (SNSS, replayed so closed tabs drop out and
  Marvellous Suspender placeholders decode to the real page), and commits `profiles/<profile>/history.jsonl`
  (merged, never overwritten — Chromium expires history after ~90 days) and `tabs.json` (session order, so
  diffs carry signal). Never touches cookies, logins, storage. Layout `<hostname>-<date>/profiles/<profile>/`.
- `~/.claude/browser-profiles/` — a Claude-side profile convention, one entry, empty.
- The developer LLM's web-fetch leaves no trace in any browser; the human's research does. Two research
  trails, one visible.
- cubeOnSKOS-ui drives Playwright journeys against a live stack (its U8 rule: "driven, not just asserted");
  those runs use whatever profile Playwright makes.

## proposition (the shape)

A **facet** — like `trees/`: something nearly every project uses, shipped by gantry, attached per repo.

- A project declares its browsers in `.gantry/adapter.json`, a data hook like `mmt_tokens`:
  ```json
  "browsers": {
    "record": "../<project>-browser-record",
    "profiles": {
      "research":   {"kind": "permanent", "default_for": "research"},
      "test-admin": {"kind": "permanent"},
      "signup":     {"kind": "transient"}
    }
  }
  ```
  Names, kinds, which is the research default. Paths to profile dirs, Playwright version, redaction rules
  live in the **record repo** (the ingress boundary, authoritative); the adapter only names the relationship.
- **Two kinds of profile.** *Permanent*: named, long-lived, credentials stay only in the untracked profile
  dir (research; a test account that stays logged in). *Transient*: created empty in an ephemeral path
  outside the archiver's scan root, used once, removed by its creator (trap/finally), never by the next
  run's optimism.
- **A file/config wrapper over Playwright**, small verb surface: `tools/g browser open <profile>` ·
  `new <name> --kind permanent|transient` · `snapshot` (tabs → evidence entry, by invoking the existing
  archiver, then recording its commit sha) · `events` (list/tail a recorded run). Playwright itself and the
  journey scripts stay the project's own tooling.
- **Recorded events as evidence.** A run records navigations (query/fragment stripped by default), console,
  network *metadata* (URL, method, status, timing — headers deny-by-default, allowlist to keep), screenshot
  hashes; JSON lines, diffable, in the record repo. A recorded run is a `=` fact in an issue or tree only if
  it is reproducible: committed script + named profile (+ seed). An event log with no replayable script is a
  screenshot, and must not satisfy an Exit clause.
- **Linkable, never stored.** A profile or a run is a namespace token (§5c): `browser:test-admin`,
  `run:2026-09-23-req42`, resolved through `mmt_links` into the record repo. The gantry repo holds pointers;
  the record repo holds contents; the tree links and never snapshots them.
- **An issue names its sub-profile** as a declared line (like `deps:`), one-directional, checkable by
  `g check` without a browser: the stated attachment must be the true one, and a second claim on an
  exclusively-leased profile is a hold, not a queue.
- **The agent's fetch leaves a trace.** A web-fetch made *for an issue* appends a history entry (url, title,
  time, issue) to the project's research profile — scoped to fetches tagged with the issue/profile, not a
  blanket hook on every fetch (reading gantry's own docs is not project research). Human and agent research
  then sit in one place, archived by the same daily job.
- **The record lives outside the primary gantry repo**, attached by reference — browsers are ingress
  (research) or testing, not project truth. The archiver stays the single owner of profile → git capture;
  gantry never reimplements it and never manages its git-crypt key.

## lived experience it serves (Tier-1 beats — DRAFT, from the operator's lens; to be confirmed)

1. I open an issue and the right browser is just there — logged in, on yesterday's tabs. Ninety-five
   projects; my memory is not the index, the project is.
2. I switch project mid-afternoon and the browser switches with me: different accounts, bookmarks,
   extensions. If I see A's tab bar while my head is in B, the boundary that keeps 95 things from becoming
   one mess is gone.
3. I ask the agent to pick up research I started yesterday and it starts from the tabs I left open, not
   cold. The tab set is the thread of the work.
4. I hand an agent a browser already logged into staging and I need to know that is the only thing it can
   touch — not my email, not the client's Slack three projects over.
5. "Does signup work for a brand-new user" needs a browser with nothing in it, gone when the test ends. If
   it leaves a trace, the next test is contaminated and I won't know why.
6. After the agent researches, I want to see what it actually looked at — the pages, in order — the way I'd
   check a colleague's work. Its fetch tool leaves nothing behind; that is the gap.
7. A test session breaks (stuck modal, redirect loop); I need a clean one back fast without the breakage
   bleeding into the persistent profile.
8. I rebuild the machine and every project's browser world comes back. If it doesn't, I re-log-into forty
   things and lose trust in the backup.
9. I file an issue and say in it "this belongs to the checkout-flow sub-profile" — some projects have more
   than one identity (staging/prod, admin/customer) and the issue points at the right one the way it points
   at a constraint.
10. The daily archive runs quietly and I trust it captures true state, because if I had to remember to
    snapshot my own browser I wouldn't.
11. An agent creates a *permanent* browser identity for a new project and it is a first-class thing I return
    to next week, not a side effect that vanishes with the session.

**Never:** an agent in my personal profile · a transient that becomes permanent, or a permanent silently
discarded · project A seeing project B's sessions · untraceable browsing on my behalf · a profile that does
not fully restore · an issue's declared sub-profile drifting from the one actually used.

## use cases the beats imply (research · testing)

- research trail per issue without asking the agent to summarise (history entries tagged by issue) · "did we
  already fetch this domain in this project?" → boolean + last seen, so the agent skips redundant fetches ·
  "what was I mid-reading" on resume = the decoded tab set · two streams researching the same API → diff their
  history for contradictions · a human-gated close can cite a committed history entry as its basis ·
  cross-project: "did we hit this Stripe webhook bug before?" over ~95 profiles' history.
- an Exit clause proven by a recorded journey on the logged-in test profile (screenshot hash, console clean)
  · a regression fear answered by a fresh transient + replayed script + diffed log · "3/3 identical runs"
  as the latch for a flaky fix · a reopened issue keeps the old run as the prior `=` fact, no overwrite ·
  a stream gets its own transient so parallel streams never share cookies · `g check` asserts "this issue
  names a profile, and that profile has a run newer than the last commit touching the code".

## constraints it would need (candidates for plan §2 — each traces to a beat above)

- C1 **Named or nothing.** Every browser launch names a gantry-owned profile; no default resolves to the
  personal profile; the wrapper refuses to launch otherwise. (beats 4, 12-never)
- C2 **Transient means gone.** Ephemeral path outside the archiver's root; cleanup by the creator; a
  crashed test cannot leave a logged-in dir for the next run or the archiver to find. (5, 7)
- C3 **Evidence is replayable.** A recorded run counts as `=` only with its committed script + named profile;
  otherwise it is a screenshot and cannot close an Exit. (testing lens)
- C4 **Deny-by-default recording.** Headers, cookies, storage, tokens in URLs never reach disk; query and
  fragment stripped unless an origin is opted in by committed config. (never-list)
- C5 **Attachment is declared, one-directional, checkable.** An issue's sub-profile is a line the tools
  read; `g check` validates it statically; exclusive lease per profile. (9, 6-never)
- C6 **Record outside, pointer inside.** The gantry repo holds names and namespaces; the record repo holds
  contents and is authoritative for paths/versions/redaction; the archiver owns capture and its key. (10)
- C7 **Agent research is visible where human research is.** Issue-tagged fetches land in the research
  profile's history; the same daily job archives both. (6, 3)
- C8 **Pinned toolchain.** Playwright + Chromium builds pinned in the record repo; a mismatch is a hold. (8)
- C9 **Scope: evidence for a directed session.** No unattended crawls, selector libraries, or headless
  pools without their own Tier-1 justification. (risk lens)

## open (undecided, and whose call)

- **Where it lives** — a `C-BROWSER` group in gantry's plan.md (a facet like trees) or its own repo adopted
  by projects (like the blueprinter)? ⛭ operator. The archiver already lives outside; the wrapper could too.
- **The archiver and a live Playwright session on one profile** — the wrapper takes a lock for the session;
  does the existing job learn to skip-and-retry, or does gantry only ever use profiles the archiver is not
  scanning at that hour? ⛭ operator (it is his job to change).
- **Pointer form** — `browser:test-admin` by name (readable, mutable) vs record-repo sha+path (immutable,
  opaque)? Probably name in prose, sha in evidence.
- **The fetch hook** — a CLAUDE.md instruction ("when fetching for an issue, also `g browser visited <url>`")
  vs an MCP tool that does both. The instruction is available today; the tool is the gantryd/MCP thread.
- **Restore** — beat 8 wants full profile restore (cookies, sessions); the archiver deliberately captures
  only history+tabs. Is full-profile backup this facet's job, or a separate, encrypted, non-git concern?
