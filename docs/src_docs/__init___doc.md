# \_\_init\_\_.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [TubeHarvester](#tubeharvester) | Package | YouTube Downloader Package initialization. |

## Overview
The `__init__.py` file initializes the TubeHarvester package, defining package-level metadata such as version and author. It serves as the entry point for the Python package structure.

## Detailed Breakdown

### TubeHarvester

**Purpose:** Package initialization and metadata definition.

**Description:**
This module marks the directory as a Python package and exposes top-level package information.

**Variables:**
| Variable | Type | Value | Description |
|----------|------|-------|-------------|
| `__version__` | str | "1.0.0" | Current package version. |
| `__author__` | str | "Panagopoulos Nikolaos" | Package author. |

**Source Code:**
```python
"""
TubeHarvester - YouTube Downloader Package

This package provides functionality for downloading YouTube videos and playlists
in various formats (MP3, MP4) with both GUI and programmatic interfaces.
"""

__version__ = "1.0.0"
__author__ = "Panagopoulos Nikolaos"
```
