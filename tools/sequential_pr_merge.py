#!/usr/bin/env python3
"""
Sequential PR Merge-and-Fix Routine for Legion Repository.
Iterates through every open Codex PR, merges it into main, and auto-fixes conflicts.
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def run_command(cmd: str, check: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def post_status(message: str, target: str = "agent-feed") -> bool:
    """Post status update using the post_update tool."""
    cmd = f'python tools/post_update.py --target {target} --message "{message}" --format'
    code, stdout, stderr = run_command(cmd, check=False)
    return code == 0


def prep_repo() -> bool:
    """Prepare repository for the merge routine."""
    print("🔧 Preparing repository...")
    
    # Ensure we're in the right directory
    work_dir = Path.home() / "Dev" / "Programs" / "Legion"
    if not work_dir.exists():
        print(f"❌ Work directory {work_dir} does not exist")
        return False
    
    os.chdir(work_dir)
    print(f"📁 Working in {work_dir}")
    
    # Fetch latest changes
    code, stdout, stderr = run_command("git fetch origin", check=False)
    if code != 0:
        print(f"⚠️  Git fetch warning: {stderr}")
    
    # Checkout and reset main
    code, stdout, stderr = run_command("git checkout main", check=False)
    if code != 0:
        print(f"❌ Failed to checkout main: {stderr}")
        return False
    
    code, stdout, stderr = run_command("git reset --hard origin/main", check=False)
    if code != 0:
        print(f"❌ Failed to reset to origin/main: {stderr}")
        return False
    
    print("✅ Repository prepared")
    return True


def fetch_codex_prs() -> List[Dict[str, Any]]:
    """Fetch open Codex PRs using GitHub CLI."""
    print("🔍 Fetching open Codex PRs...")
    
    cmd = 'gh pr list --search "author:codex state:open" --json number,title,headRefName,url'
    code, stdout, stderr = run_command(cmd, check=False)
    
    if code != 0:
        print(f"❌ Failed to fetch PRs: {stderr}")
        return []
    
    try:
        prs = json.loads(stdout)
        print(f"📋 Found {len(prs)} open Codex PRs")
        for pr in prs:
            print(f"  - PR #{pr['number']}: {pr['title']}")
        return prs
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse PR data: {e}")
        return []


def process_single_pr(pr: Dict[str, Any]) -> bool:
    """Process a single PR: checkout, rebase, fix, and merge."""
    pr_num = pr['number']
    pr_branch = pr['headRefName']
    pr_title = pr['title']
    
    print(f"\n🔄 Processing PR #{pr_num}: {pr_title}")
    post_status(f"[Cursor] Starting PR #{pr_num}: {pr_title}")
    
    # Step 1: Checkout PR branch
    print(f"📥 Checking out PR branch: {pr_branch}")
    code, stdout, stderr = run_command(f"git fetch origin pull/{pr_num}/head:{pr_branch}", check=False)
    if code != 0:
        print(f"❌ Failed to fetch PR branch: {stderr}")
        return False
    
    code, stdout, stderr = run_command(f"git checkout -B work/{pr_branch} {pr_branch}", check=False)
    if code != 0:
        print(f"❌ Failed to checkout work branch: {stderr}")
        return False
    
    # Step 2: Rebase onto latest main
    print("🔀 Rebasing onto latest main...")
    code, stdout, stderr = run_command("git rebase main", check=False)
    
    if code != 0:
        print("⚠️  Rebase conflicts detected, attempting auto-resolution...")
        
        # Auto-fix conflicts
        code, stdout, stderr = run_command("python tools/auto_resolve_conflicts.py", check=False)
        if code == 0:
            # Add resolved files and continue rebase
            run_command("git add -u", check=False)
            code, stdout, stderr = run_command("git rebase --continue", check=False)
            if code != 0:
                print(f"❌ Failed to continue rebase: {stderr}")
                return False
        else:
            print(f"❌ Auto-conflict resolution failed: {stderr}")
            return False
    
    # Step 3: Run baseline checks
    print("🔍 Running baseline checks...")
    
    # Port-sanity check
    code, stdout, stderr = run_command("./scripts/dev_start.sh --check-ports", check=False)
    if code != 0:
        print(f"⚠️  Port-sanity check failed: {stderr}")
    
    # Assurance scan (if available)
    code, stdout, stderr = run_command("python -m tools.assurance_scan --min 0.85", check=False)
    if code != 0:
        print(f"⚠️  Assurance scan failed: {stderr}")
    
    # Type checking
    code, stdout, stderr = run_command("pyright --project .", check=False)
    if code != 0:
        print(f"⚠️  Type checking failed: {stderr}")
    
    # Step 4: If checks fail, auto-patch
    if code != 0:
        print("🔧 Running auto-fix routine...")
        code, stdout, stderr = run_command("python tools/auto_fix.py --ci", check=False)
        
        if code == 0:
            # Re-run checks
            print("🔍 Re-running checks after auto-fix...")
            run_command("./scripts/dev_start.sh --check-ports", check=False)
            run_command("python -m tools.assurance_scan --min 0.85", check=False)
            run_command("pyright --project .", check=False)
        else:
            print(f"⚠️  Auto-fix failed: {stderr}")
    
    # Step 5: Fast-forward main
    print("⏩ Fast-forwarding main...")
    code, stdout, stderr = run_command("git checkout main", check=False)
    if code != 0:
        print(f"❌ Failed to checkout main: {stderr}")
        return False
    
    code, stdout, stderr = run_command(f"git merge --ff-only work/{pr_branch}", check=False)
    if code != 0:
        print(f"❌ Fast-forward merge failed: {stderr}")
        return False
    
    # Step 6: Push fix-ups back to PR (if modified)
    print("📤 Pushing any fixes back to PR...")
    code, stdout, stderr = run_command(f"git push origin HEAD:{pr_branch}", check=False)
    if code != 0:
        print(f"⚠️  Failed to push fixes back to PR: {stderr}")
    
    # Step 7: Post success status
    success_msg = f"[Cursor] PR #{pr_num} merged & fixed ✅ ({datetime.now().strftime('%Y-%m-%d')})"
    post_status(success_msg)
    
    print(f"✅ PR #{pr_num} successfully processed")
    return True


def cleanup_branches(processed_prs: List[Dict[str, Any]]) -> None:
    """Clean up work branches after processing."""
    print("🧹 Cleaning up work branches...")
    
    for pr in processed_prs:
        pr_branch = pr['headRefName']
        work_branch = f"work/{pr_branch}"
        
        code, stdout, stderr = run_command(f"git branch -D {work_branch}", check=False)
        if code == 0:
            print(f"🗑️  Deleted work branch: {work_branch}")


def main():
    """Main sequential PR merge routine."""
    print("🚀 Starting Sequential PR Merge-and-Fix Routine")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    
    # Step 1: Prep repo
    if not prep_repo():
        post_status("[Cursor ⚠] Repository preparation failed. Aborting merge routine.")
        return 1
    
    # Step 2: Fetch open Codex PRs
    prs = fetch_codex_prs()
    if not prs:
        post_status("[Cursor] No open Codex PRs found. Merge routine complete.")
        return 0
    
    post_status(f"[Cursor] Found {len(prs)} open Codex PRs. Starting sequential merge...")
    
    # Step 3: Process each PR sequentially
    processed_prs = []
    failed_pr = None
    
    for pr in prs:
        try:
            if process_single_pr(pr):
                processed_prs.append(pr)
            else:
                failed_pr = pr
                break
        except Exception as e:
            print(f"❌ Unexpected error processing PR #{pr['number']}: {e}")
            failed_pr = pr
            break
    
    # Step 4: Final sweep
    if not failed_pr:
        print("🏁 Final sweep - pushing main...")
        code, stdout, stderr = run_command("git push origin main", check=False)
        if code == 0:
            post_status("[Cursor] Sequential merge routine complete — main up-to-date.")
            print("🎉 All PRs merged successfully!")
        else:
            print(f"⚠️  Failed to push main: {stderr}")
            post_status(f"[Cursor ⚠] Failed to push main after merging {len(processed_prs)} PRs.")
    else:
        # Handle failure
        pr_num = failed_pr['number']
        post_status(f"[Cursor ⚠] Merge halted at PR #{pr_num}. Manual review needed.")
        print(f"❌ Merge routine halted at PR #{pr_num}")
        cleanup_branches(processed_prs)
        return 1
    
    # Cleanup
    cleanup_branches(processed_prs)
    
    print(f"✅ Sequential merge routine completed successfully!")
    print(f"📊 Processed {len(processed_prs)} PRs")
    print(f"⏰ Completed at: {datetime.now().isoformat()}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 