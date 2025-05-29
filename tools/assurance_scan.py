#!/usr/bin/env python3
"""
Assurance scan module for Legion repository.
Validates repository health and structure compliance.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Any


def run_command(cmd: str, check: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def check_required_directories() -> Tuple[float, List[str]]:
    """Check if required Legion directories exist."""
    required_dirs = [
        "legion/", "legion/agents/", "legion/agents/python/", "legion/agents/go/",
        "legion/configs/", "core/", "core/utils/", "core/db/", "core/db/migrations/",
        "skills/", "memory/", "memory/db/", "memory/logs/", "artifacts/",
        "artifacts/reports/", "artifacts/code/", "integration/discord/",
        "integration/discord/cogs/", "interface/", "interface/static/",
        "interface/templates/", "tests/", "tests/agents/", "tests/core/",
        "docs/", "scripts/"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    score = (len(required_dirs) - len(missing_dirs)) / len(required_dirs)
    return score, missing_dirs


def check_required_files() -> Tuple[float, List[str]]:
    """Check if required Legion files exist."""
    required_files = [
        ".env", ".gitignore", "requirements.txt", "package.json", "go.mod",
        "legion/__init__.py", "legion/orchestrator.py",
        "legion/agents/__init__.py", "legion/agents/python/__init__.py",
        "legion/agents/python/doctor.py", "legion/agents/python/researcher.py",
        "legion/configs/doctor.yaml", "legion/configs/researcher.yaml",
        "core/utils/network.py", "core/utils/indexing.py", "core/db/schema.sql",
        "skills/search.py", "skills/summarize.py", "memory/legion_memory.py",
        "memory/db/legion.db", "memory/logs/task_log.jsonl",
        "integration/discord/__init__.py", "integration/discord/settings.py",
        "integration/discord/bot.py", "integration/discord/cogs/__init__.py",
        "integration/discord/cogs/orchestrator.py", "integration/discord/cogs/ux_feed.py",
        "integration/discord/cogs/health.py", "interface/main.py",
        "interface/static/js_feed.js", "interface/templates/index.html",
        "tests/agents/test_agents.py", "tests/core/test_network.py",
        "tests/test_orchestrator.py", "docs/README.md", "docs/architecture.md",
        "scripts/deploy.sh", "scripts/init_memory.sh", "scripts/verify_discord.sh"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    score = (len(required_files) - len(missing_files)) / len(required_files)
    return score, missing_files


def check_python_syntax() -> Tuple[float, List[str]]:
    """Check Python files for syntax errors."""
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and .venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(file_path), 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}:{e.lineno}: {e.msg}")
        except Exception:
            # Skip files that can't be read
            continue
    
    if python_files:
        score = (len(python_files) - len(syntax_errors)) / len(python_files)
    else:
        score = 1.0
    
    return score, syntax_errors


def check_git_status() -> Tuple[float, List[str]]:
    """Check git repository status."""
    issues = []
    
    # Check if we're in a git repository
    code, stdout, stderr = run_command("git rev-parse --git-dir", check=False)
    if code != 0:
        issues.append("Not in a git repository")
        return 0.0, issues
    
    # Check for uncommitted changes in critical files
    code, stdout, stderr = run_command("git status --porcelain", check=False)
    if code == 0 and stdout.strip():
        critical_patterns = ['legion/', 'core/', 'requirements.txt', '.env']
        for line in stdout.strip().split('\n'):
            file_path = line[3:] if len(line) > 3 else ""
            if any(pattern in file_path for pattern in critical_patterns):
                issues.append(f"Uncommitted changes in critical file: {file_path}")
    
    # Check if we can fetch from remote
    code, stdout, stderr = run_command("git remote -v", check=False)
    if code != 0:
        issues.append("No git remotes configured")
    
    score = 1.0 if len(issues) == 0 else max(0.0, 1.0 - (len(issues) * 0.2))
    return score, issues


def check_port_configuration() -> Tuple[float, List[str]]:
    """Check port configuration compliance."""
    issues = []
    
    # Check if port configuration files exist
    port_files = [".env.ports", "check_ports.py"]
    missing_port_files = [f for f in port_files if not Path(f).exists()]
    
    if missing_port_files:
        issues.extend([f"Missing port config file: {f}" for f in missing_port_files])
    
    # Try to run port check
    if Path("check_ports.py").exists():
        code, stdout, stderr = run_command("python check_ports.py", check=False)
        if code != 0:
            issues.append(f"Port validation failed: {stderr}")
    
    score = 1.0 if len(issues) == 0 else max(0.0, 1.0 - (len(issues) * 0.3))
    return score, issues


def run_assurance_scan(min_score: float = 0.85) -> Dict[str, Any]:
    """Run comprehensive assurance scan."""
    print("🔍 Running Legion Assurance Scan...")
    
    checks = {
        "directories": check_required_directories,
        "files": check_required_files,
        "python_syntax": check_python_syntax,
        "git_status": check_git_status,
        "port_config": check_port_configuration
    }
    
    results = {}
    total_score = 0.0
    
    for check_name, check_func in checks.items():
        print(f"  📋 Running {check_name} check...")
        score, issues = check_func()
        results[check_name] = {
            "score": score,
            "issues": issues,
            "status": "✅ PASS" if score >= min_score else "❌ FAIL"
        }
        total_score += score
        
        print(f"    {results[check_name]['status']} Score: {score:.2f}")
        if issues:
            for issue in issues[:3]:  # Show first 3 issues
                print(f"      ⚠️  {issue}")
            if len(issues) > 3:
                print(f"      ... and {len(issues) - 3} more issues")
    
    overall_score = total_score / len(checks)
    results["overall"] = {
        "score": overall_score,
        "status": "✅ PASS" if overall_score >= min_score else "❌ FAIL",
        "min_required": min_score
    }
    
    print(f"\n📊 Overall Assurance Score: {overall_score:.2f}")
    print(f"🎯 Required Minimum: {min_score:.2f}")
    print(f"🔍 Result: {results['overall']['status']}")
    
    return results


def main():
    """Main assurance scan routine."""
    parser = argparse.ArgumentParser(description="Run Legion repository assurance scan")
    parser.add_argument("--min", type=float, default=0.85, help="Minimum required score")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()
    
    results = run_assurance_scan(args.min)
    
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    
    # Return appropriate exit code
    overall_score = results["overall"]["score"]
    return 0 if overall_score >= args.min else 1


if __name__ == "__main__":
    sys.exit(main()) 