#!/usr/bin/env bash
cd "$(dirname "$0")/.."
run() { printf '$ %s\n' "$*"; "$@"; printf '[exit %s]\n\n' "$?"; }
echo "# An interrupted run: where do I resume?"
run python3 scripts/resume_point.py examples/run-interrupted.md --pinned designer,judge
echo "# A pinned role (judge) was quietly downgraded to save cost:"
run python3 scripts/resume_point.py examples/run-bad.md --pinned designer,judge
