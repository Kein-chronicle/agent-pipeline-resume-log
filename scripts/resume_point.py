#!/usr/bin/env python3
"""resumable-stage-log: find where an interrupted multi-stage agent run must resume, and verify the entry protocol was honoured.
Log format (markdown, append-only):
  [ENTER] stage=3-design  agent=designer  tier=keep  reason: scale is ordinary
  [DONE]  stage=3-design
A stage with [ENTER] but no [DONE] is the interruption point: the asymmetry IS the resume marker (no separate state field).
Tier token after ENTER: keep | up | down. Silent skipping is the failure this prevents: 'keep' must be written, with a reason.
usage: resume_point.py HANDOFF.md [--stages-with-artifacts s1,s2] [--pinned designer,judge] [--defaults designer=opus,judge=opus]
exit 0 protocol honoured (prints resume point) | 1 violation | 2 bad input"""
import argparse, re, sys
ap = argparse.ArgumentParser(); ap.add_argument("log"); ap.add_argument("--stages-with-artifacts", default="")
ap.add_argument("--pinned", default="", help="roles that must never be downgraded"); ap.add_argument("--defaults", default="")
a = ap.parse_args()
try: lines = open(a.log, encoding="utf-8").read().splitlines()
except OSError as e: print(e); sys.exit(2)
defaults = dict(x.split("=") for x in a.defaults.split(",") if "=" in x); pinned = set(filter(None, a.pinned.split(",")))
enters, dones, errs = {}, set(), []
for l in lines:
    m = re.match(r"\s*\[ENTER\]\s+stage=(\S+)\s*(.*)", l)
    if m:
        st, rest = m.groups(); head = rest.split("reason:", 1)[0]          # key=value pairs count only BEFORE the free-text reason
        pairs = re.findall(r"(\w+)=(\S+)", head); kv = dict(pairs)
        if len(kv) != len(pairs): errs.append(f"stage {st}: duplicate key in the ENTER line - ambiguous, last-one-wins would hide a downgrade")
        tier = kv.get("tier"); reason = re.search(r"reason:\s*(.+)", rest)
        if tier not in ("keep", "up", "down"): errs.append(f"stage {st}: missing tier verdict (keep|up|down) - silence is not 'keep'")
        elif not reason or not reason.group(1).strip(): errs.append(f"stage {st}: tier '{tier}' without a reason")
        role = kv.get("agent")
        if tier == "down" and role in pinned: errs.append(f"stage {st}: downgrade on pinned role '{role}' is never allowed")
        models = set(re.findall(r"model=(\S+)", rest))                       # a model named anywhere on the line counts, even inside the reason text
        if role in defaults and tier == "keep" and any(m != defaults[role] for m in models): errs.append(f"stage {st}: 'keep' but model {sorted(models)[0]} != default {defaults[role]} for {role} (needs 'up' or 'down')")
        enters[st] = kv; continue
    m = re.match(r"\s*\[DONE\]\s+stage=(\S+)", l)
    if m: dones.add(m.group(1))
for st in filter(None, a.stages_with_artifacts.split(",")):
    if st not in enters: errs.append(f"stage {st} has artifacts but no [ENTER] record - the evaluation never happened")
open_ = [s for s in enters if s not in dones]
print("\n".join(errs) if errs else "protocol honoured")
print("RESUME AT: " + (open_[-1] if open_ else "(nothing open: all entered stages are done)"))
sys.exit(1 if errs else 0)
