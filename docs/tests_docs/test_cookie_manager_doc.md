# test_cookie_manager.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [TestCookieManager](#testcookiemanager) | Class | Test suite for the CookieManager class. |
| [setup_method](#setup_method) | Method | Initializes the CookieManager instance. |
| [testGetCookieFileExists](#testgetcookiefileexists) | Method | Verifies detection of an existing cookie file. |
| [testGetCookieFileExtractsSuccessfully](#testgetcookiefileextractssuccessfully) | Method | Validates full extraction workflow when the file is missing. |
| [testGetCookieFileExtractionFails](#testgetcookiefileextractionfails) | Method | Ensures fallback when extraction from all browsers fails. |
| [testExtractCookiesNoBrowsersFound](#testextractcookiesnobrowsersfound) | Method | Handles cases where no supported browsers are installed. |
| [testExtractCookiesEmptyFile](#testextractcookiesemptyfile) | Method | Validates cleanup and failure reporting for zero-byte cookie files. |

## Overview
The `test_cookie_manager.py` file contains unit tests for the `CookieManager` class, which is responsible for retrieving or extracting YouTube cookies from local browsers to bypass bot detection. These tests use extensive mocking of the filesystem (`pathlib`) and system processes (`subprocess`) to simulate cross-platform behavior.

## TestCookieManager

**Class Responsibility:** This class manages the testing lifecycle for `CookieManager`, ensuring that cookie retrieval is robust across different browser installations and filesystem states.

### setup_method

**Signature:**
```python
def setup_method(self)
```

**Purpose:** Initializes a `CookieManager` instance for each test.

**Implementation (Executable Logic Only):**
* **Line 9:** `self.cookie_manager = CookieManager()` — Standard initialization.

### testGetCookieFileExists

**Signature:**
```python
@patch('pathlib.Path.exists')
def testGetCookieFileExists(self, mock_exists)
```

**Purpose:** Verifies that if `yt_cookies.txt` already exists, the manager returns it immediately without attempting extraction.

**Implementation (Executable Logic Only):**
* **Line 13:** `mock_exists.return_value = True` — Simulates file existence.
* **Line 15:** `assert cookie_file == "yt_cookies.txt"` — Verifies the correct filename return.

### testGetCookieFileExtractsSuccessfully

**Signature:**
```python
@patch('shutil.which')
@patch('subprocess.run')
@patch('pathlib.Path.exists')
@patch('pathlib.Path.stat')
def testGetCookieFileExtractsSuccessfully(self, mock_stat, mock_exists, mock_subprocess_run, mock_shutil_which)
```

**Purpose:** Validates the flow where a cookie file is missing but is successfully extracted from a browser.

**Implementation (Executable Logic Only):**
* **Line 22:** `mock_exists.side_effect = [False, True]` — Simulates missing file initially, then present after extraction.
* **Line 24:** `Mock(returncode=0)` — Simulates successful subprocess execution.
* **Line 25:** `Mock(st_size=100)` — Simulates a non-empty resulting file.
* **Line 28-29:** Verifies correct filename return and subprocess trigger.

### testGetCookieFileExtractionFails

**Purpose:** Ensures that if extraction fails for all configured browsers, the manager returns `None`.

**Implementation (Executable Logic Only):**
* **Line 37:** `Mock(returncode=1, stderr="error")` — Simulates extraction failure.
* **Line 40-41:** Verifies `None` return and multiple attempts (one per browser).

### testExtractCookiesNoBrowsersFound

**Purpose:** Tests the condition where `yt-dlp` cannot find any supported browsers via `shutil.which`.

### testExtractCookiesEmptyFile

**Primary Library:** `pathlib`, `unittest.mock`  
**Purpose:** Ensures that if an extraction process produces an empty file, it is deleted and treated as a failure.

**Implementation (Executable Logic Only):**
* **Line 55:** `Mock(st_size=0)` — Simulates an empty file.
* **Line 57:** `assert ... is False` — Verifies failure return.
* **Line 58:** `assert mock_unlink.called` — Verifies that the empty file was deleted from the system.
```
