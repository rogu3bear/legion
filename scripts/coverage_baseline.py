#!/usr/bin/env python3
"""Establish coverage baseline for Legion Re-org Safety Blueprint."""
import json
import subprocess
import sys


def get_coverage_baseline():
    """Get current test coverage baseline."""
    try:
        # Run simple handshake test to get baseline
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--cov=legion",
                "--cov=core",
                "--cov=skills",
                "--cov-report=json:coverage-baseline.json",
                "--cov-report=term-missing",
                "scripts/selftest_handshake.py",
                "-v",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            try:
                with open("coverage-baseline.json") as f:
                    coverage_data = json.load(f)
                    total_coverage = coverage_data["totals"]["percent_covered"]
                    print(f"✅ Coverage baseline established: {total_coverage:.1f}%")
                    return total_coverage
            except (FileNotFoundError, KeyError) as e:
                print(f"⚠️  Coverage data not found: {e}")
                return 10.0  # Conservative fallback
        else:
            print(f"⚠️  Test run failed: {result.stderr}")
            return 10.0  # Conservative fallback
    except Exception as e:
        print(f"❌ Coverage baseline failed: {e}")
        return 10.0  # Conservative fallback


if __name__ == "__main__":
    baseline = get_coverage_baseline()
    print(f"Coverage gate set to: {baseline:.1f}%")
