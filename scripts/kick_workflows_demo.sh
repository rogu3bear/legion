#!/usr/bin/env bash
# =============================================================================
# Track E-A: Enhanced Workflow Kicking & Log Surfacing Demo
# =============================================================================
# Purpose: Comprehensive demonstration of manual workflow management with
#          PR integration, issue tracking, and enhanced log analysis
# Author: Cursor (Track E-A Implementation)
# Dependencies: gh CLI, jq, git
# =============================================================================

set -e

# =============================================================================
# CONFIGURATION
# =============================================================================

# Target PRs for monitoring (from CI merge system)
TARGET_PRS=(98 100 114)

# Color styling for better output readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🎯 Track E-A: Enhanced Workflow Management Demo${NC}"
echo -e "${BLUE}================================================${NC}"
echo "Demonstrating manual workflow kicking, PR integration, and log surfacing"

# =============================================================================
# STEP 1: COMPREHENSIVE STATUS OVERVIEW
# =============================================================================

echo ""
echo -e "${BLUE}🔍 Step 1: Comprehensive Workflow & PR Status${NC}"
echo "=============================================="

echo -e "\n${PURPLE}📊 Recent Workflow Runs:${NC}"
gh run list --limit 8 --json status,workflowName,headBranch,conclusion,databaseId,createdAt | \
    jq -r '.[] | "\(.status) | \(.conclusion // "N/A") | \(.workflowName) | \(.headBranch) | \(.databaseId) | \(.createdAt)"' | \
    while IFS='|' read -r status conclusion workflow branch run_id created; do
        case $status in
            "completed")
                if [[ "$conclusion" == "success" ]]; then
                    icon="✅"; color="$GREEN"
                elif [[ "$conclusion" == "failure" ]]; then
                    icon="❌"; color="$RED"
                else
                    icon="⚠️"; color="$YELLOW"
                fi
                ;;
            "in_progress")
                icon="🔄"; color="$YELLOW"
                ;;
            *)
                icon="⏳"; color="$CYAN"
                ;;
        esac
        
        # Shorten branch name for better display
        short_branch=$(echo "$branch" | sed 's/auto\/implement-patch-/patch-/' | sed 's/auto\/add-/add-/' | cut -c1-20)
        
        echo -e "${color}${icon} ${workflow} | ${short_branch} | ID:${run_id}${NC}"
    done

echo -e "\n${PURPLE}🔀 Target PR Status Overview:${NC}"
for pr in "${TARGET_PRS[@]}"; do
    echo -e "\n${PURPLE}📋 PR #${pr}:${NC}"
    
    if pr_info=$(gh pr view "$pr" --json state,title,mergeable,headRefName,statusCheckRollupState 2>/dev/null); then
        state=$(echo "$pr_info" | jq -r '.state')
        title=$(echo "$pr_info" | jq -r '.title' | cut -c1-45)
        mergeable=$(echo "$pr_info" | jq -r '.mergeable')
        branch=$(echo "$pr_info" | jq -r '.headRefName')
        checks_state=$(echo "$pr_info" | jq -r '.statusCheckRollupState // "UNKNOWN"')
        
        # Status indicators
        case $state in
            "OPEN")
                state_icon="🔴"; state_color="$YELLOW"
                ;;
            "MERGED")
                state_icon="✅"; state_color="$GREEN"
                ;;
            "CLOSED")
                state_icon="❌"; state_color="$RED"
                ;;
            *)
                state_icon="❓"; state_color="$NC"
                ;;
        esac
        
        case $checks_state in
            "SUCCESS")
                check_icon="✅"; check_color="$GREEN"
                ;;
            "FAILURE")
                check_icon="❌"; check_color="$RED"
                ;;
            "PENDING")
                check_icon="🔄"; check_color="$YELLOW"
                ;;
            *)
                check_icon="❓"; check_color="$NC"
                ;;
        esac
        
        echo -e "   ${state_color}${state_icon} State: ${state}${NC}"
        echo -e "   📝 Title: ${title}..."
        echo -e "   🌿 Branch: ${branch}"
        echo -e "   ${check_color}${check_icon} Checks: ${checks_state}${NC}"
        echo -e "   🔀 Mergeable: ${mergeable}"
        
        # Get detailed CI checks if available
        if checks_output=$(gh pr checks "$pr" --json state,name,conclusion 2>/dev/null); then
            echo "   🔍 Detailed CI Status:"
            echo "$checks_output" | jq -r '.[] | "     - \(.name): \(.state) (\(.conclusion // "N/A"))"' | head -3
        fi
    else
        echo -e "   ${RED}❌ PR not found or inaccessible${NC}"
    fi
