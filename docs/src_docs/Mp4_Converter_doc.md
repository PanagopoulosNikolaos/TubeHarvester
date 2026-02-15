# Mp4_Converter.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [Mp4Downloader](#mp4downloader) | Class | Handles the downloading of YouTube videos as MP4 files. |
| [Mp4Downloader.__init__](#mp4downloader__init__) | Function | Initializes the Mp4Downloader. |
| [Mp4Downloader.getDefaultDownloadPath](#mp4downloadergetdefaultdownloadpath) | Function | Gets the default path where downloaded files are saved. |
| [Mp4Downloader.setUrl](#mp4downloaderseturl) | Function | Sets the URL of the YouTube video to download. |
| [Mp4Downloader.setPath](#mp4downloadersetpath) | Function | Sets the path where the downloaded MP4 file will be saved. |
| [Mp4Downloader.downloadVideo](#mp4downloaderdownloadvideo) | Function | Downloads the video from YouTube in MP4 format. |
| [Mp4Downloader.fetchVideoInfo](#mp4downloaderfetchvideoinfo) | Function | Fetches information about the video without downloading. |
| [Mp4Downloader.progressHook](#mp4downloaderprogresshook) | Function | Updates the progress via the provided callback. |
| [Mp4Downloader.handleError](#mp4downloaderhandleerror) | Function | Handles errors that occur during the download process. |

## Overview
The `Mp4_Converter` module manages video downloads, ensuring files are saved in the compatible MP4 format. It provides flexible resolution selection (e.g., 1080p), handles video/audio stream merging, and includes robustness features like cookie authentication and error recovery.

## Detailed Breakdown

## Mp4Downloader

**Class Responsibility:** Handles the downloading of YouTube videos as MP4 files. This class provides methods to select resolutions, set download paths, and manage the download process using yt-dlp.

### Mp4Downloader.\_\_init\_\_

**Signature:**
```python
def __init__(self, progress_callback=None, log_callback=None)
```

**Purpose:** Initializes the Mp4Downloader with callback functions.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| progress_callback | callable | No | None | Called with download progress percentage. |
| log_callback | callable | No | None | Called with log messages. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def __init__(self, progress_callback=None, log_callback=None):
        """
        Initializes the Mp4Downloader with callback functions.

        Args:
            progress_callback (callable, optional): Called with the percentage of download progress.
            log_callback (callable, optional): Called with log messages.
        """
        self.url = None
        self.path = self.getDefaultDownloadPath()
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.video_title = None
        self.resolution = "1080"  # Default target
        self.cookie_manager = CookieManager(log_callback=self.log_callback)
```

**Implementation (Executable Logic Only):**
* **Line 23:** `self.url = None` — Initializes URL state.
* **Line 24:** `self.path = self.getDefaultDownloadPath()` — Sets default download location.
* **Line 28:** `self.resolution = "1080"` — Sets default resolution target.
* **Line 29:** `self.cookie_manager = CookieManager(...)` — Initializes authentication.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| CookieManager | Internal | Cookie management | .CookieManager |

### Mp4Downloader.getDefaultDownloadPath

**Signature:**
```python
def getDefaultDownloadPath() -> str
```

**Purpose:** Gets the default path where downloaded files are saved (static method).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| None | - | - | - | - |

**Returns:**
| Type | Description |
|------|-------------|
| str | The user's Downloads directory. |

**Source Code:**
```python
    @staticmethod
    def getDefaultDownloadPath():
        """
        Gets the default path where downloaded files are saved.

        Returns:
            str: The user's Downloads directory.
        """
        return os.path.join(os.path.expanduser('~'), 'Downloads')
```

**Implementation (Executable Logic Only):**
* **Line 39:** `return os.path.join(os.path.expanduser('~'), 'Downloads')` — Constructs path to Downloads.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| os.path | External | Path manipulation | os |

### Mp4Downloader.setUrl

**Signature:**
```python
def setUrl(self, url: str)
```

**Purpose:** Sets the URL of the YouTube video to download.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp4Downloader | Yes | — | The instance of the class. |
| url | str | Yes | — | The URL of the YouTube video. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def setUrl(self, url):
        """
        Sets the URL of the YouTube video to download.

        Args:
            url (str): The URL of the YouTube video.
        """
        self.url = url
```

**Implementation (Executable Logic Only):**
* **Line 48:** `self.url = url` — Updates internal URL state.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| None | - | - | - |

### Mp4Downloader.setPath

**Signature:**
```python
def setPath(self, path: str)
```

**Purpose:** Sets the path where the downloaded MP4 file will be saved.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp4Downloader | Yes | — | The instance of the class. |
| path | str | No | None | The destination directory. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def setPath(self, path):
        """
        Sets the path where the downloaded MP4 file will be saved.

        Args:
            path (str, optional): The destination directory.
        """
        self.path = path or self.getDefaultDownloadPath()
        os.makedirs(self.path, exist_ok=True)
```

**Implementation (Executable Logic Only):**
* **Line 57:** `self.path = path or self.getDefaultDownloadPath()` — Sets path with fallback.
* **Line 58:** `os.makedirs(self.path, exist_ok=True)` — Ensures directory exists.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| os.makedirs | External | Directory creation | os |

### Mp4Downloader.downloadVideo

**Primary Library:** `yt_dlp`
**Purpose:** Downloads the video from YouTube in MP4 format.

#### Overview
Configures `yt-dlp` to download the best video and audio streams that meet the resolution criteria and merges them into an MP4 container.

#### Signature
```python
def downloadVideo(self, custom_title: str = None)
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp4Downloader | Yes | — | The instance of the class. |
| custom_title | str | No | None | Custom title for the file. |

#### Raises
| Exception | Condition |
|-----------|-----------|
| ValueError | If the URL is not set. |
| Exception | Passed to `handleError` for logging. |

#### Dependencies
* **Required Libraries:** `yt_dlp`
* **External Tools:** `FFmpeg` (Merging streams)
* **Internal Modules:** `self.handleError`

#### Workflow (Executable Logic Only)

**Phase 1: Validation**
Checks if URL is present.
* **Line 70:** `if not self.url:` — Checks state.
* **Line 71:** `raise ValueError("URL is not set.")` — Halts if invalid.

**Phase 2: Configuration**
Sets up extensive download options.
* **Line 73:** `ydl_opts = {...}` — Video format selection, output template, merging headers.
    * `format`: Complex selector for best video <= resolution + best audio.
    * `postprocessors`: FFmpegMerger/VideoConvertor to mp4.
    * `javascript_executor`: configured for Deno.

**Phase 3: Execution**
Runs the download.
* **Line 115:** `with yt_dlp.YoutubeDL(ydl_opts) as ydl:` — Context manager.
* **Line 116:** `info = ydl.extract_info(self.url, download=True)` — Downloads video.
* **Line 117:** `self.video_title = sanitizeFilename(info.get('title', 'Unknown'))` — Updates title state.

**Phase 4: Completion and Error Handling**
Logs success or delegates errors.
* **Line 119:** `if self.log_callback:` — Checks logger.
* **Line 120:** `self.log_callback(f"Download complete: {self.video_title}")` — Logs success.
* **Line 122:** `except Exception as e:` — Catches failures.
* **Line 123:** `self.handleError(e)` — Delegates to error handler.

#### Source Code
```python
    def downloadVideo(self, custom_title=None):
        """
        Downloads the video from YouTube in MP4 format.
        """
        if not self.url:
            raise ValueError("URL is not set.")

        ydl_opts = {
            'format': f'bestvideo[height<={self.resolution}]+bestaudio/best[height<={self.resolution}]/best',
            'outtmpl': os.path.join(self.path, f"{custom_title or '%(title)s'}.%(ext)s"),
            'progress_hooks': [self.progressHook],
            'noplaylist': True,
            'merge_output_format': 'mp4',
            # ... (truncated for brevity in template, but full logic represented)
            'javascript_executor': '/home/ice/.deno/bin/deno',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                self.video_title = sanitizeFilename(info.get('title', 'Unknown'))
                
            if self.log_callback:
                self.log_callback(f"Download complete: {self.video_title}")

        except Exception as e:
            self.handleError(e)
```

### Mp4Downloader.fetchVideoInfo

**Primary Library:** `yt_dlp`
**Purpose:** Fetches information about the video without downloading.

#### Overview
Performs a lightweight metadata extraction to retrieve details like title and duration before committing to a download.

#### Signature
```python
def fetchVideoInfo(self) -> dict
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp4Downloader | Yes | — | The instance of the class. |

#### Returns
| Type | Description |
|------|-------------|
| dict | The information extracted by yt-dlp. |

#### Raises
| Exception | Condition |
|-----------|-----------|
| ValueError | If URL is not set. |

#### Workflow (Executable Logic Only)

**Phase 1: Validation**
* **Line 132:** `if not self.url:` — Checks state.
* **Line 133:** `raise ValueError("URL is not set")` — Halts.

**Phase 2: Execution**
* **Line 135:** `opts = {...}` — Light options (no playlist, quiet).
* **Line 150:** `with yt_dlp.YoutubeDL(opts) as ydl:` — Context manager.
* **Line 151:** `return ydl.extract_info(self.url, download=False)` — Fetches info.

#### Source Code
```python
    def fetchVideoInfo(self):
        """
        Fetches information about the video without downloading.
        """
        if not self.url:
            raise ValueError("URL is not set")

        opts = {
            'noplaylist': True, 
            'cookiefile': self.cookie_manager.getCookieFile(),
            'javascript_executor': '/home/ice/.deno/bin/deno',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'hl': 'en-US',
                    'gl': 'US',
                }
            },
            'youtube_include_dash_manifest': True,
            'youtube_include_hls_manifest': True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(self.url, download=False)
```

### Mp4Downloader.progressHook

**Signature:**
```python
def progressHook(self, d: dict)
```

**Purpose:** Updates the progress via the provided callback.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp4Downloader | Yes | — | The instance of the class. |
| d | dict | Yes | — | Dictionary with download progress information. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def progressHook(self, d):
        """
        Updates the progress via the provided callback.

        Args:
            d (dict): Dictionary with download progress information.
        """
        if d['status'] == 'downloading' and self.progress_callback:
            p = d.get('_percent_str', '0%').replace('%','')
            try:
                self.progress_callback(int(float(p)))
            except ValueError:
                pass
```

**Implementation (Executable Logic Only):**
* **Line 160:** `if d['status'] == 'downloading' and self.progress_callback:` — Validates state.
* **Line 161:** `p = d.get('_percent_str', '0%').replace('%','')` — Extracts percent string.
* **Line 163:** `self.progress_callback(int(float(p)))` — Converts to int and calls back.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| None | - | - | - |

### Mp4Downloader.handleError

**Signature:**
```python
def handleError(self, e: Exception)
```

**Purpose:** Handles errors that occur during the download process.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp4Downloader | Yes | — | The instance of the class. |
| e | Exception | Yes | — | The exception to handle. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def handleError(self, e):
        """
        Handles errors that occur during the download process.

        Args:
            e (Exception): The exception to handle.
        """
        err_msg = str(e)
        if any(x in err_msg for x in ["Private", "unavailable", "Sign in"]):
            msg = "Video restricted or requires authentication."
        else:
            msg = f"Error: {err_msg}"
        
        logging.error(msg)
        if self.log_callback:
            self.log_callback(msg)
```

**Implementation (Executable Logic Only):**
* **Line 175:** `if any(...)` — Checks for specific error keywords.
* **Line 180:** `logging.error(msg)` — Logs to system log.
* **Line 181:** `if self.log_callback:` — Checks user callback.
* **Line 182:** `self.log_callback(msg)` — Logs to UI.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| logging | External | Logging errors | logging |