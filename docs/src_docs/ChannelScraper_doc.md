# ChannelScraper.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [ChannelScraper](#channelscraper) | Class | Scrapes content from YouTube channels. |
| [ChannelScraper.__init__](#channelscraper__init__) | Function | Initializes the ChannelScraper. |
| [ChannelScraper.scrapeChannel](#channelscraperscrapechannel) | Function | Scrapes playlists and videos from a channel. |
| [ChannelScraper.normalizeChannelUrl](#channelscrapernormalizechannelurl) | Function | Normalizes various YouTube channel URL formats. |
| [ChannelScraper.getChannelName](#channelscrapergetchannelname) | Function | Retrieves the name of the YouTube channel. |
| [ChannelScraper.getChannelPlaylists](#channelscrapergetchannelplaylists) | Function | Retrieves all playlists from a channel. |
| [ChannelScraper.getStandaloneVideos](#channelscrapergetstandalonevideos) | Function | Retrieves standalone videos from a channel. |

## Overview
The `ChannelScraper` module is responsible for extracting comprehensive content from YouTube channels. It identifies and retrieves both organized playlists and standalone video uploads, leveraging `yt-dlp` for metadata extraction and coordinating with the `PlaylistScraper` for deep content traversals.

## Detailed Breakdown

## ChannelScraper

**Class Responsibility:** Scrapes content from YouTube channels. This class extracts playlists and standalone videos from a channel URL, coordinating with PlaylistScraper for detailed playlist extraction.

### ChannelScraper.\_\_init\_\_

**Signature:**
```python
def __init__(self, timeout=2.0, log_callback=None)
```

**Purpose:** Initializes the ChannelScraper.

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
        Initializes the ChannelScraper.

        Args:
            timeout (float): Timeout between requests in seconds (default: 2.0).
            log_callback (callable, optional): Called with log messages.
        """
        self.timeout = timeout
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)
```

**Implementation (Executable Logic Only):**
* **Line 24:** `self.timeout = timeout` — Stores the delay between network requests.
* **Line 25:** `self.log_callback = log_callback` — Stores the logging function.
* **Line 26:** `self.cookie_manager = CookieManager(...)` — Initializes the cookie manager for authenticated requests.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| CookieManager | Internal | Handle authentication cookies | .CookieManager |

### ChannelScraper.scrapeChannel

**Primary Library:** `PlaylistScraper`
**Purpose:** Scrapes playlists and videos from a channel.

#### Overview
This is the main entry point for channel processing. It normalizes the URL, fetches metadata, iterates through all playlists on the channel using `PlaylistScraper`, and finally retrieves standalone videos. It reports progress recursively.

#### Signature
```python
def scrapeChannel(self, url: str, max_videos_per_playlist: int = 200, progress_callback: callable = None) -> dict
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | str | Yes | — | The channel URL. |
| max_videos_per_playlist | int | No | 200 | Limit for videos per playlist. |
| progress_callback | callable | No | None | Called with progress updates. |

#### Returns
| Type | Description |
|------|-------------|
| dict | Scraped channel content: `{'channel_name': str, 'playlists': list, 'standalone_videos': list}`. |

#### Raises
| Exception | Condition |
|-----------|-----------|
| Exception | Propagates critical failures in channel scraping. |

#### Dependencies
* **Required Libraries:** `time` (Rate limiting)
* **Internal Modules:** `PlaylistScraper` (Nested scraping), `self.getChannelPlaylists`, `self.getStandaloneVideos`

#### Workflow (Executable Logic Only)

**Phase 1: Setup and Metadata**
initializes the result structure and fetches basic channel info.
* **Line 47:** `channel_url = self.normalizeChannelUrl(url)` — Standardizes the input URL.
* **Line 48:** `channel_info['channel_name'] = self.getChannelName(channel_url)` — Fetches the channel title.

**Phase 2: Playlist Discovery**
Finds all playlists associated with the channel.
* **Line 53:** `playlists = self.getChannelPlaylists(channel_url)` — Retrieves list of playlist URLs.
* **Line 54:** `total_tasks = len(playlists) + 1` — Calculates total work units (playlists + 1 for standalone videos).

**Phase 3: Playlist Iteration**
Process each playlist found.
* **Line 57:** `for playlist in playlists:` — Iterates over playlists.
* **Line 59:** `scraper = PlaylistScraper(...)` — Instantiates a scraper for the specific playlist.
* **Line 66:** `videos = scraper.scrapePlaylist(...)` — Delegates the scraping task.
* **Line 73:** `channel_info['playlists'].append(playlist_info)` — Stores the results.
* **Line 79:** `time.sleep(self.timeout)` — Respects rate limits.

*Code Context:*
```python
            for playlist in playlists:
                try:
                    scraper = PlaylistScraper(timeout=self.timeout, log_callback=self.log_callback)
```

**Phase 4: Standalone Video Retrieval**
Fetches videos not part of specific playlists (e.g., recent uploads).
* **Line 86:** `channel_info['standalone_videos'] = self.getStandaloneVideos(...)` — Scrapes the channel's video tab.

#### Source Code
```python
    def scrapeChannel(self, url, max_videos_per_playlist=200, progress_callback=None):
        """
        Scrapes playlists and videos from a channel.
        """
        channel_info = {
            'channel_name': 'Unknown Channel',
            'playlists': [],
            'standalone_videos': []
        }

        try:
            channel_url = self.normalizeChannelUrl(url)
            channel_info['channel_name'] = self.getChannelName(channel_url)

            if progress_callback:
                progress_callback(0, 100, 0)

            playlists = self.getChannelPlaylists(channel_url)
            total_tasks = len(playlists) + 1
            completed = 0

            for playlist in playlists:
                try:
                    scraper = PlaylistScraper(timeout=self.timeout, log_callback=self.log_callback)
                    
                    def nestedProgress(current, total, percentage):
                        if progress_callback:
                            overall_percentage = int(((completed + (percentage / 100)) / total_tasks) * 100)
                            progress_callback(completed + 1, total_tasks, overall_percentage)
                    
                    videos = scraper.scrapePlaylist(playlist['url'], max_videos_per_playlist, nestedProgress)

                    playlist_info = {
                        'title': playlist['title'],
                        'url': playlist['url'],
                        'videos': videos
                    }
                    channel_info['playlists'].append(playlist_info)

                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total_tasks, int((completed / total_tasks) * 100))

                    time.sleep(self.timeout)

                except Exception as e:
                    logging.warning(f"Failed to scrape playlist {playlist.get('title')}: {e}")
                    completed += 1
                    continue

            channel_info['standalone_videos'] = self.getStandaloneVideos(channel_url, max_videos_per_playlist)
            
            completed += 1
            if progress_callback:
                progress_callback(completed, total_tasks, 100)

        except Exception as e:
            logging.error(f"Error scraping channel: {e}")
            raise

        return channel_info
```

### ChannelScraper.normalizeChannelUrl

**Signature:**
```python
def normalizeChannelUrl(self, url: str) -> str
```

**Purpose:** Normalizes various YouTube channel URL formats (e.g., /user/, /channel/).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | ChannelScraper | Yes | — | The instance of the class. |
| url | str | Yes | — | The channel URL. |

**Returns:**
| Type | Description |
|------|-------------|
| str | The normalized URL. |

**Source Code:**
```python
    def normalizeChannelUrl(self, url):
        """
        Normalizes various YouTube channel URL formats.

        Args:
            url (str): The channel URL.

        Returns:
            str: The normalized URL.
        """
        if '/channel/' in url:
            return url
        elif '/user/' in url:
            username = url.split('/user/')[-1].split('/')[0]
            return f"https://www.youtube.com/user/{username}"
        return url
```

**Implementation (Executable Logic Only):**
* **Line 108:** `if '/channel/' in url:` — Checks for standard channel ID format.
* **Line 109:** `return url` — Returns as-is.
* **Line 110:** `elif '/user/' in url:` — Checks for legacy username format.
* **Line 111:** `username = url.split('/user/')[-1].split('/')[0]` — Extracts username.
* **Line 112:** `return f"https://www.youtube.com/user/{username}"` — Reconstructs standardized legacy URL.
* **Line 113:** `return url` — Returns original if no pattern matches.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| None | - | - | - |

### ChannelScraper.getChannelName

**Signature:**
```python
def getChannelName(self, url: str) -> str
```

**Purpose:** Retrieves the name of the YouTube channel using yt-dlp.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| self | ChannelScraper | Yes | — | The instance of the class. |
| url | str | Yes | — | The channel URL. |

**Returns:**
| Type | Description |
|------|-------------|
| str | The channel name or "Unknown Channel" on failure. |

**Source Code:**
```python
    def getChannelName(self, url):
        """
        Retrieves the name of the YouTube channel.

        Args:
            url (str): The channel URL.

        Returns:
            str: The channel name.
        """
        try:
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
                info = ydl.extract_info(url, download=False)
                return info.get('channel', 'Unknown Channel')

        except Exception as e:
            logging.error(f"Error getting channel name: {e}")
            return 'Unknown Channel'
```

**Implementation (Executable Logic Only):**
* **Line 126:** `cookie_file = self.cookie_manager.getCookieFile()` — Retrieves path to cookies.
* **Line 127:** `ydl_opts = {...}` — Configures yt-dlp for metadata extraction only.
* **Line 136:** `with yt_dlp.YoutubeDL(ydl_opts) as ydl:` — Context manager for yt-dlp instance.
* **Line 137:** `info = ydl.extract_info(url, download=False)` — Fetches channel metadata.
* **Line 138:** `return info.get('channel', 'Unknown Channel')` — Extracts channel name.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| yt_dlp.YoutubeDL | External | Metadata extraction | yt_dlp |

### ChannelScraper.getChannelPlaylists

**Primary Library:** `yt_dlp`
**Purpose:** Retrieves all playlists from a channel.

#### Overview
Queries the channel's `/playlists` endpoint via yt-dlp to get a list of all public playlists.

#### Signature
```python
def getChannelPlaylists(self, channel_url: str) -> list
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| channel_url | str | Yes | — | The channel URL. |

#### Returns
| Type | Description |
|------|-------------|
| list | List of playlist dicts containing 'title' and 'url'. |

#### Workflow (Executable Logic Only)

**Phase 1: URL Construction**
Prepares formatting for the playlists endpoint.
* **Line 155:** `playlists_url = f"{channel_url}/playlists"` — Appends /playlists to the base URL.

**Phase 2: Extraction**
Uses yt-dlp to flatten the playlist tab.
* **Line 168:** `with yt_dlp.YoutubeDL(ydl_opts) as ydl:` — Context manager.
* **Line 169:** `info = ydl.extract_info(playlists_url, download=False)` — Scrapes the page.

**Phase 3: Parsing**
Iterates entries to build the result list.
* **Line 171:** `if 'entries' in info:` — Checks for results.
* **Line 172:** `for entry in info['entries']:` — Iterates through found items.
* **Line 174:** `playlists.append(...)` — Adds validation playlist to list.
* **Line 178:** `time.sleep(self.timeout)` — Delays between parsing loop (though loop is local, this might be redundant or for safety).

#### Source Code
```python
    def getChannelPlaylists(self, channel_url):
        """
        Retrieves all playlists from a channel.
        """
        playlists = []
        playlists_url = f"{channel_url}/playlists"

        try:
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
                info = ydl.extract_info(playlists_url, download=False)

                if 'entries' in info:
                    for entry in info['entries']:
                        if entry and entry.get('title') and 'playlist' in entry.get('url', '').lower():
                            playlists.append({
                                'title': entry['title'],
                                'url': entry['url']
                            })
                            time.sleep(self.timeout)

        except Exception as e:
            logging.warning(f"Could not extract playlists: {e}")

        return playlists
```

### ChannelScraper.getStandaloneVideos

**Primary Library:** `yt_dlp`
**Purpose:** Retrieves standalone videos from a channel.

#### Overview
Queries the channel's `/videos` endpoint to get individual video uploads, respecting the maximum video limit.

#### Signature
```python
def getStandaloneVideos(self, channel_url: str, max_videos: int = 200) -> list
```

#### Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| channel_url | str | Yes | — | The channel URL. |
| max_videos | int | No | 200 | Limit for videos. |

#### Returns
| Type | Description |
|------|-------------|
| list | List of video info dicts. |

#### Workflow (Executable Logic Only)

**Phase 1: Setup**
Configures the target URL.
* **Line 197:** `videos_url = f"{channel_url}/videos"` — Target the videos tab.

**Phase 2: Extraction**
Fetches video metadata.
* **Line 210:** `with yt_dlp.YoutubeDL(ydl_opts) as ydl:` — Context manager.
* **Line 211:** `info = ydl.extract_info(videos_url, download=False)` — Scrapes the page.

**Phase 3: Parsing and Limiting**
Iterates through entries up to the limit.
* **Line 214:** `for entry in info['entries'][:max_videos]:` — Slices results to `max_videos`.
* **Line 217:** `video_url = ...` — Constructs watch URL from ID.
* **Line 220:** `videos.append(...)` — Adds sanitized video data to list.

#### Source Code
```python
    def getStandaloneVideos(self, channel_url, max_videos=200):
        """
        Retrieves standalone videos from a channel.
        """
        videos = []
        videos_url = f"{channel_url}/videos"

        try:
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
                info = ydl.extract_info(videos_url, download=False)

                if 'entries' in info:
                    for entry in info['entries'][:max_videos]:
                        if entry:
                            video_id = entry.get('id')
                            video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else entry.get('url', '')
                            
                            if video_url and entry.get('title'):
                                videos.append({
                                    'url': video_url,
                                    'title': sanitizeFilename(entry['title']),
                                    'duration': entry.get('duration', 0)
                                })

        except Exception as e:
            logging.warning(f"Could not extract standalone videos: {e}")

        return videos
```