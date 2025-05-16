#!/usr/bin/env bash

# Script to watch CI checks for a PR, merge if green, or comment if red.

# PR Number is hardcoded to 3 for this specific task.
# In a more generic script, this could be an argument.
PR_NUMBER=3

echo "Watching CI checks for PR #${PR_NUMBER}..."
# Watch until all checks complete. We'll determine success/failure by parsing JSON.
gh pr checks ${PR_NUMBER} --watch

# Fetch the final status of all checks
checks_json=$(gh pr checks ${PR_NUMBER} --json name,url,conclusion,state)

# Determine overall status
# If any check is not 'SUCCESS' (and is not 'SKIPPED' or 'NEUTRAL'), consider it a failure.
# Different CI systems might report 'PENDING' or other states if --watch didn't fully wait.
# 'COMPLETED' is a state, 'SUCCESS', 'FAILURE', 'CANCELLED', 'SKIPPED', 'NEUTRAL' are conclusions.

ci_passed=true
first_failing_check_details=""

# Use jq to iterate over checks and find failures or non-success states
# that are not neutral/skipped.
if echo "${checks_json}" | jq -e '.[] | select(.conclusion != "SUCCESS" and .conclusion != "SKIPPED" and .conclusion != "NEUTRAL")' > /dev/null; then
  ci_passed=false
  first_failing_check_details=$(echo "${checks_json}" | jq -r '.[] | select(.conclusion != "SUCCESS" and .conclusion != "SKIPPED" and .conclusion != "NEUTRAL") | "- \(.name) (\(.conclusion)): \(.url)"' | head -n 1)
fi

if ${ci_passed}; then
  echo "✅ All CI checks passed for PR #${PR_NUMBER}."
  echo "Attempting to merge PR #${PR_NUMBER}..."
  gh pr merge ${PR_NUMBER} --merge --delete-branch --subject "merge: Sprint 0 port-allocator bootstrap"
  merge_status=$?

  if [ "$merge_status" -eq 0 ]; then
    echo "PR #${PR_NUMBER} merged successfully."
    gh pr comment ${PR_NUMBER} --body "✅ CI green & merged by automation. Posted metrics & agent-feed updates."
    
    echo "Running post-merge follow-ups..."
    echo "Running: pytest --cov=legion --cov-report=term-missing -q"
    pytest --cov=legion --cov-report=term-missing -q
    echo "Running: ruff check ."
    ruff check .

    echo "Running: ./scripts/post_metrics.sh"
    ./scripts/post_metrics.sh
    echo "Running: ./scripts/post_agent_feed.sh \"merge: Sprint 0 port-allocator bootstrap\""
    ./scripts/post_agent_feed.sh "merge: Sprint 0 port-allocator bootstrap"
    echo "Post-merge follow-ups complete."
  else
    echo "❌ Failed to merge PR #${PR_NUMBER}. Status: ${merge_status}"
    gh pr comment ${PR_NUMBER} --body "❌ CI green, but merge failed. Manual intervention required. Merge command status: ${merge_status}"
  fi
else
  echo "❌ Some CI checks failed for PR #${PR_NUMBER}."
  if [ -z "${first_failing_check_details}" ]; then
    first_failing_check_details="Could not determine specific failing job from JSON output. Please check PR manually."
  fi
  gh pr comment ${PR_NUMBER} --body "❌ CI red. Details of first non-successful check (if available):
\`\`\`
${first_failing_check_details}
\`\`\`"
  echo "Commented on PR #${PR_NUMBER} with failure details."
fi
