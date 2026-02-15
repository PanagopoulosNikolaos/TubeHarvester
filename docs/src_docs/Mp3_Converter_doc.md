# Mp3_Converter.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [Mp3Downloader](#mp3downloader) | Class | Handles downloading YouTube videos and converting to MP3. |
| [Mp3Downloader.__init__](#mp3downloader__init__) | Function | Initializes the Mp3Downloader. |
| [Mp3Downloader.setUrl](#mp3downloaderseturl) | Function | Sets the URL of the YouTube video to download. |
| [Mp3Downloader.setPath](#mp3downloadersetpath) | Function | Sets the path where the downloaded MP3 file will be saved. |
| [Mp3Downloader.getDefaultDownloadPath](#mp3downloadergetdefaultdownloadpath) | Function | Gets the default path where downloaded files are saved. |
| [Mp3Downloader.downloadAsMp3](#mp3downloaderdownloadasmp3) | Function | Downloads the audio from a YouTube video as an MP3 file. |
| [Mp3Downloader.progressHook](#mp3downloaderprogresshook) | Function | Updates the progress via the provided callback. |

## Overview
The `Mp3_Converter` module is a specialized downloader that focuses on extracting audio from YouTube videos. It configures `yt-dlp` to download the best available audio stream and convert it to high-quality MP3 format using FFmpeg post-processing.

## Detailed Breakdown

## Mp3Downloader

**Class Responsibility:** Handles the downloading of YouTube videos and converting them to MP3 files. This class provides methods to set the video URL, save path, and download the audio content using yt-dlp.

### Mp3Downloader.\_\_init\_\_

**Signature:**
```python
def __init__(self, url=None, save_path=None, progress_callback=None, log_callback=None)
```

**Purpose:** Initializes the Mp3Downloader with URL, save path, and callback functions.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | str | No | None | The URL of the YouTube video to download. |
| save_path | str | No | None | The destination directory. |
| progress_callback | callable | No | None | Called with download progress percentage. |
| log_callback | callable | No | None | Called with log messages. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def __init__(self, url=None, save_path=None, progress_callback=None, log_callback=None):
        """
        Initializes the Mp3Downloader with URL, save path, and callback functions.

        Args:
            url (str, optional): The URL of the YouTube video to download.
            save_path (str, optional): The path where the downloaded MP3 file will be saved.
            progress_callback (callable, optional): Called with the percentage of download progress.
            log_callback (callable, optional): Called with log messages.
        """
        self.url = url
        self.save_path = save_path if save_path else self.getDefaultDownloadPath()
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)
```

**Implementation (Executable Logic Only):**
* **Line 27:** `self.url = url` — Stores the target URL.
* **Line 28:** `self.save_path = ...` — Sets the download path (defaults to Downloads folder).
* **Line 29:** `self.progress_callback = progress_callback` — Stores the progress listener.
* **Line 30:** `self.log_callback = log_callback` — Stores the logger.
* **Line 31:** `self.cookie_manager = CookieManager(...)` — Initializes authentication handling.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| CookieManager | Internal | Cookie management | .CookieManager |

### Mp3Downloader.setUrl

**Signature:**
```python
def setUrl(self, url: str)
```

**Purpose:** Sets the URL of the YouTube video to download.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp3Downloader | Yes | — | The instance of the class. |
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
* **Line 40:** `self.url = url` — Updates the internal URL state.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| None | - | - | - |

### Mp3Downloader.setPath

**Signature:**
```python
def setPath(self, save_path: str)
```

**Purpose:** Sets the path where the downloaded MP3 file will be saved.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp3Downloader | Yes | — | The instance of the class. |
| save_path | str | Yes | — | The destination directory. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def setPath(self, save_path):
        """
        Sets the path where the downloaded MP3 file will be saved.

        Args:
            save_path (str, optional): The destination directory. Defaults to the Downloads folder.
        """
        self.save_path = save_path if save_path else self.getDefaultDownloadPath()
```

**Implementation (Executable Logic Only):**
* **Line 49:** `self.save_path = save_path if save_path else self.getDefaultDownloadPath()` — Updates path, falling back to default if None/empty.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| self.getDefaultDownloadPath | Internal | Fallback path provider | Mp3Downloader |

### Mp3Downloader.getDefaultDownloadPath

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
            str: The default path (user's Downloads directory).
        """
        home_directory = os.path.expanduser('~')
        return os.path.join(home_directory, 'Downloads')
```

**Implementation (Executable Logic Only):**
* **Line 59:** `home_directory = os.path.expanduser('~')` — Resolves the user's home directory.
* **Line 60:** `return os.path.join(home_directory, 'Downloads')` — Constructs path to Downloads.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| os.path | External | Path manipulation | os |

### Mp3Downloader.downloadAsMp3

**Primary Library:** `yt_dlp`
**Purpose:** Downloads the audio from a YouTube video as an MP3 file.

#### Overview
Configures `yt-dlp` with specific options for audio extraction, FFmpeg conversion to MP3 (192kbps), and custom HTTP headers to mimic a browser. It performs a two-step process: fetching metadata to determine the title, then executing the download.

#### Signature
```python
def downloadAsMp3(self, custom_title: str = None) -> str
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp3Downloader | Yes | — | The instance of the class. |
| custom_title | str | No | None | Custom title for the file. |

#### Returns
| Type | Description |
|------|-------------|
| str | The path where the MP3 file was saved. |

#### Raises
| Exception | Condition |
|-----------|-----------|
| yt_dlp.DownloadError | If the download fails (restricted video, network error). |
| Exception | For unexpected runtime errors. |

#### Dependencies
* **Required Libraries:** `yt_dlp`
* **External Tools:** `FFmpeg` (Required for audio conversion)
* **Internal Modules:** `CookieManager`

#### Workflow (Executable Logic Only)

**Phase 1: Configuration**
Sets up common headers and cookie file.
* **Line 76:** `cookie_file = self.cookie_manager.getCookieFile()` — Retrieves authentication.
* **Line 79:** `common_opts = {...}` — Defines baseline yt-dlp configuration (headers, user-agent).

**Phase 2: Metadata Fetch**
Retrieves video title to determine filename.
* **Line 112:** `with yt_dlp.YoutubeDL(common_opts) as ydl:` — Context manager.
* **Line 113:** `info = ydl.extract_info(self.url, download=False)` — Fetches metadata.
* **Line 114:** `title = sanitizeFilename(...)` — Cleans title for filesystem.

**Phase 3: Download and Conversion**
Executes audio download with FFmpeg post-processing.
* **Line 119:** `options = common_opts.copy()` — Clones base options.
* **Line 120:** `options.update({...})` — Adds format-specific options:
    * `format`: 'bestaudio/best'
    * `postprocessors`: FFmpegExtractAudio to mp3 at 192kbps.
* **Line 132:** `with yt_dlp.YoutubeDL(options) as ydl:` — New instance for download.
* **Line 133:** `ydl.download([self.url])` — Starts download.
* **Line 138:** `return self.save_path` — Returns success path.

**Phase 4: Error Handling**
Catches and logs specific failures.
* **Line 140:** `except yt_dlp.DownloadError as e:` — Catches download-specific errors.
* **Line 142:** `if any(...)` — Checks for known restriction messages.
* **Line 150:** `raise` — Re-raises exception for caller handling.

#### Source Code
```python
    def downloadAsMp3(self, custom_title=None):
        """
        Downloads the audio from a YouTube video as an MP3 file.
        """
        try:
            cookie_file = self.cookie_manager.getCookieFile()
            
            # Common options for modern YouTube handling (abbreviated for docs)
            common_opts = {
                'http_headers': { ... },
                'extractor_args': { ... },
                'cookiefile': cookie_file,
                'noplaylist': True,
                # ...
            }

            # First extraction to get title
            with yt_dlp.YoutubeDL(common_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                title = sanitizeFilename(custom_title or info.get('title', 'Unknown Title'))

            if self.log_callback:
                self.log_callback(f"Download started: \"{title}\" - Format: MP3. Saved at: \"{self.save_path}\"")

            options = common_opts.copy()
            options.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.save_path, f'{title}.%(ext)s'),
                'progress_hooks': [self.progressHook],
                'keepvideo': False,
            })

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])

            if self.log_callback:
                self.log_callback(f"Download complete at {self.save_path}")

            return self.save_path
            
        except yt_dlp.DownloadError as e:
            err_msg = str(e)
            if any(x in err_msg for x in ["Private video", "unavailable", "Copyright", "Sign in"]):
                if self.log_callback:
                    self.log_callback(f"Video restricted or requires authentication: {title or 'Unknown Title'}")
                logging.info(f"Restricted video skipped: {self.url}")
            else:
                logging.error(f"yt-dlp error: {e}")
                if self.log_callback:
                    self.log_callback(f"yt-dlp error: {e}")
            raise
            
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            if self.log_callback:
                self.log_callback(f"Unexpected error: {e}")
            raise
```

### Mp3Downloader.progressHook

**Signature:**
```python
def progressHook(self, d: dict)
```

**Purpose:** Updates the progress via the provided callback (internal hook).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | Mp3Downloader | Yes | — | The instance of the class. |
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
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                percentage = (downloaded_bytes / total_bytes) * 100
                if self.progress_callback:
                    self.progress_callback(int(percentage))
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(100)
```

**Implementation (Executable Logic Only):**
* **Line 165:** `if d['status'] == 'downloading':` — Checks if currently downloading.
* **Line 166:** `total_bytes = ...` — Gets total size estimate.
* **Line 169:** `percentage = ...` — Calculates progress.
* **Line 171:** `self.progress_callback(int(percentage))` — Invokes callback.
* **Line 172:** `elif d['status'] == 'finished':` — Checks if complete.
* **Line 174:** `self.progress_callback(100)` — Ensures 100% is reported.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| None | - | - | - |