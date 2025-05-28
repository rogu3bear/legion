#!/usr/bin/env bash
# =============================================================================
# Legion Workflow Manager - Enhanced Track E-A Implementation
# =============================================================================
# Purpose: Manual workflow triggering, log surfacing, PR monitoring, and issue tracking
# Author: Cursor (Track E-A Implementation)
# Dependencies: gh CLI, jq, git
# =============================================================================

set -e

# =============================================================================
# CONFIGURATION & STYLING
# =============================================================================

# Color codes for terminal output
RED='\033[0;31m'        # Error states, failures
GREEN='\033[0;32m'      # Success states, completed
YELLOW='\033[1;33m'     # Warning states, in-progress
BLUE='\033[0;34m'       # Info states, headers
PURPLE='\033[0;35m'     # Special states, PRs
CYAN='\033[0;36m'       # Neutral states, issues
NC='\033[0m'            # No Color (reset)

# Available Legion workflows for management
WORKFLOWS=(
    "CI:.github/workflows/ci.yml"
    "Interface Backend CI:.github/workflows/interface_ci.yaml"
    "Middleware CI:.github/workflows/middleware-ci.yml"
    "link-check:.github/workflows/link-check.yml"
    "Base Image:.github/workflows/base-image.yml"
)

# Target PRs for CI monitoring (from earlier CI watch system)
MONITORED_PRS=(98 100 114)

echo -e "${BLUE}🔧 Legion Workflow Manager (Enhanced)${NC}"
echo -e "${BLUE}======================================${NC}"

# =============================================================================
# CORE WORKFLOW FUNCTIONS
# =============================================================================

# Display comprehensive workflow status including PRs and issues
show_workflow_status() {
    echo -e "\n${BLUE}📊 Current Workflow Status:${NC}"
    echo "=============================="
    
    # Get workflow runs with enhanced status display
    gh run list --limit 15 --json status,name,workflowName,conclusion,headBranch,event,createdAt,databaseId | \
        jq -r '.[] | "\(.status) | \(.conclusion // "N/A") | \(.workflowName) | \(.headBranch) | \(.event) | \(.createdAt) | \(.databaseId)"' | \
        while IFS='|' read -r status conclusion workflow branch event created run_id; do
            # Enhanced status icons and colors
            case $status in
                "completed")
                    if [[ "$conclusion" == "success" ]]; then
                        icon="✅"; color="$GREEN"
                    elif [[ "$conclusion" == "failure" ]]; then
                        icon="❌"; color="$RED"
                    elif [[ "$conclusion" == "cancelled" ]]; then
                        icon="🚫"; color="$YELLOW"
                    else
                        icon="⚠️"; color="$YELLOW"
                    fi
                    ;;
                "in_progress")
                    icon="🔄"; color="$YELLOW"
                    ;;
                "queued")
                    icon="⏳"; color="$CYAN"
                    ;;
                *)
                    icon="❓"; color="$NC"
                    ;;
            esac
            
            # Format branch name for better readability
            short_branch=$(echo "$branch" | sed 's/auto\/implement-patch-/patch-/' | sed 's/auto\/add-/add-/' | cut -c1-25)
            
            echo -e "${color}${icon} ${workflow} | ${short_branch} | ${event} | ID:${run_id}${NC}"
        done
    
    # Show PR-specific workflow status
    show_pr_workflow_status
    
    # Show related GitHub issues
    show_related_issues
}

# Enhanced function to show PR-specific workflow status
show_pr_workflow_status() {
    echo -e "\n${PURPLE}🔀 PR Workflow Status:${NC}"
    echo "======================="
    
    for pr in "${MONITORED_PRS[@]}"; do
        echo -e "\n${PURPLE}📋 PR #${pr}:${NC}"
        
        # Check if PR exists and is open
        if gh pr view "$pr" --json state,title,mergeable 2>/dev/null | jq -e '.state == "OPEN"' >/dev/null; then
            pr_info=$(gh pr view "$pr" --json title,mergeable,headRefName)
            title=$(echo "$pr_info" | jq -r '.title' | cut -c1-50)
            mergeable=$(echo "$pr_info" | jq -r '.mergeable')
            branch=$(echo "$pr_info" | jq -r '.headRefName')
            
            echo -e "   📝 Title: ${title}..."
            echo -e "   🌿 Branch: ${branch}"
            echo -e "   🔀 Mergeable: ${mergeable}"
            
            # Get CI checks for this PR
            if checks_output=$(gh pr checks "$pr" --json state,name 2>/dev/null); then
                echo "   🔍 CI Checks:"
                echo "$checks_output" | jq -r '.[] | "     - \(.name): \(.state)"' | head -5
            else
                echo "   ⚠️  No CI checks found"
            fi
        else
            echo -e "   ${RED}❌ PR not open or not found${NC}"
        fi
    done
}

