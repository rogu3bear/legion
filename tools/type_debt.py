#!/usr/bin/env python3
"""Track mypy type debt and prevent regression."""

import asyncio
import json
import pathlib
import re
import subprocess
import sys
from typing import Dict, Any


async def post_debt_update(delta: int, current: int, previous: int) -> None:
    """Post type debt update to Discord."""
    try:
        # Import here to avoid circular dependencies
        sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
        from legion.utils.discord_bridge import send_discord_embed, MessageType
        
        if delta == 0:
            return  # No change, no notification
            
        # Create progress visualization  
        total_baseline = 90  # Current actual baseline from our mypy run
        progress = max(0, (total_baseline - current) / total_baseline)
        filled = int(progress * 10)
        bar = "🟩" * filled + "🟨" * min(1, 10 - filled) + "⬜" * max(0, 9 - filled)
        
        msg_type = MessageType.SUCCESS if delta < 0 else MessageType.WARNING
        delta_str = f"{delta:+d}" if delta != 0 else "±0"
        
        message = f"Type Debt Update: {delta_str} errors"
        fields = [
            ("Current Errors", str(current)),
            ("Previous Errors", str(previous)),
            ("Delta", delta_str),
            ("Progress", f"{bar} ({current}/{total_baseline})")
        ]
        
        await send_discord_embed(
            "TypeChecker",
            message,
            msg_type,
            fields=fields
        )
    except Exception as e:
        print(f"Failed to post Discord update: {e}")


def run_mypy() -> tuple[int, str]:
    """Run mypy and return error count and output."""
    try:
        # Use the same paths as pre-commit hook
        result = subprocess.run(
            ["mypy", "--no-color-output", "--config-file=mypy.ini", 
             "legion/", "interface/", "memory/", "integration/", "discord_bot.py"],
            capture_output=True,
            text=True,
            cwd=pathlib.Path(__file__).parent.parent
        )
        output = result.stdout + result.stderr
        
        # Count error lines (excluding notes and warnings)
        error_lines = re.findall(r": error:", output)
        return len(error_lines), output
        
    except subprocess.CalledProcessError as e:
        # mypy returns non-zero exit code when there are errors
        output = e.stdout + e.stderr
        error_lines = re.findall(r": error:", output)
        return len(error_lines), output
    except FileNotFoundError:
        print("Error: mypy not found. Please install with: pip install mypy")
        sys.exit(1)


def main():
    """Main type debt tracking function."""
    debt_file = pathlib.Path(".cache/type_debt.json")
    
    # Run mypy and count errors
    current_errors, mypy_output = run_mypy()
    
    # Load previous count
    previous_errors = current_errors  # Default to current if no history
    if debt_file.exists():
        try:
            data = json.loads(debt_file.read_text())
            previous_errors = data.get("errors", current_errors)
        except (json.JSONDecodeError, KeyError):
            print("Warning: Could not parse debt file, starting fresh")
    
    # Calculate delta
    delta = current_errors - previous_errors
    
    # Save current count
    debt_data = {
        "errors": current_errors,
        "timestamp": int(subprocess.run(["date", "+%s"], capture_output=True, text=True).stdout.strip()),
        "baseline": 90  # Current actual baseline from our mypy run
    }
    debt_file.write_text(json.dumps(debt_data, indent=2))
    
    # Print summary
    print(f"Type Debt Summary:")
    print(f"  Current errors: {current_errors}")
    print(f"  Previous errors: {previous_errors}")
    print(f"  Delta: {delta:+d}")
    print(f"  Baseline: {debt_data['baseline']}")
    
    # Post to Discord if there's a change
    if delta != 0:
        try:
            asyncio.run(post_debt_update(delta, current_errors, previous_errors))
        except Exception as e:
            print(f"Discord notification failed: {e}")
    
    # Check regression (fail if errors increased)
    if delta > 0:
        print(f"\n❌ ERROR: Type debt increased by {delta} errors!")
        print("Please fix the new type errors before merging.")
        if "--verbose" in sys.argv:
            print(f"\nMypy output:\n{mypy_output}")
        sys.exit(1)
    elif delta < 0:
        print(f"\n✅ SUCCESS: Reduced type debt by {abs(delta)} errors!")
    else:
        print(f"\n➖ No change in type debt.")
    
    # Check against baseline (warn if above baseline)
    baseline = debt_data["baseline"]
    if current_errors > baseline:
        excess = current_errors - baseline
        print(f"\n⚠️  WARNING: {excess} errors above baseline ({baseline})")
        if "--strict" in sys.argv:
            print("Strict mode: failing due to baseline excess")
            sys.exit(1)


if __name__ == "__main__":
    main() 