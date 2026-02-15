# run_tests Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [run_tests](#run_tests) | Function | Executes all project tests using pytest |

## Overview

The run_tests module provides a convenient test runner for the TubeHarvester project. It validates the working directory and executes pytest with appropriate settings for comprehensive test coverage.

## Detailed Breakdown

### run_tests

**Primary Library:** subprocess, pytest  
**Purpose:** Executes all project tests using pytest with verbose output.

#### Overview
Validates that the script is run from the project root directory, then executes pytest with verbose output and short traceback formatting. Handles interruptions gracefully and provides clear feedback on test results.

#### Signature
```python
def run_tests()
```

#### Returns
| Type | Description |
|------|-------------|
| int | Exit code (0 for success, 1 for failure or error) |

#### Dependencies
* **Required Libraries:** `subprocess` (External command execution)
* **Required Libraries:** `sys` (System operations and exit codes)
* **Required Libraries:** `os` (File system operations)
* **External Tools:** pytest (Test framework)

#### Workflow (Executable Logic Only)

**Phase 1: Initialization**
Prints header information to indicate test execution has started.
* **Operation 1:** `print("Running TubeHarvester tests...")` — Displays test start message
* **Operation 2:** `print("=" * 50)` — Prints separator line

*Code Context:*
```python
print("Running TubeHarvester tests...")
print("=" * 50)
```

**Phase 2: Directory Validation**
Verifies that the script is being run from the correct project directory.
* **Operation 1:** `if not os.path.exists('src') or not os.path.exists('tests'):` — Checks for required directories
* **Operation 2:** `sys.exit(1)` — Exits with error code if directories not found

*Code Context:*
```python
if not os.path.exists('src') or not os.path.exists('tests'):
    print("Error: Please run this script from the project root directory")
    sys.exit(1)
```

**Phase 3: Test Execution**
Runs pytest with verbose output and handles the results.
* **Operation 1:** `cmd = "python -m pytest tests/ -v --tb=short"` — Constructs pytest command
* **Operation 2:** `result = subprocess.run(cmd, shell=True, cwd=os.getcwd())` — Executes pytest
* **Operation 3:** Checks return code and prints appropriate success or failure message
* **Operation 4:** `return result.returncode` — Returns exit code

*Code Context:*
```python
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
```

#### Source Code
```python
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
```

#### Usage Example
```python
# Run from command line
python run_tests.py

# Or import and run programmatically
from run_tests import run_tests
exit_code = run_tests()
```

#### Common Issues & Related Functions
* **Issue:** "Error: Please run this script from the project root directory" — The script must be run from the directory containing src/ and tests/ folders
* **Issue:** pytest not found — Install pytest using `pip install pytest`