# Function to show related GitHub issues
show_related_issues() {
    echo -e "\n${CYAN}🐛 Related GitHub Issues:${NC}"
    echo "========================="
    
    # Get recent issues related to CI/workflows
    gh issue list --limit 5 --label "ci,workflow,automation" --json number,title,state,labels 2>/dev/null | \
        jq -r '.[] | "\(.number) | \(.title) | \(.state) | \(.labels | map(.name) | join(","))"' | \
        while IFS='|' read -r number title state labels; do
            case $state in
                "OPEN")
                    icon="🔴"; color="$RED"
                    ;;
                "CLOSED")
                    icon="✅"; color="$GREEN"
                    ;;
                *)
                    icon="❓"; color="$NC"
                    ;;
            esac
            short_title=$(echo "$title" | cut -c1-40)
            echo -e "${color}${icon} #${number}: ${short_title}... [${labels}]${NC}"
        done || echo "   ℹ️  No workflow-related issues found"
}

# Enhanced workflow triggering with PR context
trigger_workflow() {
    local workflow_name="$1"
    local workflow_file="$2"
    
    echo -e "\n${YELLOW}🚀 Triggering workflow: ${workflow_name}${NC}"
    echo "File: $workflow_file"
    
    # Check if workflow supports manual dispatch
    if grep -q "workflow_dispatch" "$workflow_file" 2>/dev/null; then
        echo "✅ Workflow supports manual dispatch"
        
        # Optional: Allow targeting specific branch/PR
        if [[ -n "$3" ]]; then
            echo "🎯 Targeting branch/ref: $3"
            if gh workflow run "$workflow_file" --ref "$3"; then
                echo -e "${GREEN}✅ Successfully triggered ${workflow_name} on $3${NC}"
            else
                echo -e "${RED}❌ Failed to trigger ${workflow_name} on $3${NC}"
            fi
        else
            if gh workflow run "$workflow_file"; then
                echo -e "${GREEN}✅ Successfully triggered ${workflow_name}${NC}"
            else
                echo -e "${RED}❌ Failed to trigger ${workflow_name}${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Workflow doesn't support manual dispatch${NC}"
        
        # Enhanced re-run logic with multiple recent runs
        echo "🔍 Looking for recent runs to re-run..."
        local run_ids=$(gh run list --workflow="$workflow_file" --limit 3 --json databaseId --jq '.[].databaseId')
        local count=0
        
        for run_id in $run_ids; do
            if [[ -n "$run_id" && "$run_id" != "null" ]]; then
                echo "📋 Found recent run ID: $run_id"
                if gh run rerun "$run_id" 2>/dev/null; then
                    echo -e "${GREEN}✅ Successfully re-ran ${workflow_name} (Run: $run_id)${NC}"
                    count=$((count + 1))
                    break
                else
                    echo -e "${YELLOW}⚠️  Could not re-run $run_id (may be in progress)${NC}"
                fi
            fi
        done
        
        if [[ $count -eq 0 ]]; then
            echo -e "${YELLOW}⚠️  No recent runs available for re-running${NC}"
        fi
    fi
}

