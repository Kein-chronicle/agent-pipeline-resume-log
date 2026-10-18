---
name: resumable-stage-log
description: Make long multi-stage agent runs resumable after usage-limit cut-offs and make "did we actually evaluate the model/tier for this stage?" machine-checkable. Use when a pipeline has many stages run by different agent roles/models, when sessions get interrupted mid-stage, or when silent skipping of a planned decision (model tier, review) must become an explicit written statement.
---

# resumable-stage-log

Two problems, one append-only log (e.g. `HANDOFF.md`):

1. **Resume.** Write `[ENTER] stage=...` when starting and `[DONE] stage=...` when finished. An ENTER without a DONE *is* the
   interruption point - no separate state field to go stale.
2. **Silent skipping.** Before each stage you decide "is this model/tier enough for this scale?". If "keep" is indistinguishable
   from "never asked", the evaluation never happens (in the author's own runs, a comparable judging field was never filled in over 12 cycles; anecdotal, not a benchmark).
   So **every ENTER must state `tier=keep|up|down` and a `reason:`**; missing = FAIL.

What the checker (`scripts/resume_point.py`) really proves, said honestly:
- **Real checks:** every stage you list in `--stages-with-artifacts` has an ENTER (the script never reads the disk: you pass in which stages produced artifacts); tier token parses; a stage that names another model than the role's
  default must say `up`/`down`; downgrading a **pinned** role (design/judging roles) always fails.
- **Self-report only:** whether the judgement was sincere. `keep / reason: ordinary scale` passes. The gate stops *silence*, not
  laziness - and turning silence into an explicit statement is already a measurable deterrent.

```bash
python3 scripts/resume_point.py HANDOFF.md --stages-with-artifacts 1-plan,2-build --pinned designer,judge --defaults designer=opus
bash tests/run.sh
```
Pass `--stages-with-artifacts` and `--defaults` every time: without them those two checks do not run, and a gate that silently skips a check is a gate that is off.
The log line is `[ENTER] stage=<id> agent=<role> tier=<keep|up|down> [model=<name>] reason: <text>`; `key=value` pairs count only before `reason:`, and a repeated key is an error.
