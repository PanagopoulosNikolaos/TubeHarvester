# PlaylistScraper.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [PlaylistScraper](#playlistscraper) | Class | Scrapes video information from YouTube playlists. |
| [PlaylistScraper.__init__](#playlistscraper__init__) | Function | Initializes the PlaylistScraper. |
| [PlaylistScraper.isYoutubeMix](#playlistscraperisyoutubemix) | Function | Checks if the playlist ID corresponds to a YouTube mix. |
| [PlaylistScraper.normalizePlaylistUrl](#playlistscrapernormalizeplaylisturl) | Function | Normalizes a playlist URL to a standard format. |
| [PlaylistScraper.scrapePlaylist](#playlistscraperscrapeplaylist) | Function | Extracts video list from a YouTube playlist. |
| [PlaylistScraper.getPlaylistTitle](#playlistscrapergetplaylisttitle) | Function | Retrieves the title of a YouTube playlist. |

## Overview
The `PlaylistScraper` module provides specialized functionality for parsing YouTube playlists. It handles standard user-created playlists as well as algorithmic "Mix" playlists, normalizing URLs and extracting video metadata (URL, title, duration) while handling pagination and rate limiting.

## Detailed Breakdown

## PlaylistScraper

**Class Responsibility:** Scrapes video information from YouTube playlists. This class provides functionality to extract video URLs, titles, and durations from standard playlists and YouTube algorithmic mixes.

### PlaylistScraper.\_\_init\_\_

**Signature:**
```python
def __init__(self, timeout=2.0, log_callback=None)
```

**Purpose:** Initializes the PlaylistScraper.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| timeout | float | No | 2.0 | Timeout between requests in seconds. |
| log_callback | callable | No | None | Called with log messages. |

**Returns:**
| Type | Description |
|------|-------------|
| None | - |

**Source Code:**
```python
    def __init__(self, timeout=2.0, log_callback=None):
        """
        Initializes the PlaylistScraper.

        Args:
            timeout (float): Timeout between requests in seconds (default: 2.0).
            log_callback (callable, optional): Called with log messages.
        """
        self.timeout = timeout
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)
```

**Implementation (Executable Logic Only):**
* **Line 24:** `self.timeout = timeout` — Stores the request delay.
* **Line 25:** `self.log_callback = log_callback` — Stores the logger.
* **Line 26:** `self.cookie_manager = CookieManager(...)` — Initializes the cookie manager.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| CookieManager | Internal | Cookie management | .CookieManager |

### PlaylistScraper.isYoutubeMix

**Signature:**
```python
def isYoutubeMix(self, playlist_id: str) -> bool
```

**Purpose:** Checks if the playlist ID corresponds to a YouTube mix (algorithmic playlist).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | PlaylistScraper | Yes | — | The instance of the class. |
| playlist_id | str | Yes | — | The playlist ID to check. |

**Returns:**
| Type | Description |
|------|-------------|
| bool | True if it's a mix, False otherwise. |

**Source Code:**
```python
    def isYoutubeMix(self, playlist_id):
        """
        Checks if the playlist ID corresponds to a YouTube mix.

        Args:
            playlist_id (str): The playlist ID to check.

        Returns:
            bool: True if it's a mix, False otherwise.
        """
        mix_prefixes = ['RD', 'RDE', 'RDCL', 'RDCLAK', 'RDAMVM', 'RDCM', 'RDEO', 'RDFM', 'RDKM', 'RDM', 'RDTM', 'RDV']
        return any(playlist_id.startswith(prefix) for prefix in mix_prefixes)
```

**Implementation (Executable Logic Only):**
* **Line 38:** `mix_prefixes = [...]` — Defines list of known Mix ID prefixes.
* **Line 39:** `return any(...)` — Checks if the ID starts with any known prefix.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| None | - | - | - |

### PlaylistScraper.normalizePlaylistUrl

**Signature:**
```python
def normalizePlaylistUrl(self, url: str) -> str
```

**Purpose:** Normalizes a playlist URL to a standard format, handling "Mix" URLs specifically.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | PlaylistScraper | Yes | — | The instance of the class. |
| url | str | Yes | — | The input YouTube URL. |

**Returns:**
| Type | Description |
|------|-------------|
| str | The normalized playlist URL. |

**Source Code:**
```python
    def normalizePlaylistUrl(self, url):
        """
        Normalizes a playlist URL to a standard format.

        Args:
            url (str): The input YouTube URL.

        Returns:
            str: The normalized playlist URL.
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if 'list' in query_params:
                playlist_id = query_params['list'][0]
                
                if self.isYoutubeMix(playlist_id):
                    video_id = query_params.get('v', [None])[0]
                    if video_id:
                        return f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                
                return f"https://www.youtube.com/playlist?list={playlist_id}"
            
            return url
            
        except Exception as e:
            logging.warning(f"Error normalizing URL: {e}")
            return url
```

**Implementation (Executable Logic Only):**
* **Line 52:** `parsed_url = urlparse(url)` — Parses the URL structure.
* **Line 53:** `query_params = parse_qs(parsed_url.query)` — Extracts query parameters.
* **Line 55:** `if 'list' in query_params:` — Checks for presence of playlist ID.
* **Line 58:** `if self.isYoutubeMix(playlist_id):` — Helper check for Mix IDs.
* **Line 61:** `return f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"` — Returns Mix URL format (requires video ID).
* **Line 63:** `return f"https://www.youtube.com/playlist?list={playlist_id}"` — Returns standard playlist URL format.
* **Line 65:** `return url` — Returns original if no list ID found.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| urllib.parse | External | URL parsing | urllib.parse |

### PlaylistScraper.scrapePlaylist

**Primary Library:** `yt_dlp`
**Purpose:** Extracts video list from a YouTube playlist.

#### Overview
This method uses `yt-dlp` to fetch metadata for all videos in a playlist. It handles the nuances of Mix playlists (which require different extraction flags) and converts the raw entries into a structured list of video dictionaries.

#### Signature
```python
def scrapePlaylist(self, url: str, max_videos: int = 200, progress_callback: callable = None) -> list
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | str | Yes | — | The playlist URL. |
| max_videos | int | No | 200 | Limit for videos scraped. |
| progress_callback | callable | No | None | Called with (current, total, percentage). |

#### Returns
| Type | Description |
|------|-------------|
| list | List of video info dicts. |

#### Raises
| Exception | Condition |
|-----------|-----------|
| Exception | Propagates errors during the scraping process. |

#### Dependencies
* **Required Libraries:** `yt_dlp`
* **Internal Modules:** `self.normalizePlaylistUrl`, `self.isYoutubeMix`

#### Workflow (Executable Logic Only)

**Phase 1: URL and Option Configuration**
Prepares URL and yt-dlp options based on playlist type.
* **Line 86:** `normalized_url = self.normalizePlaylistUrl(url)` — Standardizes input.
* **Line 91:** `is_mix = playlist_id and self.isYoutubeMix(playlist_id)` — Detects Mix type.
* **Line 104:** `ydl_opts['extract_flat'] = 'in_playlist'` — Sets special flag for Mixes.

**Phase 2: Metadata Extraction**
Executes yt-dlp to get playlist info.
* **Line 106:** `with yt_dlp.YoutubeDL(ydl_opts) as ydl:` — Context manager.
* **Line 108:** `playlist_info = ydl.extract_info(normalized_url, download=False)` — Fetches metadata.
* **Line 110:** `if is_mix and 'v' in query_params:` — Fallback for Mixes if direct extraction fails.

**Phase 3: Parsing Entries**
Iterates through results and formats data.
* **Line 117:** `if 'entries' in playlist_info...` — Validates results.
* **Line 118:** `entries = playlist_info['entries'][:max_videos]` — Enforces strict limit.
* **Line 121:** `for idx, entry in enumerate(entries, 1):` — Loops through videos.
* **Line 124:** `video_data = {...}` — Constructs video object.
* **Line 129:** `videos.append(video_data)` — Adds to result list.
* **Line 133:** `progress_callback(len(videos), total, percentage)` — Reports progress.

#### Source Code
```python
    def scrapePlaylist(self, url, max_videos=200, progress_callback=None):
        """
        Extracts video list from a YouTube playlist.
        """
        videos = []

        try:
            normalized_url = self.normalizePlaylistUrl(url)
            parsed_url = urlparse(normalized_url)
            query_params = parse_qs(parsed_url.query)
            playlist_id = query_params.get('list', [None])[0] if 'list' in query_params else None
            
            is_mix = playlist_id and self.isYoutubeMix(playlist_id)
            cookie_file = self.cookie_manager.getCookieFile()
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'javascript_executor': 'deno',
            }
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file
            
            if is_mix:
                ydl_opts['extract_flat'] = 'in_playlist'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    playlist_info = ydl.extract_info(normalized_url, download=False)
                except yt_dlp.DownloadError as e:
                    if is_mix and 'v' in query_params:
                        video_id = query_params['v'][0]
                        watch_url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                        playlist_info = ydl.extract_info(watch_url, download=False)
                    else:
                        raise e

                if 'entries' in playlist_info and playlist_info['entries']:
                    entries = playlist_info['entries'][:max_videos]
                    total = len(entries)
                    
                    for idx, entry in enumerate(entries, 1):
                        if entry:
                            video_url = f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                            video_data = {
                                'url': video_url,
                                'title': sanitizeFilename(entry.get('title', 'Unknown Title')),
                                'duration': entry.get('duration', 0)
                            }
                            videos.append(video_data)
                            
                            if progress_callback:
                                percentage = int((len(videos) / total) * 100)
                                progress_callback(len(videos), total, percentage)

                            time.sleep(self.timeout)
                else:
                    logging.warning(f"No entries found in playlist: {normalized_url}")

        except Exception as e:
            logging.error(f"Error scraping playlist: {e}")
            raise

        return videos
```

### PlaylistScraper.getPlaylistTitle

**Primary Library:** `yt_dlp`
**Purpose:** Retrieves the title of a YouTube playlist.

#### Overview
Extracts just the title metadata from a playlist URL, handling potential fallbacks for Mix playlists which might behave differently than standard playlists.

#### Signature
```python
def getPlaylistTitle(self, url: str) -> str
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | PlaylistScraper | Yes | — | The instance of the class. |
| url | str | Yes | — | The playlist URL. |

#### Returns
| Type | Description |
|------|-------------|
| str | The playlist title or "Unknown Playlist" on failure. |

#### Workflow (Executable Logic Only)

**Phase 1: Setup**
Normalizes URL and checks for Mix type.
* **Line 156:** `normalized_url = self.normalizePlaylistUrl(url)` — Standardizes input.
* **Line 161:** `is_mix = playlist_id and self.isYoutubeMix(playlist_id)` — Detects Mix type.

**Phase 2: Metadata Extraction**
Attempts to fetch title via `extract_info`.
* **Line 173:** `with yt_dlp.YoutubeDL(ydl_opts) as ydl:` — Context manager.
* **Line 175:** `info = ydl.extract_info(normalized_url, download=False)` — Fetches metadata.
* **Line 176:** `return sanitizeFilename(info.get('title', 'Unknown Playlist'))` — Returns cleaned title.

**Phase 3: Fallback**
Handles DownloadError for Mixes by trying an alternative URL structure.
* **Line 177:** `except yt_dlp.DownloadError as e:` — Catches failure.
* **Line 178:** `if is_mix and 'v' in query_params:` — Checks if fallback is possible.
* **Line 180:** `watch_url = ...` — Constructs specific watch URL.
* **Line 181:** `info = ydl.extract_info(watch_url, download=False)` — Retries metadata fetch.

#### Source Code
```python
    def getPlaylistTitle(self, url):
        """
        Retrieves the title of a YouTube playlist.
        """
        try:
            normalized_url = self.normalizePlaylistUrl(url)
            parsed_url = urlparse(normalized_url)
            query_params = parse_qs(parsed_url.query)
            playlist_id = query_params.get('list', [None])[0] if 'list' in query_params else None
            
            is_mix = playlist_id and self.isYoutubeMix(playlist_id)
            cookie_file = self.cookie_manager.getCookieFile()
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'javascript_executor': 'deno',
            }
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(normalized_url, download=False)
                    return sanitizeFilename(info.get('title', 'Unknown Playlist'))
                except yt_dlp.DownloadError as e:
                    if is_mix and 'v' in query_params:
                        video_id = query_params['v'][0]
                        watch_url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                        info = ydl.extract_info(watch_url, download=False)
                        return sanitizeFilename(info.get('title', 'Unknown Playlist'))
                    else:
                        raise e

        except Exception as e:
            logging.error(f"Error getting playlist title: {e}")
            return 'Unknown Playlist'
```