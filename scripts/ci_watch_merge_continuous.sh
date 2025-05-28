#!/usr/bin/env bash
# Continuous CI Watch & Fast-Merge Script
# Auto-merge PRs when CI turns green - runs every 10 minutes

set -e

# PRs to monitor
PRS=(98 100 114)
INTERVAL=600  # 10 minutes in seconds

echo "🔍 Continuous CI Watch & Fast-Merge - Monitoring PRs: ${PRS[*]}"
echo "⏰ Check interval: ${INTERVAL}s (10 minutes)"
echo "🛑 Press Ctrl+C to stop monitoring"
echo "=================================================="

# Function to check if any target PRs are still open
check_open_prs() {
    local open_count=0
    for pr in "${PRS[@]}"; do
        if gh pr view "$pr" --json state | jq -e '.state == "OPEN"' >/dev/null 2>&1; then
            ((open_count++))
        fi
    done
    echo $open_count
}

# Function to run the CI check and merge logic
run_ci_check() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo ""
    echo "🕐 [$timestamp] Running CI check cycle..."
    
    for pr in "${PRS[@]}"; do
        echo ""
        echo "🔄 Checking PR #$pr..."
        
        # Check if PR is still open
        if ! gh pr view "$pr" --json state | jq -e '.state == "OPEN"' >/dev/null 2>&1; then
            echo "✅ PR #$pr is no longer open (merged or closed)"
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
}

# Trap to handle clean exit
trap 'echo -e "\n🛑 Monitoring stopped by user"; exit 0' INT TERM

# Main monitoring loop
while true; do
    run_ci_check
    
    # Check if any PRs are still open
    open_prs=$(check_open_prs)
    
    if [[ $open_prs -eq 0 ]]; then
        echo ""
        echo "🎯 All target PRs have been processed (merged or closed)"
        echo "🏁 Monitoring complete - exiting"
        break
    fi
    
    echo ""
    echo "📊 Status: $open_prs PRs still open"
    echo "⏰ Waiting ${INTERVAL}s before next check..."
    echo "=================================================="
    
    sleep $INTERVAL
done 