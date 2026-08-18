#!/usr/bin/env python3
"""Trigger eval: does the planning-orchestrator skill fire when it should?

A skill's description is its entire triggering mechanism, and the failure modes
are asymmetric. Under-triggering is invisible — the user just gets a worse
answer and never learns the skill existed. Over-triggering is loud and annoying
and trains people to distrust it. Both are description bugs, and neither shows
up in `claude plugin validate`, which never reads the description at all.

So this runs realistic queries through a headless session with the plugin
loaded and records whether the Skill tool fired. Near-miss negatives carry most
of the signal: anything can pass a set of obviously-irrelevant negatives.

    ./run-trigger-eval.py                  # all cases, 1 run each
    ./run-trigger-eval.py --runs 3         # 3 runs each, majority vote
    ./run-trigger-eval.py --case invites-alignment near-ticket
    ./run-trigger-eval.py --model claude-opus-5

Each case costs roughly $0.05-0.10, so a full 20-case run at --runs 3 is a few
dollars. That is why this is not wired into CI by default.
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = Path(__file__).resolve().parent / "trigger-cases.json"


def run_once(query, entry_points, model, timeout):
    """Run one query headless; return (fired, tools_used, cost, error)."""
    cmd = [
        "claude", "-p", query,
        "--plugin-dir", str(ROOT),
        # Skill is the only tool under test. Denying the rest keeps the run to
        # one decision — "consult the skill or not" — instead of paying for a
        # whole task, and stops a stray Bash/Write from touching the machine.
        "--allowedTools", "Skill",
        "--max-turns", "2",
        "--output-format", "stream-json", "--verbose",
    ]
    if model:
        cmd += ["--model", model]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, [], 0.0, "timeout"

    tools, cost, fired = [], 0.0, False
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                name = block.get("name", "")
                tools.append(name)
                if name == "Skill":
                    raw = json.dumps(block.get("input", {}))
                    if any(ep in raw for ep in entry_points):
                        fired = True
        elif event.get("type") == "result":
            cost = event.get("total_cost_usd") or 0.0

    if not tools and proc.returncode != 0:
        return False, [], cost, (proc.stderr or "").strip()[:200] or "no output"
    return fired, tools, cost, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=1, help="runs per case; >1 uses a majority vote")
    ap.add_argument("--case", nargs="*", help="only these case ids")
    ap.add_argument("--model", help="model override (defaults to the CLI's)")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--json", help="write full results to this path")
    args = ap.parse_args()

    spec = json.loads(CASES.read_text())
    entry_points = spec["entry_points"]
    cases = spec["cases"]
    if args.case:
        wanted = set(args.case)
        cases = [c for c in cases if c["id"] in wanted]
        missing = wanted - {c["id"] for c in cases}
        if missing:
            print(f"unknown case id(s): {', '.join(sorted(missing))}", file=sys.stderr)
            return 2
    if not cases:
        print("no cases selected", file=sys.stderr)
        return 2

    results, total_cost = [], 0.0
    print(f"{len(cases)} case(s) x {args.runs} run(s), entry points: {', '.join(entry_points)}\n")

    for case in cases:
        fires, tool_log, errors = [], Counter(), []
        for _ in range(args.runs):
            fired, tools, cost, err = run_once(case["query"], entry_points, args.model, args.timeout)
            fires.append(fired)
            tool_log.update(tools)
            total_cost += cost
            if err:
                errors.append(err)

        fired_n = sum(fires)
        # Majority vote: a skill that fires on 1 of 3 runs is not reliable.
        observed = fired_n * 2 > args.runs
        passed = observed == case["should_trigger"]

        want = "fire" if case["should_trigger"] else "stay quiet"
        mark = "PASS" if passed else "FAIL"
        rate = f"{fired_n}/{args.runs}"
        print(f"  [{mark}] {case['id']:<24} want={want:<10} fired={rate:<5} "
              f"tools={dict(tool_log) or '{}'}")
        if errors:
            print(f"         errors: {errors[0]}")

        results.append({**case, "fired": fired_n, "runs": args.runs,
                        "passed": passed, "tools": dict(tool_log), "errors": errors})

    npass = sum(r["passed"] for r in results)
    pos = [r for r in results if r["should_trigger"]]
    neg = [r for r in results if not r["should_trigger"]]
    print(f"\n{npass}/{len(results)} passed  "
          f"(recall {sum(r['passed'] for r in pos)}/{len(pos)}, "
          f"precision-side {sum(r['passed'] for r in neg)}/{len(neg)})  "
          f"~${total_cost:.2f}")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"entry_points": entry_points, "runs": args.runs, "model": args.model,
             "passed": npass, "total": len(results),
             "cost_usd": round(total_cost, 4), "results": results}, indent=2))
        print(f"wrote {args.json}")

    failures = [r["id"] for r in results if not r["passed"]]
    if failures:
        print(f"\nfailing: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
