#!/usr/bin/env bash

# Script to watch CI checks for a PR, merge if green, or comment if red.

# PR Number is hardcoded to 3 for this specific task.
# In a more generic script, this could be an argument.
PR_NUMBER=3

echo "Watching CI checks for PR #${PR_NUMBER}..."
gh pr checks ${PR_NUMBER} --watch --exit-status
status=$?

if [ "$status" -eq 0 ]; then
  echo "✅ All CI checks passed for PR #${PR_NUMBER}."
  echo "Attempting to merge PR #${PR_NUMBER}..."
  gh pr merge ${PR_NUMBER} --merge --delete-branch --subject "merge: Sprint 0 port-allocator bootstrap"
  merge_status=$?

  if [ "$merge_status" -eq 0 ]; then
    echo "PR #${PR_NUMBER} merged successfully."
    # It's better to post comments *before* deleting the branch if the comment is on the PR itself.
    # However, the original script had it after. For now, following the script.
    # Consider if gh pr comment works as expected after branch deletion.
    gh pr comment ${PR_NUMBER} --body "✅ CI green & merged by automation. Posted metrics & agent-feed updates."

    echo "Running post-merge follow-ups..."
    # Regenerate coverage badge & lint summary
    echo "Running: pytest --cov=legion --cov-report=term-missing -q"
    pytest --cov=legion --cov-report=term-missing -q
    echo "Running: ruff check ."
    ruff check .

    # Drop summary to metrics channel (use your existing Discord webhook script)
    echo "Running: ./scripts/post_metrics.sh"
    ./scripts/post_metrics.sh
    echo "Running: ./scripts/post_agent_feed.sh \\"merge: Sprint 0 port-allocator bootstrap\\""
    ./scripts/post_agent_feed.sh "merge: Sprint 0 port-allocator bootstrap"
    echo "Post-merge follow-ups complete."
  else
    echo "❌ Failed to merge PR #${PR_NUMBER}. Status: ${merge_status}"
    gh pr comment ${PR_NUMBER} --body "❌ CI green, but merge failed. Manual intervention required. Merge command status: ${merge_status}"
  fi
else
  echo "❌ Some CI checks failed for PR #${PR_NUMBER}."
  # Grab first failing job, ensuring it handles cases where no checks are found or jq isn't installed.
  first_fail=$(gh pr checks ${PR_NUMBER} --limit 1 --json name,url,outcome,conclusion | jq -r '.[] | select(.conclusion=="failure") | "\(.name) (\(.conclusion)): \(.url)"' || echo "Could not retrieve failing job details.")
  gh pr comment ${PR_NUMBER} --body "❌ CI red. First failing job details (if available):
\`\`\`
${first_fail}
\`\`\`"
  echo "Commented on PR #${PR_NUMBER} with failure details."
fi