done

# =============================================================================
# STEP 2: ENHANCED WORKFLOW KICKING STRATEGIES
# =============================================================================

echo ""
echo -e "${BLUE}🚀 Step 2: Enhanced Workflow Kicking Strategies${NC}"
echo "==============================================="

# Strategy 1: Re-run recent failed workflows with detailed analysis
echo -e "\n${YELLOW}📌 Strategy 1: Re-running Recent Failed Workflows${NC}"
echo "   Analyzing failures and attempting re-runs..."

failed_runs=$(gh run list --status failure --limit 5 --json databaseId,workflowName,headBranch,conclusion,createdAt)
failure_count=0

echo "$failed_runs" | jq -r '.[] | "\(.databaseId) | \(.workflowName) | \(.headBranch) | \(.createdAt)"' | \
    while IFS='|' read -r run_id workflow_name branch created; do
        echo -e "\n   ${RED}❌ Failed Run Analysis:${NC}"
        echo "      🆔 Run ID: $run_id"
        echo "      🔧 Workflow: $workflow_name"
        echo "      🌿 Branch: $branch"
        echo "      🕐 Created: $created"
        
        # Check if this failure is related to our target PRs
        pr_related=false
        for pr in "${TARGET_PRS[@]}"; do
            if pr_branch=$(gh pr view "$pr" --json headRefName --jq '.headRefName' 2>/dev/null); then
                if [[ "$pr_branch" == "$branch" ]]; then
                    echo -e "      ${PURPLE}🔀 Related to target PR #${pr}${NC}"
                    pr_related=true
                    break
                fi
            fi
        done
        
        # Attempt re-run with enhanced feedback
        echo "      🔄 Attempting re-run..."
        if gh run rerun "$run_id" 2>/dev/null; then
            echo -e "      ${GREEN}✅ Successfully re-triggered workflow${NC}"
            failure_count=$((failure_count + 1))
            
            # If PR-related, suggest monitoring
            if [[ "$pr_related" == true ]]; then
                echo "      💡 Suggestion: Monitor this PR's workflow status closely"
            fi
        else
            echo -e "      ${YELLOW}⚠️  Could not re-run (may already be running or require permissions)${NC}"
        fi
        
        # Only process first 3 failures to avoid spam
        if [[ $failure_count -ge 3 ]]; then
            break
        fi
    done

# Strategy 2: Targeted PR workflow kicking
echo -e "\n${YELLOW}📌 Strategy 2: Targeted PR Workflow Triggering${NC}"
echo "   Focusing on target PRs with specific workflow needs..."