# Enhanced log surfacing with error analysis
surface_logs() {
    local run_id="$1"
    local workflow_name="$2"
    
    echo -e "\n${BLUE}📋 Surfacing logs for: ${workflow_name} (Run ID: ${run_id})${NC}"
    echo "=================================================="
    
    # Get comprehensive run details
    echo -e "${BLUE}📊 Run Overview:${NC}"
    gh run view "$run_id" --json status,conclusion,jobs,createdAt,updatedAt,headBranch,event | \
        jq '{
            status: .status,
            conclusion: .conclusion,
            branch: .headBranch,
            event: .event,
            created: .createdAt,
            updated: .updatedAt,
            job_count: (.jobs | length),
            failed_jobs: [.jobs[] | select(.conclusion == "failure") | .name]
        }'
    
    echo -e "\n${BLUE}📄 Job Details:${NC}"
    echo "==============="
    
    # Show job-specific status with enhanced details
    gh run view "$run_id" --json jobs | \
        jq -r '.jobs[] | "\(.name) | \(.status) | \(.conclusion // "N/A") | \(.databaseId)"' | \
        while IFS='|' read -r job_name job_status job_conclusion job_id; do
            case $job_conclusion in
                "success")
                    icon="✅"; color="$GREEN"
                    ;;
                "failure")
                    icon="❌"; color="$RED"
                    ;;
                "cancelled")
                    icon="🚫"; color="$YELLOW"
                    ;;
                *)
                    if [[ "$job_status" == "in_progress" ]]; then
                        icon="🔄"; color="$YELLOW"
                    else
                        icon="⏳"; color="$CYAN"
                    fi
                    ;;
            esac
            echo -e "${color}${icon} ${job_name} (${job_status}/${job_conclusion})${NC}"
        done
    
    # Attempt to download and analyze logs
    local log_dir="/tmp/legion_workflow_logs_${run_id}_$$"
    mkdir -p "$log_dir"
    
    echo -e "\n${BLUE}📁 Log Analysis:${NC}"
    echo "=================="
    
    if gh run download "$run_id" --dir "$log_dir" 2>/dev/null; then
        echo -e "${GREEN}✅ Logs downloaded to: ${log_dir}${NC}"
        
        # Analyze log files for common error patterns
        echo -e "\n${BLUE}🔍 Error Analysis:${NC}"
        local error_count=0
        
        find "$log_dir" -type f -name "*.txt" | while read -r log_file; do
            local errors=$(grep -i "error\|failed\|exception" "$log_file" 2>/dev/null | head -3)
            if [[ -n "$errors" ]]; then
                echo -e "${RED}📄 $(basename "$log_file"):${NC}"
                echo "$errors" | sed 's/^/   /'
                error_count=$((error_count + 1))
            fi
        done
        
        # Show log structure
        echo -e "\n${BLUE}📁 Available Log Files:${NC}"
        find "$log_dir" -type f -name "*.txt" | head -10 | while read -r log_file; do
            local size=$(wc -l < "$log_file" 2>/dev/null || echo "?")
            echo "📄 $(basename "$log_file") (${size} lines)"
        done
    else
        echo -e "${YELLOW}⚠️  Could not download logs (may still be running)${NC}"
        
        # Try to get live logs with error filtering
        echo -e "\n${BLUE}📖 Live Log Preview (errors/warnings):${NC}"
        echo "========================================"
        if gh run view "$run_id" --log 2>/dev/null | grep -i "error\|failed\|exception\|warning" | head -10; then
            echo -e "${GREEN}✅ Error preview displayed above${NC}"
        else
            echo -e "${CYAN}ℹ️  No obvious errors in live logs${NC}"
        fi
    fi
    
    # Provide actionable links and suggestions
    echo -e "\n${BLUE}🔗 Resources:${NC}"
    echo "============="
    echo "   🌐 View full logs: https://github.com/$(gh repo view --json owner,name --jq '.owner.login + "/" + .name')/actions/runs/$run_id"
    echo "   📁 Local logs: $log_dir"
    
    # Suggest related PRs if this was a PR workflow
    local branch=$(gh run view "$run_id" --json headBranch --jq '.headBranch')
    if [[ -n "$branch" && "$branch" != "main" ]]; then
        echo "   🔀 Related PR: gh pr list --head $branch"
    fi
}

