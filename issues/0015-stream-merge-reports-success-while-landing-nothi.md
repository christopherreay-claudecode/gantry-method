# #0015 — stream merge reports success while landing nothing: git merge runs with check=False
type: bug        status: open
refs: [1] [2] [8]   opened: metalknee-dojo-a11-merge   closed-by: <sha>

**Found in `metalKnee-dojo`, 2026-08-20.** A stream's entire code output was silently discarded by a
merge that printed `merged + committed` and marked the stream `merged`. It was noticed only because
the *next* stream tried to build on the work and found it absent.

## The mechanism, exactly

`cmd_stream_merge`:

```python
if git(repo, "status", "--porcelain", "--untracked-files=no", check=False).stdout.strip():
    die("parent has uncommitted changes — commit or stash before merging a stream")
...
git(repo, "merge", "--no-ff", "--no-commit", s["branch"], check=False)   # <-- the defect
```

Two facts combine:

1. **The dirty-guard ignores untracked files** (`--untracked-files=no`) — deliberately, so that scratch
   files do not block a merge.
2. **`git merge` refuses to run when it would overwrite an untracked file**, and exits non-zero.

`check=False` then swallows that failure. Control falls through to the conflict scan (which finds
nothing, because no merge is in progress), the metadata regeneration is committed, the stream is
marked `merged`, and the tool reports success. **The branch's changes never enter the parent.**

## What it looked like

The parent had three untracked files. The merge commit contains **only**:

```
.gantry/streams.json · GRAPH.md · issues/INDEX.md · tools/octail.py · tools/stream.sh
5 files changed, 103 insertions(+), 2 deletions(-)
```

— the metadata plus the parent's own untracked files. The stream's four new modules and ~1,280
lines were absent. A merge of the same shape in a sibling repo landed 52 files correctly, because
that parent happened to be clean.

**The failure is worst exactly where it is least visible:** everything the orchestrator checks after
a merge — `GRAPH.md`, `INDEX.md`, the stream's `merged` status — is regenerated metadata, and all of
it says the merge succeeded.

## Fix

1. **Check the merge's exit status.** A failed `git merge` must `die()` with git's own stderr, not
   fall through. This is the whole bug; everything else is hardening.
2. **Make the guard match git's actual precondition.** Either include untracked files in the
   dirty-check, or (better) pre-flight the specific collision: if the branch adds a path that exists
   untracked in the parent, name that path and stop.
3. **Verify the merge landed.** After committing, assert `git diff --quiet <branch> HEAD -- <tracked
   paths of the branch>`, or at minimum that the merge commit has two parents. A stream marked
   `merged` whose commit has one parent is the signature of this bug and is cheap to detect.
4. Consider `--no-commit` + explicit `die` on conflicts already handled — that path is fine; it is
   only the unchecked call that is not.

## Exit

A merge that cannot complete **fails loudly and leaves the stream `open`**. A regression test: parent
with an untracked file that the branch also adds, merge, assert non-zero exit and that the stream is
still `open`.
