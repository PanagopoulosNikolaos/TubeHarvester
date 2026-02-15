# test_playlist_scraper.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [TestPlaylistScraper](#testplaylistscraper) | Class | Test suite for the PlaylistScraper class. |
| [setup_method](#setup_method) | Method | Initializes testing environment and scraper instance. |
| [testInit](#testinit) | Method | Verifies default timeout value. |
| [testInitCustomTimeout](#testinitcustomtimeout) | Method | Verifies custom timeout initialization. |
| [testScrapePlaylistSuccess](#testscrapeplaylistsuccess) | Method | Validates complete playlist metadata extraction and transformation. |
| [testScrapePlaylistLimitedVideos](#testscrapeplaylistlimitedvideos) | Method | Verifies enforcement of video count limits. |
| [testScrapePlaylistNoEntries](#testscrapeplaylistnoentries) | Method | Handles cases where the playlist contains no videos. |
| [testScrapePlaylistWithNoneEntries](#testscrapeplaylistwithnoneentries) | Method | Ensures robustness against null entries in the YouTube response. |
| [testScrapePlaylistFailure](#testscrapeplaylistfailure) | Method | Ensures exceptions are bubbled up correctly. |
| [testGetPlaylistTitleSuccess](#getplaylisttitlesuccess) | Method | Validates retrieval and sanitization of the playlist title. |
| [testScrapePlaylistRateLimiting](#testscrapeplaylistratelimiting) | Method | Verifies sleep intervals between video metadata processing. |
| [testScrapePlaylistMissingFields](#testscrapeplaylistmissingfields) | Method | Validates default value fallback for incomplete metadata. |

## Overview
The `test_playlist_scraper.py` file provides unit tests for the `PlaylistScraper` class. It ensures that YouTube playlists can be successfully parsed into a standard internal format, handling various edge cases like missing metadata fields, rate limiting requirements, and empty playlists.

## TestPlaylistScraper

**Class Responsibility:** Manages tests for `PlaylistScraper`, focusing on the parsing of nested dictionaries returned by `yt-dlp` and ensuring that the scraping process adheres to user-defined limits and timing constraints.

### setup_method

**Signature:**
```python
def setup_method(self)
```

**Purpose:** Prepares a test URL and a fresh `PlaylistScraper` instance.

**Implementation (Executable Logic Only):**
* **Line 11:** Sets a sample playlist URL.
* **Line 12:** Instantiates the scraper with default settings.

### testScrapePlaylistSuccess

**Primary Library:** `yt_dlp`, `unittest.mock`  
**Purpose:** Validates the successful extraction and standardization of playlist video metadata.

#### Overview
This test mocks the response of `yt-dlp` for a playlist, providing a list of raw video entries. It verifies that the scraper correctly transforms these into standardized dictionary objects with clean URLs and snake_cased titles.

#### Workflow (Executable Logic Only)
* **Line 28-34:** Defines the mock raw response from `yt-dlp`.
* **Line 42:** Triggers `scrapePlaylist`.
* **Line 44-48:** Defines the expected output list.
* **Line 50-51:** Asserts that the output matches the transformation logic and that `extract_info` was called without downloading.

*Code Context:*
```python
    def testScrapePlaylistSuccess(self, mock_ydl_class):
        mock_playlist_info = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                # ...
            ]
        }
        # ...
        videos = self.scraper.scrapePlaylist(self.test_url, max_videos=5)
```

### testScrapePlaylistLimitedVideos

**Purpose:** Verifies that the scraper respects the `max_videos` limit.

**Implementation (Executable Logic Only):**
* **Line 57-65:** Provides 5 mock videos.
* **Line 73:** Calls with `max_videos=3`.
* **Line 76:** Asserts that only 3 videos were returned.

### testScrapePlaylistMissingFields

**Purpose:** Ensures the scraper provides sensible defaults for missing metadata.

**Implementation (Executable Logic Only):**
* **Line 206-211:** Provides entries with missing `title` or `duration`.
* **Line 219:** Executes scrape.
* **Line 222-224:** Asserts that missing titles become "Unknown_Title" and missing durations become `0`.

### testScrapePlaylistRateLimiting

**Primary Library:** `time.sleep`
**Purpose:** Verifies that the configured timeout is respected between video processing steps.

**Implementation (Executable Logic Only):**
* **Line 196:** Initializes scraper with a 1.5s timeout.
* **Line 197:** Scrapes a playlist with 2 videos.
* **Line 200:** Asserts that `sleep(1.5)` was called once (the interval between the two videos).

### testGetPlaylistTitleSuccess

**Purpose:** Validates retrieval of a sanitized playlist title.

**Implementation (Executable Logic Only):**
* **Line 153:** Mocks title "Test Playlist".
* **Line 161:** Calls `getPlaylistTitle`.
* **Line 163:** Asserts that the title was sanitized to "Test_Playlist".
```
