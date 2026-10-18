# agent-pipeline-resume-log

**A tiny text protocol for multi-stage agent runs: find where to resume after a crash and catch silent model downgrades.**

[![test](https://github.com/Kein-chronicle/agent-pipeline-resume-log/actions/workflows/test.yml/badge.svg)](https://github.com/Kein-chronicle/agent-pipeline-resume-log/actions/workflows/test.yml) ![license](https://img.shields.io/badge/license-MIT-blue.svg) ![dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)

## Why

Long agent pipelines get interrupted. If every stage appends `[ENTER]` and `[DONE]` lines, the next session can compute the resume point. The same log makes cost decisions auditable: every stage records whether it kept, raised or lowered its model tier and why.

## Install

**As a Claude Code skill** (Claude uses it when the task matches the skill description):

```sh
git clone https://github.com/Kein-chronicle/agent-pipeline-resume-log.git ~/.claude/skills/resumable-stage-log
```

For a single project, clone into `<project>/.claude/skills/resumable-stage-log` instead, then start a new Claude Code session.

**As plain scripts:**

```sh
git clone https://github.com/Kein-chronicle/agent-pipeline-resume-log.git
cd agent-pipeline-resume-log
```

**Requires:** Python 3.10+.

## Quick start

Check two logs:

```console
$ bash examples/demo.sh
# An interrupted run: where do I resume?
$ python3 scripts/resume_point.py examples/run-interrupted.md --pinned designer,judge
protocol honoured
RESUME AT: 2-build
[exit 0]

# A pinned role (judge) was quietly downgraded to save cost:
$ python3 scripts/resume_point.py examples/run-bad.md --pinned designer,judge
stage 1-plan: downgrade on pinned role 'judge' is never allowed
RESUME AT: 1-plan
[exit 1]
```

The output above is real: it is produced by the files in `examples/`.

## Use it on your own files

```sh
python3 scripts/resume_point.py RUN_LOG.md --pinned designer,judge --stages-with-artifacts 1-plan,2-build
```

Sample inputs for every file format are in `examples/` and `tests/`; the details are in [SKILL.md](SKILL.md).

## What it checks

- `[ENTER] stage=<id> agent=<role> tier=<keep|up|down> [model=<name>] reason: ...` and `[DONE] stage=<id>` lines. `key=value` pairs count only before `reason:`; a repeated key is an error.
- Prints `RESUME AT: <stage>`.
- Pass `--stages-with-artifacts` and `--defaults` for the artifact and model checks (the script does not read the disk).
- Fails on: a missing tier verdict, a tier without a reason, a downgrade on a pinned role, a `keep` that quietly names another model, a stage with artifacts but no `[ENTER]`.

## Limits

- It validates the log; it does not run or restart the stages.

## Related projects

These solve neighbouring problems; use them when they fit better.

- **Temporal / Airflow**: full workflow engines; this is a plain-text convention you can read in a terminal

## More from the same collection

Small, tested tools that grew out of running AI agents and game/app pipelines for months:

- [**llm-verdict-gate**](https://github.com/Kein-chronicle/llm-verdict-gate): Make AI and human review gates impossible to pass by silence: machine-parsed PASS/FAIL, missing verdict = FAIL.
- [**ci-gate-forgery-test**](https://github.com/Kein-chronicle/ci-gate-forgery-test): Prove your CI gates can actually fail: feed each gate forged-bad, empty and missing input and flag the ones that stay green.
- [**stale-verdict-guard**](https://github.com/Kein-chronicle/stale-verdict-guard): Bind a pass/fail verdict to a fingerprint of the source it judged, so an edit after review makes the verdict stale.

## Development

```sh
bash tests/run.sh
```

The tests include inputs that are supposed to be rejected, so a green run also shows the checks can fail. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

If this saved you a debugging session, a star helps other people find it. Bug reports and failing test cases are even better.

<sub>Keywords: ai-agents, agent-skills, claude-code, claude-skills, workflow, resumability, pipeline, logging</sub>
