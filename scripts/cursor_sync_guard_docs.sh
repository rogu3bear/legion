#!/usr/bin/env bash

# Cursor automation: Sync main, run guards, capture docs overview, comment on latest merged PR
# Note: requires gh CLI and docker compose

set -euo pipefail

REPO="rogu3bear/legion"
TMP_DIR="tmp"
mkdir -p "$TMP_DIR"

if command -v gh >/dev/null 2>&1; then
  LAST_PR=$(gh pr list --repo "$REPO" --state merged --limit 1 --json number --jq '.[0].number')
else
  echo "gh CLI not available; cannot query latest PR" >&2
  LAST_PR=""
fi

# Pull main; fail if conflicts

git checkout main
git pull --ff-only origin main

# Rebuild containers

docker compose down
if ! docker compose up --build -d; then
  echo "Docker build failed" >&2
  if [[ -n "$LAST_PR" && $(command -v gh) ]]; then
    gh pr comment "$LAST_PR" --repo "$REPO" --body "Cursor verification build failed"
  fi
  exit 1
fi

# Run guard scripts
PORT_OUT=$(./scripts/dev/port_sanity_check.sh 2>&1 || true)
SMOKE_OUT=$(./scripts/dev/smoke_test.sh 2>&1 || true)

echo "$PORT_OUT" > "$TMP_DIR/port_status.txt"
echo "$SMOKE_OUT" > "$TMP_DIR/smoke_status.txt"

# Collect docs overview of changed files
DOC_OVERVIEW="$TMP_DIR/docs_overview.txt"
> "$DOC_OVERVIEW"

git diff --name-only HEAD~1 HEAD | grep -E '\.(md|rst)$' | while read -r f; do
  echo "### $f" >> "$DOC_OVERVIEW"
  head -n 10 "$f" >> "$DOC_OVERVIEW"
  echo "" >> "$DOC_OVERVIEW"
 done

STATUS_PORT="✅"
[[ -n "$PORT_OUT" ]] && STATUS_PORT="❌"
STATUS_SMOKE="✅"
[[ -n "$SMOKE_OUT" ]] && STATUS_SMOKE="❌"

if [[ -n "$LAST_PR" && $(command -v gh) ]]; then
  gh pr comment "$LAST_PR" --repo "$REPO" --body "Cursor verification finish

**Port-sanity:** $STATUS_PORT
\
\`\`\`
$PORT_OUT
\`\`\`

**Smoke test:** $STATUS_SMOKE
\`\`\`
$SMOKE_OUT
\`\`\`

**Docs changed:**
\`\`\`
$(cat "$DOC_OVERVIEW")
\`\`\`"
fi
