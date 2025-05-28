#!/usr/bin/env bash
# Quick CI Check & Merge - Based on original user command
# One-shot check for PRs #98, #100, #114

set -e

echo "🚀 Quick CI Check & Merge for PRs: 98, 100, 114"
echo "==============================================="

for pr in 98 100 114; do
    echo ""
    echo "🔄 Processing PR #$pr..."
    
    # Check if PR is open
    if ! gh pr view "$pr" --json state | jq -e '.state == "OPEN"' >/dev/null 2>&1; then
        echo "❌ PR #$pr is not open"
        continue
    fi
    
    # Check if PR has any checks
    if ! gh pr checks "$pr" --json state >/dev/null 2>&1; then
        echo "⚠️  No CI checks for PR #$pr - checking mergeable status..."
        if gh pr view "$pr" --json mergeable | jq -e '.mergeable == "MERGEABLE"' >/dev/null 2>&1; then
            gh pr merge "$pr" --merge --delete-branch --auto
            echo "Merged $pr ✅ (no CI checks required)"
        else
            echo "PR $pr not mergeable ❌"
        fi
        continue
    fi
    
    # Check all CI status
    if gh pr checks "$pr" --json state | jq -e 'all(.state == "SUCCESS")' >/dev/null 2>&1; then
        # All checks passed
        if gh pr view "$pr" --json mergeable | jq -e '.mergeable == "MERGEABLE"' >/dev/null 2>&1; then
            gh pr merge "$pr" --merge --delete-branch --auto
            echo "Merged $pr ✅"
        else
            echo "PR $pr passed checks but not mergeable ❌"
        fi
    else
        echo "PR $pr still has failing/pending checks ❌"
    fi
done

echo ""
echo "🏁 Quick merge check complete!" 