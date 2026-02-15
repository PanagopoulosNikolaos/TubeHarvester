# BatchDownloader.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [BatchDownloader](#batchdownloader) | Class | Manages concurrent downloads of multiple YouTube videos. |
| [BatchDownloader.__init__](#batchdownloader__init__) | Function | Initializes the BatchDownloader with thread management. |
| [BatchDownloader.downloadBatch](#batchdownloaderdownloadbatch) | Function | Downloads a batch of videos concurrently. |
| [BatchDownloader.cancelDownload](#batchdownloadercanceldownload) | Function | Cancels the current batch download operation. |
| [BatchDownloader.downloadSingleVideo](#batchdownloaderdownloadsinglevideo) | Function | Downloads a single video using the appropriate converter. |
| [BatchDownloader.createFolderStructure](#batchdownloadercreatefolderstructure) | Function | Creates the folder structure for organized downloads. |

## Overview
The `BatchDownloader` module orchestrates concurrent video downloads using a thread pool. It handles the lifecycle of multiple download tasks, including folder organization, progress tracking, logging, and cancellation. It acts as a high-level manager that delegates actual download logic to `Mp4Downloader` and `Mp3Downloader`.

## Detailed Breakdown

## BatchDownloader

**Class Responsibility:** Manages concurrent downloads of multiple YouTube videos. This class uses a ThreadPoolExecutor to handle multiple downloads in parallel, tracking overall progress and allowing for cancellation.

### BatchDownloader.\_\_init\_\_

**Signature:**
```python
def __init__(self, max_workers=3, progress_callback=None, log_callback=None)
```

**Purpose:** Initializes the BatchDownloader with thread management.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| max_workers | int | No | 3 | Maximum number of concurrent downloads. |
| progress_callback | callable | No | None | Called with overall progress percentage. |
| log_callback | callable | No | None | Called with log messages. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def __init__(self, max_workers=3, progress_callback=None, log_callback=None):
        """
        Initializes the BatchDownloader with thread management.

        Args:
            max_workers (int): Maximum number of concurrent downloads (default: 3).
            progress_callback (callable, optional): Called with overall progress percentage.
            log_callback (callable, optional): Called with log messages.
        """
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_event = threading.Event()
        self.total_videos = 0
        self.completed_videos = 0
        self.lock = threading.Lock()
        self.last_progress_update = 0
```

**Implementation (Executable Logic Only):**
* **Line 26:** `self.max_workers = max_workers` — Sets the degree of parallelism.
* **Line 27:** `self.progress_callback = progress_callback` — Stores the progress reporter.
* **Line 28:** `self.log_callback = log_callback` — Stores the logger.
* **Line 29:** `self.cancel_event = threading.Event()` — Creates a thread-safe event flag for cancellation.
* **Line 32:** `self.lock = threading.Lock()` — Initializes a lock for synchronizing shared state access updates.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| threading.Event | External | Signal cancellation across threads | threading |
| threading.Lock | External | Protect shared counters | threading |

### BatchDownloader.downloadBatch

**Primary Library:** `concurrent.futures`
**Purpose:** Downloads a batch of videos concurrently.

#### Overview
This method executes the bulk download process. It validates input, prepares the filesystem, submits tasks to a thread pool, monitors their completion, and aggregates results. It also handles real-time progress updates and cancellation requests.

#### Signature
```python
def downloadBatch(self, video_list: list, format_type: str, base_path: str, quality: str = "highest") -> dict
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| video_list | list | Yes | — | List of dicts: `[{'url': str, 'title': str, 'folder': str}, ...]`. |
| format_type | str | Yes | — | 'MP4' or 'MP3'. |
| base_path | str | Yes | — | Base directory for downloads. |
| quality | str | No | "highest" | Quality setting (e.g., 'highest', '720p'). |

#### Returns
| Type | Description |
|------|-------------|
| dict | Results summary: `{'successful': int, 'failed': int, 'errors': [str, ...]}`. |

#### Raises
| Exception | Condition |
|-----------|-----------|
| Exception | Captures exceptions from individual threads to prevent partial batch failure from crashing the main process. |

#### Dependencies
* **Required Libraries:** `concurrent.futures` (ThreadPoolExecutor)
* **Internal Modules:** `self.createFolderStructure`, `self.downloadSingleVideo`

#### Workflow (Executable Logic Only)

**Phase 1: Initialization and Validation**
Resets counters and validates the input list.
* **Line 48:** `self.total_videos = len(video_list)` — Sets the total count for progress tracking.
* **Line 50:** `self.cancel_event.clear()` — Resets the cancellation flag.
* **Line 52:** `results = {'successful': 0, 'failed': 0, 'errors': []}` — Initializes the results accumulator.
* **Line 58:** `if not video_list:` — Checks for an empty input list.
* **Line 61:** `return results` — early exit if no videos.

**Phase 2: Preparation**
Sets up the file structure and logging.
* **Line 66:** `organized_paths = self.createFolderStructure(video_list, base_path, format_type)` — Creates necessary subdirectories before starting threads.

**Phase 3: Task Submission**
Submits download tasks to the thread pool.
* **Line 68:** `with ThreadPoolExecutor(max_workers=self.max_workers) as executor:` — Context manager for the thread pool.
* **Line 70:** `for video_info in video_list:` — Iterates over each video to prepare tasks.
* **Line 75:** `future = executor.submit(self.downloadSingleVideo, ...)` — Schedules the download task.
* **Line 82:** `future_to_video[future] = video_info` — Maps the future object back to video metadata for result tracking.

*Code Context:*
```python
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_video = {}
            for video_info in video_list:
                if self.cancel_event.is_set():
                    break
```

**Phase 4: Result Processing**
Iterates through completed futures, updates progress, and handles errors.
* **Line 84:** `for future in as_completed(future_to_video):` — Blocks until tasks complete.
* **Line 90:** `success, error_msg = future.result()` — Retrieves the return value from the worker thread.
* **Line 91:** `with self.lock:` — Enters critical section to update shared counters.
* **Line 92:** `self.completed_videos += 1` — Increments completion count.
* **Line 101:** `overall_progress = (self.completed_videos / self.total_videos) * 100` — Calculates percentage.
* **Line 103:** `self.progress_callback(int(overall_progress))` — Invokes the UI progress callback.

**Phase 5: Completion and Cancellation Check**
Finalizes the process logic.
* **Line 126:** `if self.cancel_event.is_set():` — Checks if the process was cancelled by user.
* **Line 133:** `return results` — Returns the aggregated statistics.

#### Source Code
```python
    def downloadBatch(self, video_list, format_type, base_path, quality="highest"):
        """
        Downloads a batch of videos concurrently.
        """
        self.total_videos = len(video_list)
        self.completed_videos = 0
        self.cancel_event.clear()

        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        if not video_list:
            if self.log_callback:
                self.log_callback("No videos to download")
            return results

        if self.log_callback:
            self.log_callback(f"Starting batch download of {self.total_videos} videos in {format_type} format")

        organized_paths = self.createFolderStructure(video_list, base_path, format_type)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_video = {}
            for video_info in video_list:
                if self.cancel_event.is_set():
                    break

                folder_path = organized_paths.get(video_info.get('folder', ''), base_path)
                future = executor.submit(
                    self.downloadSingleVideo,
                    video_info,
                    format_type,
                    folder_path,
                    quality
                )
                future_to_video[future] = video_info

            for future in as_completed(future_to_video):
                if self.cancel_event.is_set():
                    break

                video_info = future_to_video[future]
                try:
                    success, error_msg = future.result()
                    with self.lock:
                        self.completed_videos += 1
                        if success:
                            results['successful'] += 1
                        else:
                            results['failed'] += 1
                            results['errors'].append(f"{video_info['title']}: {error_msg}")
                            if self.log_callback:
                                self.log_callback(f"Failed: {video_info['title']} - {error_msg}")

                        overall_progress = (self.completed_videos / self.total_videos) * 100
                        if self.progress_callback:
                            self.progress_callback(int(overall_progress))

                        progress_percent = int(overall_progress)
                        if progress_percent > self.last_progress_update and (progress_percent % 5 == 0 or progress_percent == 100):
                            self.last_progress_update = progress_percent
                            if self.log_callback:
                                bar_length = 20
                                filled_length = int(bar_length * self.completed_videos // self.total_videos)
                                bar = '[' + '=' * filled_length + '>' + ' ' * (bar_length - filled_length - 1) + ']'
                                self.log_callback(f"Download progress: {bar} {progress_percent}% ({self.completed_videos}/{self.total_videos} videos)")

                except Exception as e:
                    with self.lock:
                        self.completed_videos += 1
                        results['failed'] += 1
                        results['errors'].append(f"{video_info['title']}: {str(e)}")
                        if self.log_callback:
                            self.log_callback(f"Error: {video_info['title']} - {str(e)}")

                        overall_progress = (self.completed_videos / self.total_videos) * 100
                        if self.progress_callback:
                            self.progress_callback(int(overall_progress))

        if self.cancel_event.is_set():
            if self.log_callback:
                self.log_callback("Batch download cancelled")
        else:
            if self.log_callback:
                self.log_callback(f"Batch download completed: {results['successful']} successful, {results['failed']} failed")

        return results
```

#### Usage Example
```python
downloader = BatchDownloader()
videos = [{'url': '...', 'title': 'video1', 'folder': 'group1'}]
stats = downloader.downloadBatch(videos, 'MP4', '/downloads')
```

### BatchDownloader.cancelDownload

**Signature:**
```python
def cancelDownload(self)
```

**Purpose:** Cancels the current batch download operation.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | BatchDownloader | Yes | — | The instance of the class. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def cancelDownload(self):
        """
        Cancels the current batch download operation.
        """
        self.cancel_event.set()
        if self.log_callback:
            self.log_callback("Cancelling batch download...")
```

**Implementation (Executable Logic Only):**
* **Line 139:** `self.cancel_event.set()` — Signals all threads to stop processing.
* **Line 140:** `if self.log_callback:` — Checks for logger.
* **Line 141:** `self.log_callback("Cancelling batch download...")` — Logs the cancellation request.

### BatchDownloader.downloadSingleVideo

**Primary Library:** `Mp4_Converter`, `Mp3_Converter`
**Purpose:** Downloads a single video using the appropriate converter based on format type.

#### Overview
Instantiates the correct downloader class (`Mp4Downloader` or `Mp3Downloader`), configures it with the video URL and path, sets the resolution if applicable, and executes the download.

#### Signature
```python
def downloadSingleVideo(self, video_info: dict, format_type: str, folder_path: str, quality: str) -> tuple
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| video_info | dict | Yes | — | Video metadata `{'url': str, 'title': str}`. |
| format_type | str | Yes | — | 'MP4' or 'MP3'. |
| folder_path | str | Yes | — | Destination directory. |
| quality | str | Yes | — | Target resolution/quality. |

#### Returns
| Type | Description |
|------|-------------|
| tuple | `(success: bool, error_message: str)`. |

#### Raises
| Exception | Condition |
|-----------|-----------|
| ValueError | If `format_type` is not supported. |
| Exception | Catches any download errors to return them as a result string. |

#### Workflow (Executable Logic Only)

**Phase 1: Preparation**
Sanitizes the filename.
* **Line 156:** `try:` — Error handling block.
* **Line 157:** `sanitized_title = sanitizeFilename(video_info['title'])` — Cleans title for filesystem safety.

**Phase 2: Format Selection and Configuration**
Branches logic based on MP4 or MP3 selection.
* **Line 159:** `if format_type.upper() == 'MP4':` — Checks for MP4.
* **Line 160:** `downloader = Mp4Downloader()` — Creates MP4 downloader instance.
* **Line 161:** `downloader.setUrl(video_info['url'])` — Sets URL.
* **Line 162:** `downloader.setPath(folder_path)` — Sets output directory.
* **Line 165:** `if quality and quality.lower() != "highest":` — Checks for custom resolution.
* **Line 173:** `downloader.downloadVideo(custom_title=sanitized_title)` — Executes video download.
* **Line 175:** `elif format_type.upper() == 'MP3':` — Checks for MP3.
* **Line 176:** `downloader = Mp3Downloader()` — Creates MP3 downloader instance.
* **Line 179:** `downloader.downloadAsMp3(custom_title=sanitized_title)` — Executes audio download.

**Phase 3: Result Return**
Returns success or error state.
* **Line 184:** `return True, ""` — Returns success tuple.
* **Line 186:** `except Exception as e:` — Catches failures.
* **Line 187:** `return False, str(e)` — Returns failure tuple with error message.

#### Source Code
```python
    def downloadSingleVideo(self, video_info, format_type, folder_path, quality):
        """
        Downloads a single video using the appropriate converter.
        """
        try:
            sanitized_title = sanitizeFilename(video_info['title'])
            
            if format_type.upper() == 'MP4':
                downloader = Mp4Downloader()
                downloader.setUrl(video_info['url'])
                downloader.setPath(folder_path)
                # Resolution mapping could be improved here
                # Pass the quality parameter to set the resolution
                if quality and quality.lower() != "highest":
                    try:
                        # Extract numeric value from quality (e.g., "720p" -> 720)
                        resolution = ''.join(filter(str.isdigit, quality))
                        if resolution:
                            downloader.resolution = resolution
                    except:
                        pass  # Use default resolution if parsing fails
                downloader.downloadVideo(custom_title=sanitized_title)

            elif format_type.upper() == 'MP3':
                downloader = Mp3Downloader()
                downloader.setUrl(video_info['url'])
                downloader.setPath(folder_path)
                downloader.downloadAsMp3(custom_title=sanitized_title)

            else:
                raise ValueError(f"Unsupported format: {format_type}")

            return True, ""

        except Exception as e:
            return False, str(e)
```

#### Common Issues & Related Functions
* **Issue:** Unsupported format raises ValueError.
* **`Mp4Downloader`**: Used for video downloads.
* **`Mp3Downloader`**: Used for audio extraction.

### BatchDownloader.createFolderStructure

**Primary Library:** `os`
**Purpose:** Creates the folder structure for organized downloads.

#### Overview
Determines the root directory based on format (Music vs Videos) and creates subdirectories for grouped videos (e.g., from different playlists).

#### Signature
```python
def createFolderStructure(self, video_list: list, base_path: str, format_type: str) -> dict
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| video_list | list | Yes | — | List of video items. |
| base_path | str | Yes | — | Root path. |
| format_type | str | Yes | — | 'MP4' or 'MP3'. |

#### Returns
| Type | Description |
|------|-------------|
| dict | Map of folder identifiers to absolute paths. |

#### Workflow (Executable Logic Only)

**Phase 1: Root Directory Selection**
Selects base folder based on media type.
* **Line 201:** `organized_paths = {}` — Initializes result map.
* **Line 203:** `if format_type.upper() == 'MP3':` — Checks input format.
* **Line 204:** `root_folder = os.path.join(base_path, "Music")` — Selects Music folder.
* **Line 206:** `root_folder = os.path.join(base_path, "Videos")` — Selects Videos folder.

**Phase 2: Grouping**
Groups videos by their folder attribute.
* **Line 208:** `folder_groups = {}` — Initializes group map.
* **Line 209:** `for video in video_list:` — Iterates videos.
* **Line 210:** `item_folder = video.get('folder', '')` — Extracts grouping key.
* **Line 213:** `folder_groups[item_folder].append(video)` — Groups videos.

**Phase 3: Directory Creation**
Creates physical directories.
* **Line 215:** `for item_folder, videos_in_group in folder_groups.items():` — Iterates groups.
* **Line 217:** `full_path = os.path.join(root_folder, item_folder)` — Constructs full path.
* **Line 221:** `os.makedirs(full_path, exist_ok=True)` — Creates directory.
* **Line 222:** `organized_paths[item_folder] = full_path` — Stores map entry.

#### Source Code
```python
    def createFolderStructure(self, video_list, base_path, format_type):
        """
        Creates the folder structure for organized downloads.
        """
        organized_paths = {}

        if format_type.upper() == 'MP3':
            root_folder = os.path.join(base_path, "Music")
        else:
            root_folder = os.path.join(base_path, "Videos")

        folder_groups = {}
        for video in video_list:
            item_folder = video.get('folder', '')
            if item_folder not in folder_groups:
                folder_groups[item_folder] = []
            folder_groups[item_folder].append(video)

        for item_folder, videos_in_group in folder_groups.items():
            if item_folder:
                full_path = os.path.join(root_folder, item_folder)
            else:
                full_path = root_folder

            os.makedirs(full_path, exist_ok=True)
            organized_paths[item_folder] = full_path

        return organized_paths
```