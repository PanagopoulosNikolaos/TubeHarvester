# GUI.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [SingleDownloadPanel](#singledownloadpanel) | Class | Panel for individual video downloads. |
| [SingleDownloadPanel.__init__](#singledownloadpanel__init__) | Function | Initializes user interface components. |
| [SingleDownloadPanel.buildGui](#singledownloadpanelbuildgui) | Function | Constructs the GUI layout for single downloads. |
| [SingleDownloadPanel.autoFetchResolutions](#singledownloadpanelautofetchresolutions) | Function | Periodically checks URL field to trigger resolution fetching. |
| [SingleDownloadPanel.browsePath](#singledownloadpanelbrowsepath) | Function | Opens directory selection dialog. |
| [SingleDownloadPanel.fetchResolutions](#singledownloadpanelfetchresolutions) | Function | Retrieves available video qualities from YouTube. |
| [SingleDownloadPanel.startDownload](#singledownloadpanelstartdownload) | Function | Initiates the download process in a separate thread. |
| [SingleDownloadPanel.updateProgress](#singledownloadpanelupdateprogress) | Function | Updates the progress bar UI. |
| [SingleDownloadPanel.clearProgressBar](#singledownloadpanelclearprogressbar) | Function | Resets progress bar to zero. |
| [SingleDownloadPanel.logMessage](#singledownloadpanellogmessage) | Function | Appends messages to status display. |
| [SingleDownloadPanel.updateFormatColor](#singledownloadpanelupdateformatcolor) | Function | Updates UI state based on format selection. |
| [BatchDownloadPanel](#batchdownloadpanel) | Class | Panel for batch video downloads (playlists/channels). |
| [BatchDownloadPanel.__init__](#batchdownloadpanel__init__) | Function | Initializes batch download interface. |
| [BatchDownloadPanel.buildGui](#batchdownloadpanelbuildgui) | Function | Constructs the GUI layout for batch operations. |
| [BatchDownloadPanel.autoFetchResolutions](#batchdownloadpanelautofetchresolutions) | Function | Periodically checks URL field for batch operations. |
| [BatchDownloadPanel.browsePath](#batchdownloadpanelbrowsepath) | Function | Opens directory selection dialog for batch downloads. |
| [BatchDownloadPanel.fetchResolutions](#batchdownloadpanelfetchresolutions) | Function | Fetches available resolutions from first video in list. |
| [BatchDownloadPanel.updateFormatColor](#batchdownloadpanelupdateformatcolor) | Function | Updates UI state for batch format selection. |
| [BatchDownloadPanel.populateQualityMenu](#batchdownloadpanelpopulatequalitymenu) | Function | Populates quality dropdown with standard options. |
| [BatchDownloadPanel.updateMaxVideosDisplay](#batchdownloadpanelupdatemaxvideosdisplay) | Function | Updates Max Videos field based on mode. |
| [BatchDownloadPanel.startBatchDownload](#batchdownloadpanelstartbatchdownload) | Function | Starts batch download in background thread. |
| [BatchDownloadPanel.cancelDownload](#batchdownloadpanelcanceldownload) | Function | Cancels ongoing batch download. |
| [BatchDownloadPanel.executeBatchDownload](#batchdownloadpanelexecutebatchdownload) | Function | Coordinates scraping and downloading process. |
| [BatchDownloadPanel.updateFetchProgress](#batchdownloadpanelupdatefetchprogress) | Function | Updates UI for data fetching phase. |
| [BatchDownloadPanel.updateProgress](#batchdownloadpanelupdateprogress) | Function | Updates the main batch download progress bar. |
| [BatchDownloadPanel.logMessage](#batchdownloadpanellogmessage) | Function | Logs a message to the batch status display. |
| [BatchDownloadPanel.displayStartupInfo](#batchdownloadpaneldisplaystartupinfo) | Function | Displays system info at startup. |
| [YouTubeDownloaderGUI](#youtubedownloadergui) | Class | Main application window and orchestrator. |
| [YouTubeDownloaderGUI.__init__](#youtubedownloadergui__init__) | Function | Sets up main window, themes, and tabs. |
| [runGui](#rungui) | Function | Entry point to run the application. |

## Overview
The `GUI.py` module implements the graphical user interface for TubeHarvester using Tkinter. It is structured into two main panels: `SingleDownloadPanel` for individual videos and `BatchDownloadPanel` for playlists/channels. The interface supports dark mode theming, real-time logging, threaded operations to prevent freezing, and dynamic resolution fetching.

## Detailed Breakdown

## SingleDownloadPanel

**Class Responsibility:** Panel for individual video downloads. Provides a GUI for entering a YouTube URL, selecting format and resolution, and tracking the download progress.

### SingleDownloadPanel.\_\_init\_\_

**Signature:**
```python
def __init__(self, parent, colors: dict)
```

**Purpose:** Initializes the SingleDownloadPanel.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| parent | widget | Yes | — | Parent container. |
| colors | dict | Yes | — | Theme color palette. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def __init__(self, parent, colors):
        """
        Initializes the SingleDownloadPanel.

        Args:
            parent: The parent widget.
            colors (dict): Theme color palette.
        """
        super().__init__(parent)
        self.master = parent
        self.colors = colors
        self.downloader = None
        self.default_download_path = str(Path.home() / "Downloads")
        self.buildGui()
```

### SingleDownloadPanel.buildGui

**Purpose:** Constructs the GUI components for the single download panel.

#### Overview
Builds the visual hierarchy including input fields for URL and path, options for format (MP4/MP3) and resolution, control buttons, and status/logging areas.

#### Signature
```python
def buildGui(self)
```

#### Workflow (Executable Logic Only)
**Phase 1: Layout Construction**
* **Line 41:** `main_frame = ttk.Frame(...)` — Creates container.
* **Line 45:** `url_path_frame = ttk.LabelFrame(...)` — Groups inputs.
* **Line 50:** `self.url_entry = ttk.Entry(...)` — URL input.
* **Line 55:** `self.path_display = ttk.Entry(...)` — Path input.
* **Line 63:** `options_frame = ttk.LabelFrame(...)` — Groups settings.
* **Line 68:** `self.format_var = tk.StringVar(value="MP4")` — State for format.
* **Line 77:** `self.resolution_menu = ttk.OptionMenu(...)` — Resolution dropdown.
* **Line 87:** `self.download_button = ttk.Button(...)` — Action trigger.

**Phase 2: Status Area**
* **Line 93:** `progress_log_frame = ttk.LabelFrame(...)` — Groups feedback.
* **Line 103:** `self.fetch_progress = ttk.Progressbar(...)` — Loading indicator.
* **Line 119:** `self.progress = ttk.Progressbar(...)` — Download indicator.
* **Line 126:** `self.message_screen = Text(...)` — Log output window.

**Phase 3: Initialization**
* **Line 135:** `self.master.after(1000, self.autoFetchResolutions)` — Starts polling.

#### Source Code
(Refer to source file for full GUI construction code)

### SingleDownloadPanel.autoFetchResolutions

**Signature:**
```python
def autoFetchResolutions(self)
```

**Purpose:** Periodically checks the URL field to trigger resolution fetching.

**Source Code:**
```python
    def autoFetchResolutions(self):
        """
        Periodically checks the URL field to trigger resolution fetching.
        """
        current_url = self.url_entry.get()
        if current_url and current_url != self.last_checked_url:
            self.last_checked_url = current_url
            threading.Thread(target=self.fetchResolutions, daemon=True).start()
        self.master.after(1000, self.autoFetchResolutions)
```

**Implementation (Executable Logic Only):**
* **Line 141:** `current_url = self.url_entry.get()` — Retrieves current URL.
* **Line 142:** `if current_url and current_url != self.last_checked_url:` — Detects change.
* **Line 144:** `threading.Thread(...).start()` — Fetches asynchronously.
* **Line 145:** `self.master.after(1000, ...)` — Loops check.

### SingleDownloadPanel.browsePath

**Signature:**
```python
def browsePath(self)
```

**Purpose:** Opens a directory selection dialog.

### SingleDownloadPanel.fetchResolutions

**Purpose:** Fetches available resolutions for the current YouTube URL.

#### Overview
Uses `Mp4Downloader` and `yt_dlp` to extract video metadata without downloading.

#### Signature
```python
def fetchResolutions(self)
```

#### Workflow (Executable Logic Only)
**Phase 1: Preparation**
* **Line 160:** `url = self.last_checked_url` — Gets target.
* **Line 187:** `with yt_dlp.YoutubeDL(opts) as ydl:` — Context manager.

**Phase 2: UI Update**
* **Line 207:** `menu.delete(0, 'end')` — Clears dropdown.
* **Line 212:** `menu.add_command(...)` — Adds found resolutions.

#### Source Code
(Refer to source file for detailed resolution extraction logic)

### SingleDownloadPanel.startDownload

**Signature:**
```python
def startDownload(self)
```

**Purpose:** Initializes and starts the download process in a separate thread.

**Source Code:**
```python
    def startDownload(self):
        """
        Initializes and starts the download process in a separate thread.
        """
        # ... logic to determine format and start thread ...
        if self.format_var.get() == "MP4":
            # ... MP4 logic ...
            download_thread = threading.Thread(target=self.downloader.downloadVideo)
        elif self.format_var.get() == "MP3":
            # ... MP3 logic ...
            download_thread = threading.Thread(target=self.downloader.downloadAsMp3)
        download_thread.start()
```

### SingleDownloadPanel.updateProgress

**Signature:**
```python
def updateProgress(self, percentage: int)
```

**Purpose:** Updates the progress bar UI.

### SingleDownloadPanel.clearProgressBar

**Signature:**
```python
def clearProgressBar(self)
```

**Purpose:** Resets the progress bar to zero.

### SingleDownloadPanel.logMessage

**Signature:**
```python
def logMessage(self, message: str)
```

**Purpose:** Appends a message to the status display area.

### SingleDownloadPanel.updateFormatColor

**Signature:**
```python
def updateFormatColor(self)
```

**Purpose:** Updates the UI state based on format selection.

---

## BatchDownloadPanel

**Class Responsibility:** Panel for batch video downloads (playlists/channels).

### BatchDownloadPanel.\_\_init\_\_

**Signature:**
```python
def __init__(self, parent, colors: dict)
```

### BatchDownloadPanel.buildGui

**Purpose:** Constructs the GUI components for the batch download panel.

#### Signature
```python
def buildGui(self)
```

#### Workflow (Executable Logic Only)
* **Line 313:** `url_path_frame = ...` — Input section.
* **Line 329:** `options_frame = ...` — Settings section.
* **Line 361:** `controls_frame = ...` — Buttons section.
* **Line 402:** `progress_log_frame = ...` — Feedback section.

### BatchDownloadPanel.autoFetchResolutions

**Signature:**
```python
def autoFetchResolutions(self)
```

### BatchDownloadPanel.browsePath

**Signature:**
```python
def browsePath(self)
```

### BatchDownloadPanel.fetchResolutions

**Purpose:** Fetches available resolutions from the first video in list.

#### Signature
```python
def fetchResolutions(self)
```

#### Workflow (Executable Logic Only)
* **Line 469:** `if 'list=' in url:` — Check for playlist.
* **Line 478:** `info = ydl.extract_info(fetch_url, download=False)` — Generic fetch.

### BatchDownloadPanel.updateFormatColor

**Signature:**
```python
def updateFormatColor(self)
```

### BatchDownloadPanel.populateQualityMenu

**Signature:**
```python
def populateQualityMenu(self)
```

### BatchDownloadPanel.updateMaxVideosDisplay

**Signature:**
```python
def updateMaxVideosDisplay(self, *args)
```

**Source Code:**
```python
    def updateMaxVideosDisplay(self, *args):
        """
        Updates the Max Videos field based on the selected mode.
        """
        if self.mode_var.get() == "Profile Scrape":
            self.max_videos_var.set("ALL")
        else:
            self.max_videos_var.set("200")
```

### BatchDownloadPanel.startBatchDownload

**Signature:**
```python
def startBatchDownload(self)
```

**Purpose:** Starts batch download in background thread.

### BatchDownloadPanel.cancelDownload

**Signature:**
```python
def cancelDownload(self)
```

### BatchDownloadPanel.executeBatchDownload

**Purpose:** Coordinates scraping and downloading process.

#### Signature
```python
def executeBatchDownload(self, url, base_path, format_type, quality, max_videos, mode)
```

#### Workflow (Executable Logic Only)
* **Phase 1 (Scraping):** Uses `PlaylistScraper` or `ChannelScraper`.
* **Phase 2 (Downloading):** Uses `BatchDownloader`.

### BatchDownloadPanel.updateFetchProgress

**Signature:**
```python
def updateFetchProgress(self, current: int, total: int, percentage: int)
```

### BatchDownloadPanel.updateProgress

**Signature:**
```python
def updateProgress(self, percentage: int)
```

### BatchDownloadPanel.logMessage

**Signature:**
```python
def logMessage(self, message: str)
```

### BatchDownloadPanel.displayStartupInfo

**Signature:**
```python
def displayStartupInfo(self)
```

---

## YouTubeDownloaderGUI

**Class Responsibility:** Main application window and orchestrator.

### YouTubeDownloaderGUI.\_\_init\_\_

**Signature:**
```python
def __init__(self, master: tk.Tk)
```

**Purpose:** Sets up main window, themes, and tabs.

#### Workflow (Executable Logic Only)
* **Line 778:** `self.colors = {...}` — GitHub Dark Dimmed palette.
* **Line 794:** `style = ttk.Style(...)` — Configures theme.
* **Line 898:** `self.notebook = ttk.Notebook(...)` — Tab container.
* **Line 906:** `self.single_panel = SingleDownloadPanel(...)` — Tab 1.
* **Line 914:** `self.batch_panel = BatchDownloadPanel(...)` — Tab 2.

### runGui

**Signature:**
```python
def runGui()
```

**Purpose:** Entry point to run the application.

**Source Code:**
```python
def runGui():
    """
    Initializes and runs the TubeHarvester GUI application.
    """
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()
```