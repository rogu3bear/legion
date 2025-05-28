#!/bin/bash
# PR Categorization Script
# Analyzes file changes and assigns priority buckets

echo "=== PR CATEGORIZATION ANALYSIS ==="
echo ""

declare -A pr_categories
declare -A pr_files
declare -A pr_titles

# Read PRs and analyze each one
while IFS=$'\t' read -r num title branch author updated; do
    echo "Analyzing PR #$num: $title"
    
    # Get file changes for this PR
    files=$(git diff --name-only origin/main...origin/$branch 2>/dev/null | head -50)
    pr_files[$num]="$files"
    pr_titles[$num]="$title"
    
    # Categorize based on file patterns
    if [[ "$files" =~ scripts/|\.env\.ports|legion/orchestrator|legion/middleware ]]; then
        category="A-blocking-core"
    elif [[ "$files" =~ ui/frontend ]]; then
        category="B-feature-ui"
    elif [[ "$files" =~ interface/api ]]; then
        category="B-feature-api"  
    elif [[ "$files" =~ docs/|README|\.md$ ]]; then
        category="C-docs-chore"
    elif [[ "$files" =~ test|spec ]]; then
        category="C-docs-chore"
    else
        category="D-experimental"
    fi
    
    pr_categories[$num]="$category"
    echo "  → Files: $(echo $files | tr '\n' ' ')"
    echo "  → Category: $category"
    echo ""
    
done < /tmp/prs.tsv

echo "=== PRIORITY BUCKETS ==="
echo ""

for bucket in "A-blocking-core" "B-feature-ui" "B-feature-api" "C-docs-chore" "D-experimental"; do
    echo "[$bucket]"
    count=0
    for num in "${!pr_categories[@]}"; do
        if [[ "${pr_categories[$num]}" == "$bucket" ]]; then
            echo "  PR #$num: ${pr_titles[$num]}"
            ((count++))
        fi
    done
    echo "  Total: $count PRs"
    echo ""
done 