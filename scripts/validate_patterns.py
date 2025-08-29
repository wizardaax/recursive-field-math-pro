#!/usr/bin/env python3
"""
Validation script to check for result_normal dictionary access patterns in the codebase.
This script can be run locally to validate the codebase before pushing.
"""

import subprocess
import sys
from pathlib import Path


def check_prohibited_patterns():
    """Check for prohibited patterns in the codebase."""
    print("Checking for prohibited patterns...")

    # Run the same check as CI
    try:
        result = subprocess.run(
            ["grep", "-r", r"\bresult_normal\.ok\b", ".", "--include=*.py", "-n"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )

        if result.returncode == 0:
            print("❌ Found prohibited pattern (attribute access instead of dictionary):")
            print(result.stdout)
            print("\nPlease replace with result_normal[\"ok\"] for dictionary access.")
            return False
        else:
            print("✅ No prohibited patterns found")
            return True

    except FileNotFoundError:
        print("Warning: grep command not found. Skipping pattern check.")
        return True


def main():
    """Main validation function."""
    print("Running codebase validation...")

    if not check_prohibited_patterns():
        print("\n❌ Validation failed!")
        sys.exit(1)

    print("\n✅ All validations passed!")


if __name__ == "__main__":
    main()
