#!/usr/bin/env bash
# CI Watch & Fast-Merge Script
# Auto-merge PRs when CI turns green

set -e

# PRs to monitor
PRS=(98 100 114)

echo "🔍 CI Watch & Fast-Merge - Starting monitoring for PRs: ${PRS[*]}"
echo "=================================================="

for pr in "${PRS[@]}"; do
    echo ""
    echo "🔄 Checking PR #$pr..."
    
    # Check if PR is still open
    if ! gh pr view "$pr" --json state | jq -e '.state == "OPEN"' >/dev/null 2>&1; then
        echo "❌ PR #$pr is not open (may be already merged or closed)"
        continue
    fi
    
    # Get checks status
    if ! checks_output=$(gh pr checks "$pr" --json state,name 2>/dev/null); then
        echo "⚠️  No CI checks found for PR #$pr - checking if it's mergeable..."
        
        # If no checks, verify it's mergeable and merge
        if gh pr view "$pr" --json mergeable | jq -e '.mergeable == "MERGEABLE"' >/dev/null 2>&1; then
            echo "✅ PR #$pr has no CI checks and is mergeable - proceeding with merge"
            if gh pr merge "$pr" --merge --delete-branch; then
                echo "🎉 Successfully merged PR #$pr"
            else
                echo "❌ Failed to merge PR #$pr"
            fi
        else
            echo "❌ PR #$pr is not in a mergeable state"
        fi
        continue
    fi
    
    # Parse check results
    echo "📊 Check results for PR #$pr:"
    echo "$checks_output" | jq -r '.[] | "  - \(.name): \(.state)"'
    
    # Count states
    total_checks=$(echo "$checks_output" | jq length)
    success_checks=$(echo "$checks_output" | jq '[.[] | select(.state == "SUCCESS")] | length')
    failure_checks=$(echo "$checks_output" | jq '[.[] | select(.state == "FAILURE")] | length')
    pending_checks=$(echo "$checks_output" | jq '[.[] | select(.state == "PENDING" or .state == "IN_PROGRESS")] | length')
    
    echo "📈 Summary: $success_checks success, $failure_checks failed, $pending_checks pending (total: $total_checks)"
    
    # Decision logic
    if [[ $failure_checks -gt 0 ]]; then
        echo "❌ PR #$pr has failing checks - will not merge"
    elif [[ $pending_checks -gt 0 ]]; then
        echo "⏳ PR #$pr has pending checks - waiting..."
    elif [[ $success_checks -eq $total_checks ]] && [[ $total_checks -gt 0 ]]; then
        echo "✅ All checks passed for PR #$pr - proceeding with merge"
        
        # Verify it's mergeable before attempting merge
        if gh pr view "$pr" --json mergeable | jq -e '.mergeable == "MERGEABLE"' >/dev/null 2>&1; then
            if gh pr merge "$pr" --merge --delete-branch; then
                echo "🎉 Successfully merged PR #$pr"
            else
                echo "❌ Failed to merge PR #$pr"
            fi
        else
            echo "❌ PR #$pr passed all checks but is not in a mergeable state"
        fi
    else
        echo "⚠️  Unexpected state for PR #$pr"
    fi
done

echo ""
echo "=================================================="
echo "🏁 CI Watch & Fast-Merge - Monitoring complete" 