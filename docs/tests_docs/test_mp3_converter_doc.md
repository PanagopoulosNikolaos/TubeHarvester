# test_mp3_converter.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [TestMp3Downloader](#testmp3downloader) | Class | Test suite for the Mp3Downloader class. |
| [setup_method](#setup_method) | Method | Initializes testing environment and downloader instance. |
| [teardown_method](#teardown_method) | Method | Cleans up temporary test directories. |
| [testInitWithUrlAndPath](#testinitwithurlandpath) | Method | Verifies constructor assignment. |
| [testSetUrl](#testseturl) | Method | Verifies URL setter. |
| [testSetPath](#testsetpath) | Method | Verifies path setter. |
| [testGetDefaultDownloadPath](#getdefaultdownloadpath) | Method | Verifies cross-platform default Downloads path logic. |
| [testDownloadAsMp3Success](#testdownloadasmp3success) | Method | Validates the multi-stage yt-dlp download process. |
| [testDownloadAsMp3WithCustomTitle](#testdownloadasmp3withcustomtitle) | Method | Verifies filename templating with custom titles. |
| [testDownloadAsMp3Failure](#testdownloadasmp3failure) | Method | Ensures exceptions are bubbled up and logged. |
| [testProgressHookDownloading](#testprogresshookdownloading) | Method | Validates percentage calculation during download. |
| [testProgressHookFinished](#testprogresshookfinished) | Method | Verifies 100% completion reporting. |

## Overview
The `test_mp3_converter.py` file provides the unit test suite for the `Mp3Downloader` class. It focuses on validating the configuration of `yt-dlp` for audio extraction (MP3 format), handling of download progress via hooks, and robust error management.

## TestMp3Downloader

**Class Responsibility:** Manages the lifecycle and assertions for testing the `Mp3Downloader` component, using temporary directories for file output simulation and mocks for the `yt-dlp` library.

### setup_method

**Signature:**
```python
def setup_method(self)
```

**Purpose:** Prepares a temporary filesystem and a `Mp3Downloader` instance.

**Implementation (Executable Logic Only):**
* **Line 14:** `tempfile.mkdtemp()` — Creates a unique temporary path.
* **Line 15:** `Mp3Downloader(...)` — Initializes the downloader with the test URL and path.

### testDownloadAsMp3Success

**Primary Library:** `yt_dlp`, `unittest.mock`  
**Purpose:** Validates the successful multi-call process required by `yt-dlp` to extract metadata and perform a download.

#### Overview
This test covers two critical phases of the `downloadAsMp3` method: initial metadata extraction (to get the title) and the subsequent actual download execution. It verifies that `YoutubeDL` is instantiated twice with different configurations and that the result matches the expected save path.

#### Signature
```python
@patch('yt_dlp.YoutubeDL')
def testDownloadAsMp3Success(self, mock_ydl_class)
```

#### Workflow (Executable Logic Only)

**Phase 1: Mock yt-dlp Contexts**
* **Line 76:** `mock_ydl_class.side_effect = [...]` — Sequences two mock instances (for info extraction and for downloading).
* **Line 70:** Sets `extract_info.return_value = {'title': 'Test Video'}`.

**Phase 2: Execution**
* **Line 83:** Calls `downloadAsMp3()`.

**Phase 3: Verification**
* **Line 86:** Asserts that `YoutubeDL` was called exactly twice.
* **Line 87:** Verifies the return path matches the initialized test path.
* **Line 90:** Ensures the log callback was triggered to keep the user informed.

*Code Context:*
```python
        mock_ydl_class.side_effect = [mock_ydl_info, mock_ydl_download]
        downloader = Mp3Downloader(self.test_url, self.test_path, progress_callback, log_callback)
        result = downloader.downloadAsMp3()
```

#### Source Code
```python
    @patch('yt_dlp.YoutubeDL')
    def testDownloadAsMp3Success(self, mock_ydl_class):
        """Test successful MP3 download."""
        # Mock the YoutubeDL instances as context managers
        mock_ydl_info = Mock()
        mock_ydl_info.__enter__ = Mock(return_value=mock_ydl_info)
        mock_ydl_info.__exit__ = Mock(return_value=None)
        mock_ydl_info.extract_info.return_value = {'title': 'Test Video'}

        mock_ydl_download = Mock()
        mock_ydl_download.__enter__ = Mock(return_value=mock_ydl_download)
        mock_ydl_download.__exit__ = Mock(return_value=None)

        mock_ydl_class.side_effect = [mock_ydl_info, mock_ydl_download]

        # Mock progress callback
        progress_callback = Mock()
        log_callback = Mock()

        downloader = Mp3Downloader(self.test_url, self.test_path, progress_callback, log_callback)
        result = downloader.downloadAsMp3()

        # Verify the download was called
        assert mock_ydl_class.call_count == 2
        assert result == self.test_path

        # Verify log callback was called
        log_callback.assert_called()
```

### testProgressHookDownloading

**Purpose:** Validates the conversion of `yt-dlp` raw bytes data into a percentage for the GUI.

**Implementation (Executable Logic Only):**
* **Line 139-143:** Constructs a status dictionary with `total_bytes: 1000` and `downloaded_bytes: 500`.
* **Line 145:** Calls `progressHook`.
* **Line 148:** Asserts that the callback received the value `50`.

### testProgressHookNoTotalBytes

**Purpose:** Verifies that the progress hook gracefully handles missing size metadata.

**Implementation (Executable Logic Only):**
* **Line 169-172:** Constructs a status dictionary without `total_bytes`.
* **Line 177:** Asserts that `progress_callback` was skipped to avoid division by zero errors.
```
