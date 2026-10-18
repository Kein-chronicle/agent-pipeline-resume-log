#!/usr/bin/env bash
set -u; here="$(cd "$(dirname "$0")" && pwd)"; s="$here/../scripts/resume_point.py"; d="$(mktemp -d)"; bad=0
t() { name="$1"; want="$2"; pat="$3"; shift 3; out="$("$@" 2>&1)"; got=$?; if [ "$got" = "$want" ] && echo "$out" | grep -q -- "$pat"; then echo "ok   $name"; else echo "FAIL $name (want $want got $got, pattern '$pat')"; echo "$out" | sed 's/^/     /'; bad=1; fi; }
cat > "$d/ok.md" <<'M'
[ENTER] stage=1-plan agent=designer tier=keep reason: ordinary scale
[DONE]  stage=1-plan
[ENTER] stage=2-build agent=coder tier=down reason: mechanical edits
M
t "interrupted run reports the resume point" 0 "RESUME AT: 2-build" python3 "$s" "$d/ok.md" --pinned designer,judge
printf '[ENTER] stage=1-plan agent=designer reason: x\n' > "$d/notier.md"
t "missing tier verdict fails" 1 "missing tier verdict" python3 "$s" "$d/notier.md"
printf '[ENTER] stage=1-plan agent=designer tier=keep\n' > "$d/noreason.md"
t "tier without reason fails" 1 "without a reason" python3 "$s" "$d/noreason.md"
printf '[ENTER] stage=1-plan agent=judge tier=down reason: save money\n' > "$d/down.md"
t "downgrading a pinned role fails" 1 "pinned role" python3 "$s" "$d/down.md" --pinned designer,judge
printf '[ENTER] stage=1-plan agent=designer tier=keep reason: fine model=sonnet\n' > "$d/sneak.md"
t "'keep' that quietly uses another model fails" 1 "needs 'up' or 'down'" python3 "$s" "$d/sneak.md" --defaults designer=opus
printf '[ENTER] stage=1-plan agent=designer tier=keep reason: ok\n[DONE] stage=1-plan\n' > "$d/skipped.md"
t "stage with artifacts but no ENTER fails" 1 "no \[ENTER\]" python3 "$s" "$d/skipped.md" --stages-with-artifacts 1-plan,2-build
printf '[ENTER] stage=1-plan agent=judge tier=down reason: ok tier=keep\n' > "$d/hide.md"
t "a reason that smuggles 'tier=keep' cannot hide a pinned downgrade" 1 "pinned role" python3 "$s" "$d/hide.md" --pinned designer,judge
printf '[ENTER] stage=1-plan agent=judge tier=keep tier=down reason: x\n' > "$d/dup.md"
t "duplicate keys are rejected" 1 "duplicate key" python3 "$s" "$d/dup.md"
rm -rf "$d"; exit $bad