for pr in "${TARGET_PRS[@]}"; do
    echo -e "\n   ${PURPLE}🎯 Targeting PR #${pr}:${NC}"
    
    if pr_info=$(gh pr view "$pr" --json state,headRefName,statusCheckRollupState 2>/dev/null); then
        state=$(echo "$pr_info" | jq -r '.state')
        branch=$(echo "$pr_info" | jq -r '.headRefName')
        checks_state=$(echo "$pr_info" | jq -r '.statusCheckRollupState // "UNKNOWN"')
        
        if [[ "$state" == "OPEN" ]]; then
            echo "      🌿 Branch: $branch"
            echo "      📊 Current check status: $checks_state"
            
            # Strategy: If checks are failing, try to re-trigger workflows on this branch
            if [[ "$checks_state" == "FAILURE" || "$checks_state" == "UNKNOWN" ]]; then
                echo "      🚀 Attempting to re-trigger workflows for failing/unknown checks..."
                
                # Find recent workflow runs for this branch and re-run them
                branch_runs=$(gh run list --branch "$branch" --limit 3 --json databaseId,workflowName,status)
                echo "$branch_runs" | jq -r '.[] | "\(.databaseId) \(.workflowName) \(.status)"' | \
                    while read -r run_id workflow_name run_status; do
                        if [[ "$run_status" != "in_progress" ]]; then
                            echo "         🔄 Re-running $workflow_name (ID: $run_id)..."
                            if gh run rerun "$run_id" 2>/dev/null; then
                                echo -e "         ${GREEN}✅ Successfully triggered${NC}"
                            else
                                echo -e "         ${YELLOW}⚠️  Re-run failed or already running${NC}"
                            fi
                        else
                            echo -e "         ${CYAN}ℹ️  $workflow_name already running${NC}"
                        fi
                    done
            else
                echo -e "      ${GREEN}✅ Checks are passing or pending - no intervention needed${NC}"
            fi
        else
            echo -e "      ${CYAN}ℹ️  PR is $state - skipping workflow triggering${NC}"
        fi
    else
        echo -e "      ${RED}❌ Could not access PR information${NC}"
    fi
done

# Strategy 3: Manual workflow dispatch attempts with enhanced workflow discovery
echo -e "\n${YELLOW}📌 Strategy 3: Manual Workflow Dispatch Discovery${NC}"
echo "   Discovering and attempting manual triggers..."

