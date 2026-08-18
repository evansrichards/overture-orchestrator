#!/usr/bin/env python3
"""Check that the skill's internal cross-references resolve.

SKILL.md is deliberately light and routes to references/*.md, so a reference
that has been renamed, or a heading citation that no longer matches, silently
strands the agent at exactly the moment it needs the detail. `claude plugin
validate` does not catch this. This does.

Checks:
  1. Every `references/<file>.md` cited from SKILL.md, a reference, or the
     command exists on disk.
  2. Every reference file is cited at least once (no orphans).
  3. Every `file.md` -> Heading / file.md § Heading citation names a heading
     that actually exists in that file.

Exits 1 on any failure, printing every problem found.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "planning-orchestrator"
REF_DIR = SKILL_DIR / "references"
COMMAND_DIR = ROOT / "commands"

# `file.md` followed by an arrow or section mark, then the heading text.
CITE = re.compile(r"`([a-z0-9-]+\.md)`\s*(?:->|→|§)\s*([^\n.;,)]+)")
# A bare `references/<name>.md` path mention.
REFPATH = re.compile(r"`?references/([a-z0-9-]+\.md)`?")
HEADING = re.compile(r"^#{1,6}\s+(.*)$", re.M)


def normalize(text):
    """Strip markup so a citation can match its heading regardless of styling."""
    text = re.sub(r"[`*§]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def main():
    if not SKILL_DIR.is_dir():
        print(f"FAIL: skill directory not found: {SKILL_DIR}")
        return 1

    ref_files = sorted(REF_DIR.glob("*.md"))
    if not ref_files:
        print(f"FAIL: no reference files under {REF_DIR}")
        return 1

    headings = {
        p.name: {normalize(m.group(1)) for m in HEADING.finditer(p.read_text())}
        for p in ref_files
    }
    headings["SKILL.md"] = {
        normalize(m.group(1)) for m in HEADING.finditer((SKILL_DIR / "SKILL.md").read_text())
    }

    # Glob rather than naming one file: a renamed command must not silently
    # drop out of coverage, which is exactly what an `if exists()` guard does.
    command_files = sorted(COMMAND_DIR.glob("*.md"))
    if not command_files:
        print(f"FAIL: no command files under {COMMAND_DIR}")
        return 1

    sources = [SKILL_DIR / "SKILL.md", *ref_files, *command_files]

    problems = []
    cited_paths = set()
    checked = 0

    for src in sources:
        text = src.read_text()
        rel = src.relative_to(ROOT)

        for m in REFPATH.finditer(text):
            name = m.group(1)
            cited_paths.add(name)
            if not (REF_DIR / name).exists():
                problems.append(f"{rel}: cites references/{name}, which does not exist")

        for m in CITE.finditer(text):
            target, heading = m.group(1), normalize(m.group(2))
            if target not in headings:
                # Workspace data files (proposal.md, index.md, ...) are not part
                # of the plugin; only plugin-internal targets are checked.
                continue
            checked += 1
            known = headings[target]
            if not any(h == heading or h.startswith(heading) or heading.startswith(h) for h in known):
                problems.append(f"{rel}: cites `{target}` -> \"{m.group(2).strip()}\", no such heading")

    for p in ref_files:
        if p.name not in cited_paths:
            problems.append(f"references/{p.name}: exists but is never cited from the routing table")

    if problems:
        print(f"FAIL: {len(problems)} cross-reference problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(
        f"OK: {len(ref_files)} reference files, all cited; "
        f"{len(command_files)} command file(s); {checked} heading citations resolve"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
