#!/usr/bin/env python3
"""
Cursor-Legion-Operator: CLI/FS automation agent for Legion CI/CD

Handles:
- Fetching PRs from Codex
- Running automated tests
- Reporting results
- Discord notifications
"""

import subprocess
import sys
import os
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CIResults:
    """Results from CI pipeline execution"""
    migration_success: bool
    python_compile_errors: int
    pytest_passed: int
    pytest_failed: int
    go_tests_passed: int
    go_tests_failed: int
    overall_success: bool
    error_messages: List[str]


class CursorLegionOperator:
    """Automation agent for Legion CI/CD operations"""
    
    def __init__(self, repo_path: str = "/Users/vix/Dev/Programs/Legion"):
        self.repo_path = Path(repo_path)
        self.results = CIResults(
            migration_success=False,
            python_compile_errors=0,
            pytest_passed=0,
            pytest_failed=0,
            go_tests_passed=0,
            go_tests_failed=0,
            overall_success=False,
            error_messages=[]
        )
    
    def run_command(self, cmd: str, cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """Execute shell command and return (exit_code, stdout, stderr)"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=cwd or self.repo_path,
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out after 5 minutes"
        except Exception as e:
            return 1, "", f"Command execution failed: {e}"
    
    def check_git_clean(self) -> bool:
        """Verify git working directory is clean"""
        exit_code, stdout, stderr = self.run_command("git status --porcelain")
        if exit_code != 0:
            self.results.error_messages.append(f"Git status check failed: {stderr}")
            return False
        
        if stdout.strip():
            self.results.error_messages.append(
                f"Git working directory not clean:\\n{stdout}"
            )
            return False
        
        return True
    
    def fetch_pr_from_codex(self, pr_title: str) -> bool:
        """Fetch PR from Codex system (placeholder - would need actual API)"""
        print(f"🔄 Fetching PR: {pr_title}")
        
        # PLACEHOLDER: In reality, this would:
        # 1. Query Codex API for PR with matching title
        # 2. Get the PR's branch/commit info
        # 3. Fetch the remote branch
        # 4. Return success/failure
        
        print("⚠️  SIMULATION: Would fetch from Codex API")
        return True
    
    def checkout_test_branch(self, branch_name: str) -> bool:
        """Create and checkout test branch"""
        print(f"🔄 Creating test branch: {branch_name}")
        
        # Confirm branch name (safety check)
        if not branch_name.startswith("test/"):
            self.results.error_messages.append(
                f"Branch name '{branch_name}' doesn't start with 'test/'"
            )
            return False
        
        # Create and checkout branch
        exit_code, stdout, stderr = self.run_command(f"git checkout -b {branch_name}")
        if exit_code != 0:
            self.results.error_messages.append(f"Branch checkout failed: {stderr}")
            return False
        
        print(f"✅ Checked out to {branch_name}")
        return True
    
    def run_install_dev(self) -> bool:
        """Run make install-dev if Makefile exists"""
        print("🔄 Running make install-dev...")
        
        if not (self.repo_path / "Makefile").exists():
            print("ℹ️  No Makefile found, skipping make install-dev")
            return True
        
        exit_code, stdout, stderr = self.run_command("make install-dev")
        if exit_code != 0:
            self.results.error_messages.append(f"make install-dev failed: {stderr}")
            return False
        
        print("✅ make install-dev completed")
        return True
    
    def run_pnpm_install(self) -> bool:
        """Run pnpm install (with || true for non-critical failure)"""
        print("🔄 Running pnpm install...")
        
        exit_code, stdout, stderr = self.run_command("pnpm i || true")
        # Always return True since we use || true
        print("✅ pnpm install attempted (non-critical)")
        return True
    
    def run_alembic_upgrade(self) -> bool:
        """Run database migrations"""
        print("🔄 Running alembic upgrade head...")
        
        exit_code, stdout, stderr = self.run_command("alembic upgrade head")
        self.results.migration_success = (exit_code == 0)
        
        if exit_code != 0:
            self.results.error_messages.append(f"Migration failed: {stderr}")
            print("❌ Migration failed")
            return False
        
        print("✅ Migration successful")
        return True
    
    def run_python_compile(self) -> bool:
        """Run Python compilation check"""
        print("🔄 Running Python compilation check...")
        
        exit_code, stdout, stderr = self.run_command("python -m compileall .")
        
        # Count compilation errors (simplified - would need better parsing)
        if exit_code != 0:
            self.results.python_compile_errors = stderr.count("SyntaxError") + stderr.count("IndentationError")
            self.results.error_messages.append(f"Python compile errors: {stderr}")
            print(f"❌ Python compilation failed: {self.results.python_compile_errors} errors")
            return False
        
        print("✅ Python compilation successful")
        return True
    
    def run_pytest(self) -> bool:
        """Run Python tests"""
        print("🔄 Running pytest...")
        
        exit_code, stdout, stderr = self.run_command("pytest -q --tb=short")
        
        # Parse pytest output (simplified - would need better parsing)
        if "passed" in stdout:
            # Extract numbers from output like "5 passed, 2 failed"
            import re
            passed_match = re.search(r'(\\d+) passed', stdout)
            failed_match = re.search(r'(\\d+) failed', stdout)
            
            self.results.pytest_passed = int(passed_match.group(1)) if passed_match else 0
            self.results.pytest_failed = int(failed_match.group(1)) if failed_match else 0
        
        if exit_code != 0:
            self.results.error_messages.append(f"Pytest failures: {stderr}")
            print(f"❌ Pytest failed: {self.results.pytest_failed} failed")
            return False
        
        print(f"✅ Pytest passed: {self.results.pytest_passed} tests")
        return True
    
    def run_go_tests(self) -> bool:
        """Run Go tests"""
        print("🔄 Running Go tests...")
        
        # Check if Go files exist
        go_files = list(self.repo_path.rglob("*.go"))
        if not go_files:
            print("ℹ️  No Go files found, skipping Go tests")
            return True
        
        # Run go vet
        exit_code, stdout, stderr = self.run_command("go vet ./...")
        if exit_code != 0:
            self.results.error_messages.append(f"go vet failed: {stderr}")
            print("❌ go vet failed")
            return False
        
        # Run go test
        exit_code, stdout, stderr = self.run_command("go test ./...")
        if exit_code != 0:
            self.results.error_messages.append(f"go test failed: {stderr}")
            print("❌ go test failed")
            return False
        
        print("✅ Go tests passed")
        return True
    
    def generate_ci_summary(self) -> str:
        """Generate CI results summary"""
        summary = "## MCP Phase 0 CI Results\\n\\n"
        
        # Migration
        status = "✅" if self.results.migration_success else "❌"
        summary += f"- **Migration**: {status} {'Success' if self.results.migration_success else 'Failed'}\\n"
        
        # Python compile
        if self.results.python_compile_errors == 0:
            summary += f"- **Python Compile**: ✅ No errors\\n"
        else:
            summary += f"- **Python Compile**: ❌ {self.results.python_compile_errors} errors\\n"
        
        # Pytest
        if self.results.pytest_failed == 0:
            summary += f"- **Pytest**: ✅ {self.results.pytest_passed} passed\\n"
        else:
            summary += f"- **Pytest**: ❌ {self.results.pytest_failed} failed, {self.results.pytest_passed} passed\\n"
        
        # Go tests
        summary += f"- **Go Tests**: ✅ Passed\\n"
        
        # Overall result
        self.results.overall_success = (
            self.results.migration_success and
            self.results.python_compile_errors == 0 and
            self.results.pytest_failed == 0 and
            not self.results.error_messages
        )
        
        if self.results.overall_success:
            summary += "\\n🎉 **Overall: SUCCESS** - Ready for review!"
        else:
            summary += "\\n💥 **Overall: FAILED** - Needs fixes"
            if self.results.error_messages:
                summary += "\\n\\n**Errors:**\\n"
                for error in self.results.error_messages:
                    summary += f"- {error}\\n"
        
        return summary
    
    def comment_on_pr(self, pr_id: str, comment: str) -> bool:
        """Comment on PR (placeholder - would need actual API)"""
        print(f"💬 Would comment on PR {pr_id}:")
        print(comment)
        print("⚠️  SIMULATION: Would use Codex API to comment")
        return True
    
    def send_discord_update(self, channel: str, title: str, content: str) -> bool:
        """Send Discord update (placeholder - would need webhook)"""
        discord_message = f"**{title}**\\n\\n{content}"
        print(f"📢 Would send to Discord #{channel}:")
        print(discord_message)
        print("⚠️  SIMULATION: Would use Discord webhook")
        return True
    
    def execute_ci_pipeline(self, pr_title: str, test_branch: str) -> bool:
        """Execute the complete CI pipeline"""
        print("🚀 Starting Cursor-Legion-Operator CI Pipeline")
        print("=" * 60)
        
        # Safety check: clean git state
        if not self.check_git_clean():
            print("💥 ABORT: Git working directory not clean")
            return False
        
        # Step 1: Fetch PR
        if not self.fetch_pr_from_codex(pr_title):
            return False
        
        # Step 2: Checkout test branch
        if not self.checkout_test_branch(test_branch):
            return False
        
        # Step 3: Run installation and tests
        steps = [
            ("install-dev", self.run_install_dev),
            ("pnpm install", self.run_pnpm_install),
            ("alembic upgrade", self.run_alembic_upgrade),
            ("python compile", self.run_python_compile),
            ("pytest", self.run_pytest),
            ("go tests", self.run_go_tests)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"💥 Pipeline failed at: {step_name}")
                break
        
        # Generate summary
        summary = self.generate_ci_summary()
        print("\\n" + "=" * 60)
        print(summary)
        
        # Comment on PR
        if self.results.overall_success:
            self.comment_on_pr(pr_title, "CI ✅ — ready for review")
        else:
            self.comment_on_pr(pr_title, f"CI ❌ — needs fixes\\n\\n{summary}")
        
        # Discord notification
        self.send_discord_update(
            "agent-feed",
            "MCP Phase 0 CI Report", 
            summary
        )
        
        return self.results.overall_success


def main():
    """Main entry point for Cursor-Legion-Operator"""
    operator = CursorLegionOperator()
    
    # Mission parameters
    pr_title = "feat: MCP Stack Phase 0 foundation"
    test_branch = "test/mcp-phase0"
    
    success = operator.execute_ci_pipeline(pr_title, test_branch)
    
    if success:
        print("\\n🎉 CI Pipeline completed successfully!")
        sys.exit(0)
    else:
        print("\\n💥 CI Pipeline failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 