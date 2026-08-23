#!/usr/bin/env sh
# SessionStart rehydration for the planning-orchestrator skill.
#
# Re-engagement is the forgotten half of onboarding: a returning user should see
# "3 inbox items on invitations-flow; one contested decision unowned" without
# asking. Anything more belongs in `/overture status`, not here.
#
# Contract: prints NOTHING and exits 0 unless a `planning/` workspace is present
# in or above the cwd. It ships in a general-purpose plugin, so a session that
# has nothing to do with planning must never notice it exists.

set -u

# --- Guard: locate `planning/index.md`, walking up from cwd. -----------------
dir=$(pwd -P 2>/dev/null) || exit 0
ws=""
while [ -n "$dir" ]; do
  if [ -f "$dir/planning/index.md" ]; then
    ws="$dir/planning"
    break
  fi
  [ "$dir" = "/" ] && break
  dir=$(dirname "$dir")
done
[ -n "$ws" ] || exit 0
[ -d "$ws/proposals" ] || exit 0

# --- Gather. Every count is best-effort; a bad read must not break startup. --
lines=""
total_inbox=0
total_unowned=0

for p in "$ws"/proposals/*/; do
  [ -d "$p" ] || continue
  slug=$(basename "$p")

  inbox=0
  if [ -d "$p/inbox" ]; then
    inbox=$(grep -rlE '^state:[[:space:]]*new[[:space:]]*$' "$p/inbox" 2>/dev/null | wc -l | tr -d ' ')
  fi

  # Contested with no decider: `decider:` absent, empty, or null.
  unowned=0
  if [ -d "$p/decisions" ]; then
    for f in "$p"/decisions/*.md; do
      [ -f "$f" ] || continue
      grep -qE '^state:[[:space:]]*contested[[:space:]]*$' "$f" 2>/dev/null || continue
      if ! grep -qE '^decider:[[:space:]]*[^[:space:]]' "$f" 2>/dev/null \
         || grep -qE '^decider:[[:space:]]*(null|~)[[:space:]]*$' "$f" 2>/dev/null; then
        unowned=$((unowned + 1))
      fi
    done
  fi

  [ "$inbox" -eq 0 ] && [ "$unowned" -eq 0 ] && continue

  detail=""
  [ "$inbox" -gt 0 ] && detail="$inbox inbox item$([ "$inbox" -eq 1 ] || echo s)"
  if [ "$unowned" -gt 0 ]; then
    [ -n "$detail" ] && detail="$detail, "
    detail="$detail$unowned contested decision$([ "$unowned" -eq 1 ] || echo s) unowned"
  fi

  lines="$lines
- $slug: $detail"
  total_inbox=$((total_inbox + inbox))
  total_unowned=$((total_unowned + unowned))
done

[ "$total_inbox" -eq 0 ] && [ "$total_unowned" -eq 0 ] && exit 0

# --- Report. --------------------------------------------------------------
printf 'Planning workspace at %s has pending items:%s\n\nRun `/overture status` to triage, or `/overture attach <slug>` to pick one up.\n' \
  "$ws" "$lines"
exit 0