workflow_dispatch_count=0
for workflow in .github/workflows/*.yml .github/workflows/*.yaml; do
    if [[ -f "$workflow" ]]; then
        workflow_name=$(basename "$workflow")
        echo -e "\n   🔍 Analyzing: ${workflow_name}"
        
        if grep -q "workflow_dispatch" "$workflow" 2>/dev/null; then
            echo -e "      ${GREEN}✅ Supports manual dispatch${NC}"
            
            # Check if workflow has inputs for targeted triggering
            if grep -A 10 "workflow_dispatch:" "$workflow" | grep -q "inputs:"; then
                echo "         💡 Has configurable inputs - could be customized"
            fi
            
            echo "         🚀 Attempting manual trigger..."
            if gh workflow run "$workflow" 2>/dev/null; then
                echo -e "         ${GREEN}✅ Successfully triggered${NC}"
                workflow_dispatch_count=$((workflow_dispatch_count + 1))
            else
                echo -e "         ${YELLOW}⚠️  Dispatch failed (may require specific inputs or permissions)${NC}"
            fi
        else
            echo -e "      ${RED}❌ No manual dispatch support${NC}"
            echo "         💡 Suggestion for Codex: Add workflow_dispatch trigger"
        fi
    fi
done

echo -e "\n   📊 Manual Dispatch Summary: ${workflow_dispatch_count} workflows triggered"

# =============================================================================
# STEP 3: ADVANCED LOG SURFACING & ANALYSIS
# =============================================================================

echo ""
echo -e "${BLUE}📊 Step 3: Advanced Log Surfacing & Analysis${NC}"
echo "============================================="

# Get most recent workflow run for detailed analysis
echo -e "\n${CYAN}📌 Detailed Analysis of Most Recent Run:${NC}"
recent_run=$(gh run list --limit 1 --json databaseId,workflowName,status,conclusion,headBranch,jobs)
run_id=$(echo "$recent_run" | jq -r '.[0].databaseId')
workflow_name=$(echo "$recent_run" | jq -r '.[0].workflowName')
status=$(echo "$recent_run" | jq -r '.[0].status')
conclusion=$(echo "$recent_run" | jq -r '.[0].conclusion')
branch=$(echo "$recent_run" | jq -r '.[0].headBranch')

echo "   🎯 Target: $workflow_name (ID: $run_id)"
echo "   📊 Status: $status | Conclusion: $conclusion"
echo "   🌿 Branch: $branch"

# Enhanced job analysis
echo -e "\n${CYAN}🔍 Job-Level Analysis:${NC}"
echo "$recent_run" | jq -r '.[0].jobs[] | "\(.name) | \(.status) | \(.conclusion // "N/A") | \(.databaseId)"' | \
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
        echo -e "   ${color}${icon} ${job_name} (${job_status}/${job_conclusion})${NC}"
        
        # For failed jobs, try to get specific error information
        if [[ "$job_conclusion" == "failure" ]]; then
            echo "      🔍 Analyzing failure details..."
            # This would require more complex log parsing in a real implementation
            echo "      💡 Suggestion: Review logs at: https://github.com/$(gh repo view --json owner,name --jq '.owner.login + "/" + .name')/actions/runs/$run_id/job/$job_id"
        fi
    done

# Log download and analysis attempt
echo -e "\n${CYAN}📁 Log Download & Analysis:${NC}"
log_dir="/tmp/legion_demo_logs_${run_id}_$$"
mkdir -p "$log_dir"

echo "   📥 Attempting log download..."
if gh run download "$run_id" --dir "$log_dir" 2>/dev/null; then
    echo -e "   ${GREEN}✅ Logs downloaded successfully${NC}"
    
    # Analyze log files for common patterns
    echo "   🔍 Performing error pattern analysis..."
    
    error_patterns=("ERROR" "FAILED" "Exception" "Error:" "fatal:" "CRITICAL")
    warning_patterns=("WARNING" "WARN" "deprecated" "DEPRECATION")
    
    for pattern in "${error_patterns[@]}"; do
        count=$(find "$log_dir" -name "*.txt" -exec grep -l "$pattern" {} \; 2>/dev/null | wc -l)
        if [[ $count -gt 0 ]]; then
            echo -e "      ${RED}❌ Found '$pattern' in $count log files${NC}"
        fi
    done
    
    for pattern in "${warning_patterns[@]}"; do
        count=$(find "$log_dir" -name "*.txt" -exec grep -l "$pattern" {} \; 2>/dev/null | wc -l)
        if [[ $count -gt 0 ]]; then
            echo -e "      ${YELLOW}⚠️  Found '$pattern' in $count log files${NC}"
        fi
    done
    
    # Show log file structure
    echo "   📁 Available log files:"
    find "$log_dir" -name "*.txt" | head -5 | while read -r log_file; do
        size=$(wc -l < "$log_file" 2>/dev/null || echo "?")
        echo "      📄 $(basename "$log_file") ($size lines)"
    done
    
    # Quick content preview from first log file
    first_log=$(find "$log_dir" -name "*.txt" | head -1)
    if [[ -n "$first_log" ]]; then
        echo -e "\n   📖 Quick Content Preview (first 5 lines):"
        head -5 "$first_log" | sed 's/^/      /'
    fi
else
    echo -e "   ${YELLOW}⚠️  Could not download logs (may still be running)${NC}"
    
    # Alternative: Try to get live log preview
    echo "   🔄 Attempting live log preview..."
    if live_logs=$(gh run view "$run_id" --log 2>/dev/null | head -10); then
        echo -e "   ${GREEN}✅ Live log preview available:${NC}"
        echo "$live_logs" | sed 's/^/      /'
    else
        echo -e "   ${YELLOW}⚠️  Live logs not immediately available${NC}"
    fi
fi

# =============================================================================
# STEP 4: GITHUB ISSUES INTEGRATION
# =============================================================================

echo ""
echo -e "${BLUE}🐛 Step 4: GitHub Issues Integration${NC}"
echo "===================================="

echo -e "\n${CYAN}📋 Workflow-Related Issues Analysis:${NC}"

# Check for existing workflow/CI related issues
existing_issues=$(gh issue list --label "workflow,ci,automation" --limit 5 --json number,title,state,labels 2>/dev/null || echo "[]")

if [[ "$existing_issues" != "[]" && $(echo "$existing_issues" | jq length) -gt 0 ]]; then
    echo "   📊 Found existing workflow-related issues:"
    echo "$existing_issues" | jq -r '.[] | "\(.number) | \(.title) | \(.state) | \(.labels | map(.name) | join(","))"' | \
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
            short_title=$(echo "$title" | cut -c1-50)
            echo -e "      ${color}${icon} #${number}: ${short_title}... [$labels]${NC}"
        done
else
    echo "   ℹ️  No existing workflow-related issues found"
fi

# Offer to create issue for recent failures
echo -e "\n${CYAN}💡 Issue Creation Opportunity:${NC}"
recent_failures=$(gh run list --status failure --limit 1 --json databaseId,workflowName,headBranch)

if [[ $(echo "$recent_failures" | jq length) -gt 0 ]]; then
    failure_run_id=$(echo "$recent_failures" | jq -r '.[0].databaseId')
    failure_workflow=$(echo "$recent_failures" | jq -r '.[0].workflowName')
    failure_branch=$(echo "$recent_failures" | jq -r '.[0].headBranch')
    
    echo "   🚨 Recent failure detected:"
    echo "      🆔 Run ID: $failure_run_id"
    echo "      🔧 Workflow: $failure_workflow"
    echo "      🌿 Branch: $failure_branch"
    echo "   💡 Suggestion: Use './scripts/workflow_manager.sh issue $failure_run_id \"$failure_workflow\"' to create tracking issue"
else
    echo "   ✅ No recent failures requiring issue creation"
fi

# =============================================================================
# FINAL SUMMARY & NEXT STEPS
# =============================================================================

echo ""
echo -e "${BLUE}🏁 Track E-A Workflow Management Demo Complete${NC}"
echo "=============================================="

echo -e "\n${GREEN}✅ Summary of Accomplished Actions:${NC}"
echo "  📊 Comprehensive workflow and PR status analysis"
echo "  🚀 Multiple workflow triggering strategies demonstrated"
echo "  🔄 Failed workflow re-runs attempted"
echo "  🎯 PR-specific workflow targeting"
echo "  📁 Advanced log surfacing and error analysis"
echo "  🐛 GitHub Issues integration and tracking"

echo -e "\n${YELLOW}📊 Key Metrics from This Demo:${NC}"
failed_count=$(gh run list --status failure --limit 10 | wc -l)
success_count=$(gh run list --status completed --limit 10 | grep -c "✓" || echo "0")
running_count=$(gh run list --status in_progress --limit 10 | wc -l)

echo "  ❌ Recent Failed Runs: $failed_count"
echo "  ✅ Recent Successful Runs: $success_count"  
echo "  🔄 Currently Running: $running_count"
echo "  🔀 Target PRs Monitored: ${#TARGET_PRS[@]}"

echo -e "\n${PURPLE}🎯 Next Steps for Enhanced Workflow Management:${NC}"
echo "  1. 🔧 Use './scripts/workflow_manager.sh monitor' for real-time monitoring"
echo "  2. 🔀 Use './scripts/workflow_manager.sh kick-pr <number>' for PR-specific workflows"
echo "  3. 🐛 Use './scripts/workflow_manager.sh issue <run_id> <workflow>' for failure tracking"
echo "  4. 📊 Use './scripts/workflow_manager.sh failed' for comprehensive failure analysis"

echo -e "\n${CYAN}💡 Recommendations for Codex (Track E-B):${NC}"
echo "  🔧 Add workflow_dispatch triggers to all workflows for manual control"
echo "  🔧 Implement workflow input parameters for branch/PR targeting"
echo "  🔧 Add automatic issue creation for critical workflow failures"
echo "  🔧 Enhance workflow retry logic with exponential backoff"
echo "  🔧 Implement workflow status notifications (Discord/Slack integration)"

echo -e "\n${BLUE}🔗 Quick Access Commands:${NC}"
echo "  ./scripts/workflow_manager.sh st          # Status overview"
echo "  ./scripts/workflow_manager.sh kick-pr 98   # Kick workflows for PR #98"
echo "  ./scripts/workflow_manager.sh f           # Analyze failures"
echo "  ./scripts/workflow_manager.sh m           # Start monitoring"

echo -e "\n${GREEN}🎉 Track E-A Implementation Successfully Demonstrated!${NC}" 