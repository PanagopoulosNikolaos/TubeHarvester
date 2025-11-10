#!/usr/bin/env python3
"""
TubeHarvester Test Runner

This script provides a convenient way to run all tests for the TubeHarvester project.
It activates the conda environment and runs pytest with appropriate settings.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests using pytest."""
    print("Running TubeHarvester tests...")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('src') or not os.path.exists('tests'):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)

    # Use the current python interpreter
    cmd = "python -m pytest tests/ -v --tb=short"

    try:
        result = subprocess.run(cmd, shell=True, cwd=os.getcwd())
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("All tests passed!")
        else:
            print("\n" + "=" * 50)
            print("Some tests failed. Check the output above for details.")
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user.")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
