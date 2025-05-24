#!/usr/bin/env python3
"""Identify easy win opportunities for type error fixing."""

import json
import pathlib
import re
import subprocess
import sys
from collections import defaultdict
from typing import Dict, List, Tuple


def run_mypy_with_codes() -> str:
    """Run mypy with error codes to categorize errors."""
    try:
        result = subprocess.run(
            ["mypy", "--no-color-output", "--config-file=mypy.ini", "--show-error-codes",
             "legion/", "interface/", "memory/", "integration/", "discord_bot.py"],
            capture_output=True,
            text=True,
            cwd=pathlib.Path(__file__).parent.parent
        )
        return result.stdout + result.stderr
    except FileNotFoundError:
        print("Error: mypy not found. Please install with: pip install mypy")
        sys.exit(1)


def parse_mypy_output(output: str) -> Dict[str, List[Tuple[str, str, str]]]:
    """Parse mypy output into file -> [(line, error_code, message)]."""
    file_errors = defaultdict(list)
    
    for line in output.split('\n'):
        if ': error:' in line:
            # Format: file.py:line: error: message [error-code]
            match = re.match(r'^([^:]+):(\d+): error: (.+?) \[([^\]]+)\]', line)
            if match:
                file_path, line_num, message, error_code = match.groups()
                file_errors[file_path].append((line_num, error_code, message))
    
    return dict(file_errors)


def categorize_files(file_errors: Dict[str, List[Tuple[str, str, str]]]) -> Dict[str, List[str]]:
    """Categorize files by error count for prioritization."""
    categories = {
        "easy_wins": [],      # 1-3 errors
        "manageable": [],     # 4-10 errors  
        "complex": [],        # 11+ errors
    }
    
    for file_path, errors in file_errors.items():
        error_count = len(errors)
        if error_count <= 3:
            categories["easy_wins"].append(file_path)
        elif error_count <= 10:
            categories["manageable"].append(file_path)
        else:
            categories["complex"].append(file_path)
    
    return categories


def analyze_error_patterns(file_errors: Dict[str, List[Tuple[str, str, str]]]) -> Dict[str, int]:
    """Analyze common error patterns across the codebase."""
    error_counts = defaultdict(int)
    
    for file_path, errors in file_errors.items():
        for line_num, error_code, message in errors:
            error_counts[error_code] += 1
    
    return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))


def generate_recommendations(categories: Dict[str, List[str]], 
                           file_errors: Dict[str, List[Tuple[str, str, str]]], 
                           error_patterns: Dict[str, int]) -> str:
    """Generate actionable recommendations for fixing type errors."""
    report = []
    
    report.append("# 🎯 Type Error Easy Wins Queue\n")
    
    # Easy wins section
    if categories["easy_wins"]:
        report.append("## 🚀 Quick Fixes (1-3 errors each)")
        report.append("*Start here for immediate impact!*\n")
        
        for i, file_path in enumerate(categories["easy_wins"][:5], 1):
            errors = file_errors[file_path]
            report.append(f"### {i}. `{file_path}` ({len(errors)} errors)")
            
            for line_num, error_code, message in errors:
                report.append(f"- **Line {line_num}:** `{error_code}` - {message}")
            
            # Add quick fix suggestions
            common_fixes = {
                "var-annotated": "Add type annotation: `variable: TypeHint = value`",
                "assignment": "Check type compatibility or add type ignore",
                "arg-type": "Verify argument types match function signature",
                "attr-defined": "Check attribute exists or add type ignore",
                "return-value": "Ensure return type matches annotation"
            }
            
            error_codes = [error[1] for error in errors]
            suggested_fixes = [common_fixes.get(code, f"See mypy docs for {code}") 
                             for code in set(error_codes)]
            
            if suggested_fixes:
                report.append("  **Quick fixes:**")
                for fix in set(suggested_fixes):
                    report.append(f"  - {fix}")
            
            report.append("")
    
    # Manageable files
    if categories["manageable"]:
        report.append("## 🔧 Medium Priority (4-10 errors each)")
        for file_path in categories["manageable"][:3]:
            errors = file_errors[file_path]
            report.append(f"- `{file_path}` ({len(errors)} errors)")
    
    # Error pattern analysis
    report.append("\n## 📊 Top Error Patterns")
    for error_code, count in list(error_patterns.items())[:5]:
        percentage = (count / sum(error_patterns.values())) * 100
        report.append(f"- `{error_code}`: {count} occurrences ({percentage:.1f}%)")
    
    # Recommendations
    report.append("\n## 💡 Recommended Strategy")
    report.append("1. **Start with easy wins** - Fix 1-3 files with ≤3 errors each")
    report.append("2. **Focus on common patterns** - Address high-frequency error codes")
    report.append("3. **Use type ignores judiciously** - For complex cases, add `# type: ignore[error-code]`")
    report.append("4. **Add `# mypy: ignore-errors`** - For files with >10 errors")
    
    return "\n".join(report)


def main():
    """Generate easy wins queue for type error fixing."""
    print("🔍 Analyzing mypy errors for easy wins...")
    
    # Run mypy with error codes
    mypy_output = run_mypy_with_codes()
    
    # Parse results
    file_errors = parse_mypy_output(mypy_output)
    categories = categorize_files(file_errors)
    error_patterns = analyze_error_patterns(file_errors)
    
    # Generate report
    report = generate_recommendations(categories, file_errors, error_patterns)
    
    # Save to file
    output_file = pathlib.Path("artifacts/reports/easy_wins_queue.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report)
    
    # Print summary
    total_files = len(file_errors)
    easy_wins = len(categories["easy_wins"])
    total_errors = sum(len(errors) for errors in file_errors.values())
    
    print(f"📈 Analysis Complete:")
    print(f"  Total files with errors: {total_files}")
    print(f"  Easy wins (≤3 errors): {easy_wins}")
    print(f"  Total errors: {total_errors}")
    print(f"  Report saved: {output_file}")
    
    # Show top 3 easy wins
    if easy_wins > 0:
        print(f"\n🎯 Top 3 Easy Wins:")
        for i, file_path in enumerate(categories["easy_wins"][:3], 1):
            error_count = len(file_errors[file_path])
            print(f"  {i}. {file_path} ({error_count} errors)")
    
    # Save machine-readable data
    data = {
        "categories": categories,
        "error_patterns": error_patterns,
        "total_files": total_files,
        "total_errors": total_errors,
        "easy_wins_count": easy_wins
    }
    
    json_file = pathlib.Path("artifacts/reports/easy_wins_data.json")
    json_file.write_text(json.dumps(data, indent=2))
    
    return 0 if easy_wins > 0 else 1


if __name__ == "__main__":
    sys.exit(main()) 