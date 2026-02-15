# main Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [Main Execution Block](#main-execution-block) | Script | Entry point for TubeHarvester application |

## Overview

The main module serves as the entry point for the TubeHarvester GUI application. It imports and launches the graphical user interface when executed directly as a script.

## Detailed Breakdown

### Main Execution Block

**Purpose:** Launches the TubeHarvester GUI application when the script is run directly.

**Source Code:**
```python
#!/usr/bin/env python3
"""
Main entry point for TubeHarvester application.

This file serves as the main entry point for the TubeHarvester GUI application.
It can be run directly to start the YouTube downloader GUI.
"""

from src.GUI import runGui

if __name__ == "__main__":
    runGui()
```

**Implementation (Executable Logic Only):**
* **Line 9:** `from src.GUI import runGui` — Imports the GUI initialization function
* **Line 11:** `if __name__ == "__main__":` — Checks if script is run directly
* **Line 12:** `runGui()` — Launches the GUI application

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| runGui | Internal | Initializes and runs the GUI | src.GUI |

**Usage Example:**
```bash
python main.py
```

**Common Issues & Related Functions:**
* **Issue:** Import errors — Ensure the src package is in the Python path
* **`runGui()`:** Main GUI initialization function that creates the application window
