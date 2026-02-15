# CookieManager.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [CookieManager](#cookiemanager) | Class | Manages the extraction and retrieval of YouTube cookies from local browsers. |
| [CookieManager.__init__](#cookiemanager__init__) | Function | Initializes the CookieManager. |
| [CookieManager.getCookieFile](#cookiemanagergetcookiefile) | Function | Gets the path to the cookie file, extracting if necessary. |
| [CookieManager.extractCookies](#cookiemanagerextractcookies) | Function | Extracts YouTube cookies from installed browsers using yt-dlp. |

## Overview
The `CookieManager` module facilitates authenticated YouTube requests by managing cookie extraction from local web browsers. It acts as a bridge between the application and `yt-dlp`'s cookie extraction capabilities, ensuring that a valid cookie file is available for download operations.

## Detailed Breakdown

## CookieManager

**Class Responsibility:** Manages the extraction and retrieval of YouTube cookies from local browsers. This class attempts to find installed browsers and use yt-dlp's built-in cookie extraction to create a cookie file for authenticated requests.

### CookieManager.\_\_init\_\_

**Signature:**
```python
def __init__(self, log_callback=None)
```

**Purpose:** Initializes the CookieManager.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| log_callback | callable | No | None | Called with log messages. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def __init__(self, log_callback=None):
        """
        Initializes the CookieManager.

        Args:
            log_callback (callable, optional): Called with log messages.
        """
        self.log_callback = log_callback
```

**Implementation (Executable Logic Only):**
* **Line 33:** `self.log_callback = log_callback` — Stores the optional logging callback function.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| None | - | - | - |

### CookieManager.getCookieFile

**Signature:**
```python
def getCookieFile(self) -> str
```

**Purpose:** Gets the path to the cookie file, extracting if necessary.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | CookieManager | Yes | — | The instance of the class. |

**Returns:**
| Type | Description |
|------|-------------|
| str | Path to the cookie file or None if extraction fails. |

**Source Code:**
```python
    def getCookieFile(self):
        """
        Gets the path to the cookie file, extracting if necessary.

        Returns:
            str: Path to the cookie file or None if extraction fails.
        """
        cookie_path = Path(self.COOKIE_FILE)
        if cookie_path.exists():
            if self.log_callback:
                self.log_callback(f"Using existing cookie file: {self.COOKIE_FILE}")
            return str(cookie_path)
        
        if self.log_callback:
            self.log_callback("Cookie file not found. Attempting extraction from browsers.")
        
        if self.extractCookies():
            return str(cookie_path)
        
        return None
```

**Implementation (Executable Logic Only):**
* **Line 42:** `cookie_path = Path(self.COOKIE_FILE)` — Creates a Path object for the cookie file configuration.
* **Line 43:** `if cookie_path.exists():` — Checks if the cookie file already exists on the filesystem.
* **Line 44:** `if self.log_callback:` — Checks if a logging callback is registered.
* **Line 45:** `self.log_callback(f"Using existing cookie file: {self.COOKIE_FILE}")` — Logs the usage of the existing cookie file.
* **Line 46:** `return str(cookie_path)` — Returns the absolute path of the existing cookie file.
* **Line 48:** `if self.log_callback:` — Checks if a logging callback is registered.
* **Line 49:** `self.log_callback("Cookie file not found...)` — Logs that the cookie file is missing and extraction will begin.
* **Line 51:** `if self.extractCookies():` — Calls the extraction method and checks for success.
* **Line 52:** `return str(cookie_path)` — Returns the path of the newly extracted cookie file.
* **Line 54:** `return None` — Returns None indicating failure to retrieve or extract cookies.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| Path | External | File path manipulation | pathlib |
| self.extractCookies | Internal | Helper method to extract cookies | CookieManager |

### CookieManager.extractCookies

**Primary Library:** `subprocess`
**Purpose:** Extracts YouTube cookies from installed browsers using yt-dlp.

#### Overview
This method iterates through a predefined list of supported browsers and attempts to extract cookies using the `yt-dlp` command-line tool. It uses a trial-and-error approach, stopping at the first successful extraction.

#### Signature
```python
def extractCookies(self) -> bool
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | CookieManager | Yes | — | The instance of the class. |

#### Returns
| Type | Description |
|------|-------------|
| bool | True if extraction was successful, False otherwise. |

#### Raises
| Exception | Condition |
|-----------|-----------|
| Exception | Catches generic exceptions during the subprocess call or file operations to prevent crash. |

#### Dependencies
* **Required Libraries:** `subprocess` (Executing yt-dlp), `shutil` (Checking for browser executables)
* **External Tools:** `yt-dlp` (Core extraction tool)
* **Internal Modules:** `logging` (via callback)

#### Workflow (Executable Logic Only)

**Phase 1: Initialization**
Prepares for extraction by logging the attempt.
* **Line 63:** `if self.log_callback:` — Checks for logging callback.
* **Line 64:** `self.log_callback("Attempting to extract YouTube cookies...")` — Logs the start of the extraction process.

**Phase 2: Browser Iteration**
Iterates through supported browsers to find a valid source.
* **Line 66:** `for binary, name in self.BROWSERS:` — Loops through the list of known browser binaries and names.
* **Line 67:** `if not shutil.which(binary):` — Checks if the browser binary is present in the system PATH.
* **Line 68:** `continue` — Skips to the next browser if the current one is not found.
* **Line 70:** `if self.log_callback:` — Checks for logging callback.
* **Line 71:** `self.log_callback(f"Found {name}, attempting extraction...")` — Logs that a browser was found.

*Code Context:*
```python
        for binary, name in self.BROWSERS:
            if not shutil.which(binary):
                continue
```

**Phase 3: Extraction Attempt**
Executes `yt-dlp` to extract cookies from the identified browser.
* **Line 73:** `try:` — Begins error handling block for the external process.
* **Line 75:** `result = subprocess.run([...], capture_output=True, timeout=15, text=True)` — Executes `yt-dlp` with arguments to extract cookies from the specific browser, capturing output.

**Phase 4: Validation and Completion**
Verifies the result of the extraction attempt.
* **Line 87:** `if result.returncode == 0 and Path(self.COOKIE_FILE).exists():` — Checks if `yt-dlp` exited successfully and the output file was created.
* **Line 88:** `if Path(self.COOKIE_FILE).stat().st_size > 0:` — Verifies that the created cookie file is not empty.
* **Line 89:** `if self.log_callback:` — Checks for logging callback.
* **Line 90:** `self.log_callback(f"Successfully extracted cookies from {name}")` — Logs successful extraction.
* **Line 91:** `return True` — Returns True, terminating the loop and function.
* **Line 93:** `Path(self.COOKIE_FILE).unlink()` — Deletes the empty file if extraction yielded 0 bytes.

**Phase 5: Error Handling and Fallback**
Handles failures for the current browser and proceeds or finishes.
* **Line 95:** `except Exception as e:` — Catches any errors during the extraction process.
* **Line 96:** `if self.log_callback:` — Checks for logging callback.
* **Line 97:** `self.log_callback(f"Error extracting from {name}: {type(e).__name__}")` — Logs the error type.
* **Line 99:** `if self.log_callback:` — Checks for logging callback (after loop finishes without success).
* **Line 100:** `self.log_callback("Failed to extract cookies from any browser.")` — Logs failure after trying all browsers.
* **Line 101:** `return False` — Returns False indicating total failure.

#### Source Code
```python
    def extractCookies(self):
        """
        Extracts YouTube cookies from installed browsers using yt-dlp.

        Returns:
            bool: True if extraction was successful, False otherwise.
        """
        if self.log_callback:
            self.log_callback("Attempting to extract YouTube cookies...")

        for binary, name in self.BROWSERS:
            if not shutil.which(binary):
                continue

            if self.log_callback:
                self.log_callback(f"Found {name}, attempting extraction...")

            try:
                # Use --user-agent for consistency with downloader options
                result = subprocess.run(
                    [
                        "yt-dlp",
                        "--cookies-from-browser", name,
                        "--cookies", self.COOKIE_FILE,
                        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    ],
                    capture_output=True,
                    timeout=15,
                    text=True
                )

                if result.returncode == 0 and Path(self.COOKIE_FILE).exists():
                    if Path(self.COOKIE_FILE).stat().st_size > 0:
                        if self.log_callback:
                            self.log_callback(f"Successfully extracted cookies from {name}")
                        return True
                    else:
                        Path(self.COOKIE_FILE).unlink()

            except Exception as e:
                if self.log_callback:
                    self.log_callback(f"Error extracting from {name}: {type(e).__name__}")

        if self.log_callback:
            self.log_callback("Failed to extract cookies from any browser.")
        return False
```

#### Usage Example
```python
manager = CookieManager()
if manager.extractCookies():
    print("Cookies extracted!")
```

## Configuration: `BROWSERS`
```python
    BROWSERS = [
        ("brave-browser", "brave"),
        ("google-chrome", "chrome"),
        ("chromium", "chromium"),
        ("firefox", "firefox"),
        ("opera", "opera"),
        ("edge", "edge"),
    ]
```

**Key Options:**
| Option | Type | Purpose | Valid Values |
|--------|------|---------|--------------|
| binary | str | The system command to check for the browser's existence. | "google-chrome", "firefox", etc. |
| name | str | The internal name used by `yt-dlp` to identify the browser. | "chrome", "firefox", etc. |