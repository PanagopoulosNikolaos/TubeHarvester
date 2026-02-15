# test_gui.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [TestSingleDownloadPanel](#testsingledownloadpanel) | Class | Tests for the single video download GUI component. |
| [TestBatchDownloadPanel](#testbatchdownloadpanel) | Class | Tests for the batch/playlist/channel download GUI component. |
| [TestYouTubeDownloaderGUI](#testyoutubedownloadergui) | Class | Tests for the main window and application lifecycle. |

### TestSingleDownloadPanel Methods
| Name | Type | Description |
|------|------|-------------|
| [setup_method](#setup_method) | Method | Initializes Tkinter root and the single download panel. |
| [teardown_method](#teardown_method) | Method | Cleans up the Tkinter environment. |
| [testBrowsePath](#testbrowsepath) | Method | Verifies directory selection dialog integration. |
| [testFetchResolutionsNoFormats](#testfetchresolutionsnoformats) | Method | Handles cases with no available video formats. |
| [testFetchResolutionsError](#testfetchresolutionserror) | Method | Handles network errors during resolution fetching. |
| [testStartDownloadMp4](#teststartdownloadmp4) | Method | Validates triggering of an MP4 download thread. |
| [testStartDownloadMp3](#teststartdownloadmp3) | Method | Validates triggering of an MP3 download thread. |
| [testStartDownloadMp4NoResolution](#teststartdownloadmp4noresolution) | Method | Validates validation logic for missing resolution select. |
| [testUpdateProgress](#testupdateprogress) | Method | Verifies progress bar value updates. |
| [testClearProgressBar](#testclearprogressbar) | Method | Verifies progress bar resetting. |
| [testLogMessage](#testlogmessage) | Method | Checks message insertion into the GUI text widget. |
| [testUpdateFormatColorMp4](#testupdateformatcolormp4) | Method | Verifies UI state changes for MP4 format. |
| [testUpdateFormatColorMp3](#testupdateformatcolormp3) | Method | Verifies UI state changes for MP3 format. |

### TestBatchDownloadPanel Methods
| Name | Type | Description |
|------|------|-------------|
| [testUpdateMaxVideosDisplayPlaylist](#testupdatemaxvideosdisplayplaylist) | Method | Checks default limits for playlist mode. |
| [testUpdateMaxVideosDisplayProfile](#testupdatemaxvideosdisplayprofile) | Method | Checks 'ALL' limit for profile scraping. |
| [testStartBatchDownloadPlaylistMode](#teststartbatchdownloadplaylistmode) | Method | Validates batch infrastructure for playlists. |
| [testStartBatchDownloadProfileMode](#teststartbatchdownloadprofilemode) | Method | Validates batch infrastructure for channels. |
| [testCancelDownload](#testcanceldownload) | Method | Verifies coordination with the BatchDownloader cancellation. |

## Overview
The `test_gui.py` file contains the unit test suite for the application's graphical user interface. It ensures that user interactions—such as button clicks, format selections, and path browsing—correctly trigger the underlying business logic in a threaded manner, while maintaining a responsive and accurate UI state.

---

## TestSingleDownloadPanel

**Class Responsibility:** Manages the testing of the `SingleDownloadPanel` component, simulating user input into Tkinter widgets and verifying that the component correctly configures `Mp4Downloader` and `Mp3Downloader` instances.

### setup_method

**Signature:**
```python
def setup_method(self)
```

**Purpose:** Prepares a headless Tkinter environment and a color-themed `SingleDownloadPanel`.

**Implementation (Executable Logic Only):**
* **Line 14-15:** `tk.Tk()` and `withdraw()` — Creates a hidden root window for widget parentage.
* **Line 16-26:** Color dictionary — Provides the required theme tokens for the custom GUI.
* **Line 27:** `SingleDownloadPanel(...)` — Instantiates the target component.

### testStartDownloadMp4

**Primary Library:** `threading`, `unittest.mock`  
**Purpose:** Validates that clicking "Download" for MP4 format correctly configures the downloader and starts a background thread.

#### Overview
This test populates the URL, path, and resolution fields of the GUI, then triggers the download logic. It verifies that an `Mp4Downloader` is instantiated with the GUI data and that a separate thread is started to prevent UI freezing.

#### Workflow (Executable Logic Only)

**Phase 1: Widget Population**
Simulates user typing into the GUI entries.
* **Line 86:** Inserts a test URL.
* **Line 87:** Inserts a test download path.
* **Line 88:** Sets the resolution variable to "720".

**Phase 2: Execution**
* **Line 90:** Calls `startDownload()`.

**Phase 3: Logic Verification**
* **Line 93-95:** Asserts that the downloader was told where to go and what resolution to use.
* **Line 98:** Verifies that `thread.start()` was called exactly once.

#### Source Code
```python
    @patch('src.GUI.Mp4Downloader')
    @patch('threading.Thread')
    def testStartDownloadMp4(self, mock_thread_class, mock_downloader_class):
        """Test starting MP4 download."""
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        # Set up GUI fields
        self.panel.url_entry.insert(0, "https://youtube.com/watch?v=test")
        self.panel.path_display.insert(0, "/test/path")
        self.panel.resolution_var.set("720")

        self.panel.startDownload()

        # Verify downloader was configured correctly
        mock_downloader.setUrl.assert_called_with("https://youtube.com/watch?v=test")
        mock_downloader.setPath.assert_called_with("/test/path")
        assert mock_downloader.resolution == 720

        # Verify thread was started
        mock_thread.start.assert_called_once()
```

---

## TestBatchDownloadPanel

**Class Responsibility:** Manages tests for the `BatchDownloadPanel`, focusing on the complex coordination between `PlaylistScraper`, `ChannelScraper`, and `BatchDownloader`.

### testStartBatchDownloadPlaylistMode

**Primary Library:** `src.PlaylistScraper`, `src.BatchDownloader`  
**Purpose:** Validates the multi-stage process of scraping a playlist and starting a batch download from the GUI.

#### Overview
This test mocks the scraper to return a fixed list of videos and the downloader to simulate a successful batch run. It ensures that the GUI correctly transitions between these stages when in "Playlist Download" mode.

#### Workflow (Executable Logic Only)
* **Phase 1 (Scraper Mock):** Configures `scrapePlaylist` to return one video and `getPlaylistTitle` to return "Test Playlist" (Lines 240-243).
* **Phase 2 (Downloader Mock):** Configures `downloadBatch` to report success (Lines 248-250).
* **Phase 3 (GUI Setup):** Enters URL and mode into the panel (Lines 257-259).
* **Phase 4 (Execution):** Triggers `startBatchDownload` (Line 261).
* **Phase 5 (UI State):** Verifies that the Download button is disabled and Cancel is enabled during execution (Lines 267-268).

---

## TestYouTubeDownloaderGUI

**Class Responsibility:** Verifies the instantiation of the top-level application window and the embedding of the functional panels within tabs.

### testRunGui

**Primary Library:** `tkinter`, `unittest.mock`  
**Purpose:** Validates the application entry point and main event loop start.

#### Workflow (Executable Logic Only)
* **Phase 1:** Mocks the `tk.Tk` class and its `mainloop`.
* **Phase 2:** Patches the `YouTubeDownloaderGUI` constructor.
* **Phase 3:** Calls `runGui()`.
* **Phase 4:** Asserts that a root window was created, the main GUI class was instantiated, and the execution was passed to `root.mainloop()` (Lines 395-397).
```
