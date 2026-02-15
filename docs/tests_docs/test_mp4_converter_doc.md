# test_mp4_converter.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [TestMp4Downloader](#testmp4downloader) | Class | Test suite for the Mp4Downloader class. |
| [setup_method](#setup_method) | Method | Initializes testing environment and downloader instance. |
| [teardown_method](#teardown_method) | Method | Cleans up temporary test directories and files. |
| [testInit](#testinit) | Method | Verifies default state and download path logic. |
| [testInitWithCallbacks](#testinitwithcallbacks) | Method | Verifies injection of progress and log callbacks. |
| [testSetPath](#testsetpath) | Method | Validates path assignment and directory auto-creation. |
| [testFetchVideoInfoSuccess](#testfetchvideoinfosuccess) | Method | Validates metadata extraction with Deno environment. |
| [testFetchVideoInfoNoUrl](#testfetchvideoinfonourl) | Method | Ensures error on missing URL during info fetching. |
| [testDownloadVideoSuccess](#testdownloadvideosuccess) | Method | Validates full MP4 download workflow with yt-dlp. |
| [testProgressHookDownloading](#testprogresshookdownloading) | Method | Validates percentage parsing from yt-dlp status strings. |
| [testHandleError](#testhandleerror) | Method | Validates error categorization and logging. |

## Overview
The `test_mp4_converter.py` file contains unit tests for the `Mp4Downloader` class. It ensures that the downloader correctly interfaces with `yt-dlp`, specifically verifying the use of the Deno JavaScript executor and the handling of various video resolutions and statuses.

## TestMp4Downloader

**Class Responsibility:** Manages tests for `Mp4Downloader`, providing a sandboxed environment using temporary directories and mocking `yt-dlp` to verify library configuration and data processing logic.

### setup_method

**Signature:**
```python
def setup_method(self)
```

**Purpose:** Initializes a test URL, path, and a fresh `Mp4Downloader`.

**Implementation (Executable Logic Only):**
* **Line 14:** Creates a temporary directory.
* **Line 15:** Instantiates the downloader (without initial URL/Path setup).

### testFetchVideoInfoSuccess

**Primary Library:** `yt_dlp`, `unittest.mock`  
**Purpose:** Validates that metadata extraction is performed with correct environment configurations.

#### Overview
This test ensures that when fetching video information, the `Mp4Downloader` correctly specifies the path to the Deno executable (required for some YouTube decryption) and correctly calls the `yt-dlp` library.

#### Workflow (Executable Logic Only)
* **Line 80:** Mocks a successful metadata dictionary.
* **Line 84:** Executes `fetchVideoInfo`.
* **Line 87:** Verifies that the `javascript_executor` option is set to `/home/ice/.deno/bin/deno`.
* **Line 90:** Verifies that `extract_info` was called with `download=False`.

*Code Context:*
```python
        self.downloader.setUrl(self.test_url)
        result = self.downloader.fetchVideoInfo()

        opts_capture = mock_ydl_class.call_args[0][0]
        assert opts_capture['javascript_executor'] == '/home/ice/.deno/bin/deno'
```

### testDownloadVideoSuccess

**Primary Library:** `yt_dlp`, `unittest.mock`  
**Purpose:** Validates the complete video download execution logic.

#### Overview
This test sets up a complete downloader configuration including URL, path, and resolution, then triggers the download. It verifies that the underlying library is configured with the expected resolution and environment settings.

#### Workflow (Executable Logic Only)
* **Line 114-117:** Configures the downloader instance.
* **Line 119:** Executes `downloadVideo`.
* **Line 122:** Verifies Deno path configuration.
* **Line 125:** Verifies that `extract_info` was called with `download=True` to trigger actual file transfer.
* **Line 128:** Checks if the success message was logged to the GUI.

### testProgressHookDownloading

**Purpose:** Tests the extraction of progress percentages from yt-dlp's status string.

**Implementation (Executable Logic Only):**
* **Line 166:** Provides a mock status dictionary with `_percent_str: ' 50.0%'`.
* **Line 172:** Asserts that the GUI progress callback received the integer `50`.

### testSetPath

**Purpose:** Validates that setting a download path ensures the directory's existence on the filesystem.

**Implementation (Executable Logic Only):**
* **Line 63:** Calls `setPath(self.test_path)`.
* **Line 66:** Asserts `os.path.exists(self.test_path)` to verify directory auto-creation.

### testHandleError

**Purpose:** Tests the translation of technical exceptions into user-friendly log messages.

**Implementation (Executable Logic Only):**
* **Line 227:** Simulates a "Private Video" exception.
* **Line 228-229:** Verifies that a specific authentication error message is logged instead of the raw exception string.
* **Line 232:** Simulates a generic exception.
* **Line 233:** Verifies that generic errors are prefixed with "Error: ".
```
