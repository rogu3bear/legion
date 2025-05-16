#!/usr/bin/env bash
set -euo pipefail

branch=$(git rev-parse --abbrev-ref HEAD)
echo "🔍 Checking workflow runs on branch $branch"

ids=$(gh run list --branch "$branch" --json databaseId,conclusion --limit 100 --jq '.[] | select(.conclusion != "success" and .conclusion != "neutral" and .conclusion != "skipped" and .conclusion != "cancelled") | .databaseId')

if [[ -z "$ids" ]]; then
  echo "✅ No failing runs on branch $branch"
  exit 0
fi

echo "❌ Failing runs: $ids"
mkdir -p /tmp/ci_logs

for id in $ids; do
  echo "⏬ Downloading logs for run $id"
  gh run view "$id" --log > "/tmp/ci_logs/$id.log" || echo "⚠️ Could not fetch logs for run $id"
  echo "📄 Tail of $id:"
  if [[ -f "/tmp/ci_logs/$id.log" ]]; then
    tail -n 50 "/tmp/ci_logs/$id.log"
  else
    echo "   (no log file found)"
  fi
done 