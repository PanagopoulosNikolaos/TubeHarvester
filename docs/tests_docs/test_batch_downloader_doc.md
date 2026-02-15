# test_batch_downloader.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [TestBatchDownloader](#testbatchdownloader) | Class | Test suite for the BatchDownloader class. |
| [setup_method](#setup_method) | Method | Initializes testing environment for each test case. |
| [teardown_method](#teardown_method) | Method | Cleans up the temporary directory after each test. |
| [testInit](#testinit) | Method | Verifies the default initialization state of BatchDownloader. |
| [testInitWithParameters](#testinitwithparameters) | Method | Verifies initialization with custom configurations. |
| [testDownloadBatchMp4Success](#testdownloadbatchmp4success) | Method | Validates success of MP4 batch downloads using mocks. |
| [testDownloadBatchMp3Success](#testdownloadbatchmp3success) | Method | Validates success of MP3 batch downloads using mocks. |
| [testDownloadBatchEmptyList](#testdownloadbatchemptylist) | Method | Checks behavior when an empty list is provided for download. |
| [testDownloadBatchInvalidFormat](#testdownloadbatchinvalidformat) | Method | Ensures error handling for unsupported file formats. |
| [testDownloadBatchPartialFailure](#testdownloadbatchpartialfailure) | Method | Verifies handling of batches where some downloads fail. |
| [testCancelDownload](#testcanceldownload) | Method | Tests the cancellation flag setting. |
| [testCreateFolderStructureMp3](#testcreatefolderstructuremp3) | Method | Validates recursive directory creation for MP3 files. |
| [testCreateFolderStructureMp4](#testcreatefolderstructuremp4) | Method | Validates recursive directory creation for MP4 files. |
| [testDownloadBatchCancellation](#testdownloadbatchcancellation) | Method | Verifies that BatchDownloader halts execution upon cancellation. |
| [testDownloadSingleVideoMp4](#testdownloadsinglevideomp4) | Method | Tests individual MP4 video download logic. |
| [testDownloadSingleVideoMp3](#testdownloadsinglevideomp3) | Method | Tests individual MP3 video download logic. |
| [testDownloadSingleVideoInvalidFormat](#testdownloadsinglevideoinvalidformat) | Method | Tests error reporting for single invalid format download. |
| [testDownloadSingleVideoException](#testdownloadsinglevideoexception) | Method | Tests error handling when a downloader throws an exception. |

## Overview
The `test_batch_downloader.py` file contains unit and integration tests for the `BatchDownloader` class. It ensures that video downloads can be performed in batches, organized into folder structures, and handled correctly under various conditions such as success, partial failure, and cancellation.

## TestBatchDownloader

**Class Responsibility:** This class manages the testing lifecycle for `BatchDownloader`, providing setup and teardown of temporary file systems and executing various test cases to validate downloading logic.

### setup_method

**Signature:**
```python
def setup_method(self)
```

**Purpose:** Prepares a temporary directory and a `BatchDownloader` instance for each test.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | TestBatchDownloader | Yes | — | Instance reference. |

**Returns:**
| Type | Description |
|------|-------------|
| None | No return value. |

**Source Code:**
```python
    def setup_method(self):
        """Create temporary directory and downloader instance."""
        self.test_base_path = tempfile.mkdtemp()
        self.downloader = BatchDownloader(max_workers=2)
```

**Implementation (Executable Logic Only):**
* **Line 13:** `tempfile.mkdtemp()` — Creates a temporary directory for test artifacts.
* **Line 14:** `BatchDownloader(max_workers=2)` — Initializes the downloader with a fixed worker count.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| tempfile.mkdtemp | External | Create temporary directories | tempfile |
| BatchDownloader | Internal | Target class for testing | src.BatchDownloader |

### teardown_method

**Signature:**
```python
def teardown_method(self)
```

**Purpose:** Cleans up the temporary directory and all files within it after each test.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | TestBatchDownloader | Yes | — | Instance reference. |

**Returns:**
| Type | Description |
|------|-------------|
| None | No return value. |

**Source Code:**
```python
    def teardown_method(self):
        """Clean up temporary directory."""
        # Clean up any files created during tests
        if os.path.exists(self.test_base_path):
            for file in os.listdir(self.test_base_path):
                file_path = os.path.join(self.test_base_path, file)
                if os.path.isfile(file_path):
                    try:
                        os.unlink(file_path)
                    except:
                        pass  # Ignore cleanup errors
            try:
                os.rmdir(self.test_base_path)
            except:
                pass  # Ignore cleanup errors
```

**Implementation (Executable Logic Only):**
* **Line 19:** `os.path.exists(self.test_base_path)` — Checks if the directory exists before cleanup.
* **Line 20:** `os.listdir(self.test_base_path)` — Iterates through files in the temporary directory.
* **Line 24:** `os.unlink(file_path)` — Deletes individual files.
* **Line 28:** `os.rmdir(self.test_base_path)` — Removes the temporary directory itself.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| os.path.exists | External | Check for path existence | os |
| os.listdir | External | List directory contents | os |
| os.path.join | External | Path construction | os |
| os.path.isfile | External | Identify files | os |
| os.unlink | External | Remove files | os |
| os.rmdir | External | Remove directories | os |

### testInit

**Signature:**
```python
def testInit(self)
```

**Purpose:** Verifies that the `BatchDownloader` initializes with correct default values.

**Implementation (Executable Logic Only):**
* **Line 34:** `BatchDownloader()` — Instantiates the downloader.
* **Line 35-39:** `assert` statements — Validates default properties (workers, callbacks, counters).

### testInitWithParameters

**Signature:**
```python
def testInitWithParameters(self)
```

**Purpose:** Verifies that parameters passed to the constructor are correctly assigned.

**Implementation (Executable Logic Only):**
* **Line 43-44:** `Mock()` — Creates mock objects for callbacks.
* **Line 45:** `BatchDownloader(...)` — Initializes with custom parameters.
* **Line 46-48:** `assert` statements — Validates property assignment.

### testDownloadBatchMp4Success

**Primary Library:** `unittest.mock`  
**Purpose:** Validates successful MP4 batch download process.

#### Overview
This test uses mocks to simulate the `Mp4Downloader` and verifies that `BatchDownloader.downloadBatch` correctly coordinates multiple downloads, updates progress, and returns success metrics.

#### Signature
```python
def testDownloadBatchMp4Success(self, mock_mp4_downloader_class)
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | TestBatchDownloader | Yes | — | Instance reference. |
| mock_mp4_downloader_class | MagicMock | Yes | — | Mocked class from the patch decorator. |

#### Workflow (Executable Logic Only)

**Phase 1: Setup Mocks**
Mocks the downloader class and its instance methods.
* **Line 54-60:** Sets up return values and mock methods for the downloader instance.

**Phase 2: Execution**
Triggers the batch download.
* **Line 70-71:** Calls `downloadBatch` with a list of two videos.

**Phase 3: Verification**
Checks the results and call counts.
* **Line 74-76:** Asserts return values for successful and failed counts.
* **Line 79-82:** Asserts that the downloader methods were called for each video.
* **Line 85-86:** Asserts that logging and progress callbacks were executed.

*Code Context:*
```python
        downloader = BatchDownloader(max_workers=1, progress_callback=progress_callback, log_callback=log_callback)
        result = downloader.downloadBatch(video_list, 'MP4', self.test_base_path, 'highest')

        # Verify results
        assert result['successful'] == 2
```

#### Source Code
```python
    @patch('src.BatchDownloader.Mp4Downloader')
    def testDownloadBatchMp4Success(self, mock_mp4_downloader_class):
        """Test successful MP4 batch download."""
        # Mock MP4 downloader
        mock_mp4_downloader = Mock()
        mock_mp4_downloader_class.return_value = mock_mp4_downloader

        # Mock download methods
        mock_mp4_downloader.setUrl = Mock()
        mock_mp4_downloader.setPath = Mock()
        mock_mp4_downloader.downloadVideo = Mock()

        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': 'TestChannel/Playlist1'},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': 'TestChannel/Playlist1'}
        ]

        log_callback = Mock()
        progress_callback = Mock()

        downloader = BatchDownloader(max_workers=1, progress_callback=progress_callback, log_callback=log_callback)
        result = downloader.downloadBatch(video_list, 'MP4', self.test_base_path, 'highest')

        # Verify results
        assert result['successful'] == 2
        assert result['failed'] == 0
        assert result['errors'] == []

        # Verify MP4 downloader was called correctly
        assert mock_mp4_downloader_class.call_count == 2
        assert mock_mp4_downloader.setUrl.call_count == 2
        assert mock_mp4_downloader.setPath.call_count == 2
        assert mock_mp4_downloader.downloadVideo.call_count == 2

        # Verify callbacks were called
        assert log_callback.call_count >= 3  # Start, 2 completed, finished
        assert progress_callback.call_count >= 2  # Progress updates
```

### testDownloadBatchMp3Success

**Primary Library:** `unittest.mock`  
**Purpose:** Validates successful MP3 batch download process.

#### Workflow (Executable Logic Only)
* **Line 92-108:** Sets up MP3 downloader mocks and executes `downloadBatch` for MP3 files.
* **Line 112-120:** Verifies success counts and method calls on the MP3 downloader.

### testDownloadBatchEmptyList

**Purpose:** Verifies behavior when the download list is empty.

**Implementation (Executable Logic Only):**
* **Line 127:** Calls `downloadBatch` with an empty list.
* **Line 129-131:** Asserts zero counts.
* **Line 134:** Verifies specific log message "No videos to download".

### testDownloadBatchInvalidFormat

**Purpose:** Verifies handling of unsupported download formats.

**Implementation (Executable Logic Only):**
* **Line 144-145:** Patches both MP4 and MP3 downloaders.
* **Line 153:** Calls `downloadBatch` with 'AVI' format.
* **Line 155-158:** Asserts failure and presence of error message.

### testDownloadBatchPartialFailure

**Primary Library:** `unittest.mock`  
**Purpose:** Validates behavior when some downloads in a batch fail.

#### Workflow (Executable Logic Only)
* **Line 164-174:** Configures two downloader mocks, one that succeeds and one that raises an Exception.
* **Line 185:** Executes the batch download.
* **Line 187-189:** Verifies that one succeeded and one failed, with one error recorded.

### testCancelDownload

**Purpose:** Verifies that the cancellation signal is set correctly.

**Implementation (Executable Logic Only):**
* **Line 196:** Calls `cancelDownload()`.
* **Line 198:** Checks `cancel_event.is_set()`.

### testCreateFolderStructureMp3

**Purpose:** Validates the creation of directory structures for MP3 downloads.

**Implementation (Executable Logic Only):**
* **Line 209:** Calls `createFolderStructure` with MP3 format.
* **Line 211-217:** Asserts correctly constructed paths.
* **Line 220-222:** Verifies that directories actually exist on the file system.

### testCreateFolderStructureMp4

**Purpose:** Validates the creation of directory structures for MP4 downloads.

**Implementation (Executable Logic Only):**
* **Line 230:** Calls `createFolderStructure` with MP4 format.
* **Line 232-239:** Verifies path logic and directory existence for MP4.

### testDownloadBatchCancellation

**Primary Library:** `threading`, `concurrent.futures`  
**Purpose:** Verifies that the batch download halts when cancelled.

#### Workflow (Executable Logic Only)
* **Line 246-248:** Mocks a `threading.Event` where `is_set()` returns True midway through iteration.
* **Line 251-257:** Mocks the `ThreadPoolExecutor` and internal future objects.
* **Line 267-269:** Patching `downloadSingleVideo` and executing `downloadBatch`.
* **Line 272:** Verifies the log message "Batch download cancelled".

### testDownloadSingleVideoMp4

**Purpose:** Validates the low-level `downloadSingleVideo` method for MP4.

**Implementation (Executable Logic Only):**
* **Line 283:** Calls `downloadSingleVideo`.
* **Line 285-291:** Verifies success return and correct downloader configuration.

### testDownloadSingleVideoMp3

**Purpose:** Validates the low-level `downloadSingleVideo` method for MP3.

**Implementation (Executable Logic Only):**
* **Line 302:** Calls `downloadSingleVideo`.
* **Line 304-310:** Verifies success return and method calls on MP3 downloader.

### testDownloadSingleVideoInvalidFormat

**Purpose:** Tests single video download failure for unsupported formats.

**Implementation (Executable Logic Only):**
* **Line 317:** Calls `downloadSingleVideo` with 'AVI'.
* **Line 319-320:** Asserts failure and error message.

### testDownloadSingleVideoException

**Purpose:** Tests error recovery for single video download exceptions.

**Implementation (Executable Logic Only):**
* **Line 327:** Sets `downloadVideo` to raise an `Exception`.
* **Line 332:** Executes `downloadSingleVideo`.
* **Line 334-335:** Asserts failure and captures the exception message.

**Source Code:**
```python
    @patch('src.BatchDownloader.Mp4Downloader')
    def testDownloadSingleVideoException(self, mock_mp4_downloader_class):
        """Test single video download with exception."""
        mock_mp4_downloader = Mock()
        mock_mp4_downloader_class.return_value = mock_mp4_downloader
        mock_mp4_downloader.downloadVideo.side_effect = Exception("Network error")

        video_info = {'url': 'https://youtube.com/watch?v=1', 'title': 'Test Video'}
        folder_path = os.path.join(self.test_base_path, 'test')

        success, error = self.downloader.downloadSingleVideo(video_info, 'MP4', folder_path, 'highest')

        assert success is False
        assert error == "Network error"
```