# Enhanced failed logs analysis with PR correlation
surface_failed_logs() {
    echo -e "\n${RED}🚨 Failed Workflow Analysis${NC}"
    echo "============================"
    
    # Get recent failed runs with enhanced analysis
    local failed_runs=$(gh run list --status failure --limit 5 --json databaseId,workflowName,headBranch,conclusion,createdAt)
    
    echo "$failed_runs" | jq -r '.[] | "\(.databaseId) | \(.workflowName) | \(.headBranch) | \(.createdAt)"' | \
        while IFS='|' read -r run_id workflow_name branch created; do
            echo -e "\n${RED}❌ Failed: ${workflow_name} on ${branch}${NC}"
            echo -e "   🕐 Created: ${created}"
            
            # Check if this is related to a monitored PR
            for pr in "${MONITORED_PRS[@]}"; do
                if gh pr view "$pr" --json headRefName 2>/dev/null | jq -e ".headRefName == \"$branch\"" >/dev/null; then
                    echo -e "   ${PURPLE}🔀 Related to monitored PR #${pr}${NC}"
                    break
                fi
            done
            
            # Surface logs with analysis
            surface_logs "$run_id" "$workflow_name"
            echo -e "\n$(printf '=%.0s' {1..80})"
        done
}

# =============================================================================
# ENHANCED WORKFLOW OPERATIONS
# =============================================================================

# Kick workflows for specific PRs
kick_pr_workflows() {
    local target_pr="$1"
    
    if [[ -z "$target_pr" ]]; then
        echo -e "${YELLOW}Available PRs for workflow kicking:${NC}"
        for pr in "${MONITORED_PRS[@]}"; do
            if gh pr view "$pr" --json state,title,headRefName 2>/dev/null | jq -e '.state == "OPEN"' >/dev/null; then
                local pr_info=$(gh pr view "$pr" --json title,headRefName)
                local title=$(echo "$pr_info" | jq -r '.title' | cut -c1-30)
                local branch=$(echo "$pr_info" | jq -r '.headRefName')
                echo -e "  ${PURPLE}#${pr}${NC}: ${title}... (${branch})"
            fi
        done
        return 0
    fi
    
    echo -e "\n${PURPLE}🔀 Kicking workflows for PR #${target_pr}${NC}"
    
    # Get PR branch
    local branch=$(gh pr view "$target_pr" --json headRefName --jq '.headRefName' 2>/dev/null)
    if [[ -z "$branch" ]]; then
        echo -e "${RED}❌ Could not find PR #${target_pr}${NC}"
        return 1
    fi
    
    echo -e "🌿 Branch: ${branch}"
    
    # Trigger workflows on the PR branch
    for workflow in "${WORKFLOWS[@]}"; do
        local name="${workflow%%:*}"
        local file="${workflow##*:}"
        echo -e "\n🚀 Triggering ${name} for PR #${target_pr}..."
        trigger_workflow "$name" "$file" "$branch"
    done
}

# Create GitHub issue for workflow failures
create_workflow_issue() {
    local run_id="$1"
    local workflow_name="$2"
    
    if [[ -z "$run_id" || -z "$workflow_name" ]]; then
        echo -e "${RED}Usage: create_workflow_issue <run_id> <workflow_name>${NC}"
        return 1
    fi
    
    echo -e "\n${CYAN}🐛 Creating GitHub issue for failed workflow${NC}"
    
    # Gather failure information
    local run_info=$(gh run view "$run_id" --json conclusion,headBranch,createdAt,jobs)
    local branch=$(echo "$run_info" | jq -r '.headBranch')
    local created=$(echo "$run_info" | jq -r '.createdAt')
    local failed_jobs=$(echo "$run_info" | jq -r '[.jobs[] | select(.conclusion == "failure") | .name] | join(", ")')
    
    # Create issue title and body
    local title="🚨 Workflow Failure: ${workflow_name} on ${branch}"
    local body="## Workflow Failure Report

**Workflow:** ${workflow_name}
**Branch:** ${branch}
**Run ID:** ${run_id}
**Created:** ${created}
**Failed Jobs:** ${failed_jobs}

**Run URL:** https://github.com/$(gh repo view --json owner,name --jq '.owner.login + "/" + .name')/actions/runs/${run_id}

### Next Steps
- [ ] Review failure logs
- [ ] Identify root cause
- [ ] Apply fix
- [ ] Re-run workflow

**Labels:** workflow, ci, automation, bug"

    # Create the issue
    if gh issue create --title "$title" --body "$body" --label "workflow,ci,automation,bug"; then
        echo -e "${GREEN}✅ GitHub issue created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create GitHub issue${NC}"
    fi
}

# =============================================================================
# MAIN COMMAND INTERFACE
# =============================================================================

case "${1:-menu}" in
    "status"|"st")
        show_workflow_status
        ;;
    "trigger"|"t")
        if [[ -n "$2" ]]; then
            # Find and trigger specific workflow
            for workflow in "${WORKFLOWS[@]}"; do
                name="${workflow%%:*}"
                file="${workflow##*:}"
                if [[ "$name" == "$2" ]] || [[ "$file" == "$2" ]]; then
                    trigger_workflow "$name" "$file" "$3"
                    exit 0
                fi
            done
            echo -e "${RED}❌ Workflow not found: $2${NC}"
            exit 1
        else
            echo -e "${YELLOW}Available workflows:${NC}"
            for workflow in "${WORKFLOWS[@]}"; do
                name="${workflow%%:*}"
                echo "  - $name"
            done
        fi
        ;;
    "logs"|"l")
        if [[ -n "$2" ]]; then
            surface_logs "$2" "Manual Log Request"
        else
            echo -e "${YELLOW}Usage: $0 logs <run_id>${NC}"
            echo "Recent runs:"
            gh run list --limit 10 --json databaseId,workflowName,status,conclusion | \
                jq -r '.[] | "\(.databaseId) - \(.workflowName) (\(.status)/\(.conclusion // "N/A"))"'
        fi
        ;;
    "failed"|"f")
        surface_failed_logs
        ;;
    "kick-all"|"ka")
        echo -e "${BLUE}🚀 Kicking all available workflows${NC}"
        for workflow in "${WORKFLOWS[@]}"; do
            name="${workflow%%:*}"
            file="${workflow##*:}"
            trigger_workflow "$name" "$file"
            sleep 2  # Prevent rate limiting
        done
        ;;
    "kick-pr"|"kpr")
        kick_pr_workflows "$2"
        ;;
    "issue"|"i")
        if [[ -n "$2" && -n "$3" ]]; then
            create_workflow_issue "$2" "$3"
        else
            echo -e "${YELLOW}Usage: $0 issue <run_id> <workflow_name>${NC}"
            echo "Recent failed runs:"
            gh run list --status failure --limit 5 --json databaseId,workflowName | \
                jq -r '.[] | "\(.databaseId) \(.workflowName)"'
        fi
        ;;
    "monitor"|"m")
        echo -e "${BLUE}📡 Starting enhanced workflow monitor (Ctrl+C to stop)${NC}"
        while true; do
            clear
            show_workflow_status
            echo -e "\n${YELLOW}🔄 Refreshing in 30s... (Ctrl+C to stop)${NC}"
            echo -e "${CYAN}💡 Tip: Use 'kick-pr <number>' to target specific PRs${NC}"
            sleep 30
        done
        ;;
    "help"|"h"|*)
        echo -e "${BLUE}🔧 Legion Workflow Manager (Enhanced)${NC}"
        echo "======================================"
        echo "Usage: $0 <command> [options]"
        echo ""
        echo -e "${GREEN}Core Commands:${NC}"
        echo "  status  (st)     - Show workflow status + PRs + issues"
        echo "  trigger (t)      - Manually trigger workflow [branch]"
        echo "  logs    (l)      - Surface logs for specific run"
        echo "  failed  (f)      - Analyze recent failed workflows"
        echo ""
        echo -e "${PURPLE}PR Commands:${NC}"
        echo "  kick-pr (kpr)    - Kick workflows for specific PR"
        echo ""
        echo -e "${CYAN}Issue Commands:${NC}"
        echo "  issue   (i)      - Create GitHub issue for failure"
        echo ""
        echo -e "${YELLOW}Bulk Commands:${NC}"
        echo "  kick-all (ka)    - Trigger all available workflows"
        echo "  monitor  (m)     - Real-time monitoring dashboard"
        echo ""
        echo -e "${BLUE}Examples:${NC}"
        echo "  $0 kick-pr 98           # Kick workflows for PR #98"
        echo "  $0 trigger CI main      # Trigger CI on main branch"
        echo "  $0 issue 123456 'CI'    # Create issue for failed run"
        echo ""
        show_workflow_status
        ;;
esac 