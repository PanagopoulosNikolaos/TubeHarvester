# test_channel_scraper.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [TestChannelScraper](#testchannelscraper) | Class | Test suite for the ChannelScraper class. |
| [setup_method](#setup_method) | Method | Initializes testing environment and scraper instance. |
| [testInit](#testinit) | Method | Verifies default timeout value. |
| [testInitCustomTimeout](#testinitcustomtimeout) | Method | Verifies custom timeout initialization. |
| [testScrapeChannelSuccess](#testscrapechannelsuccess) | Method | Validates complete channel scraping process with mocks. |
| [testNormalizeChannelUrlChannelFormat](#testnormalizechannelurlchannelformat) | Method | Tests normalization for standard channel URLs. |
| [testNormalizeChannelUrlUserFormat](#testnormalizechannelurluserformat) | Method | Tests normalization for user-based URLs. |
| [testNormalizeChannelUrlCustomFormat](#testnormalizechannelurlcustomformat) | Method | Tests normalization for custom channel aliases. |
| [testNormalizeChannelUrlAtFormat](#testnormalizechannelurlatformat) | Method | Tests @handle URL normalization. |
| [testNormalizeChannelUrlUnknownFormat](#testnormalizechannelurlunknownformat) | Method | Verifies pass-through for unrecognized URL patterns. |
| [testGetChannelNameSuccess](#getchannelnamesuccess) | Method | Validates successful metadata extraction for channel name. |
| [testGetChannelNameFailure](#getchannelnamefailure) | Method | Ensures fallback to 'Unknown Channel' on error. |
| [testGetChannelPlaylistsSuccess](#getchannelplaylistssuccess) | Method | Verifies filtering of non-playlist entries. |
| [testGetChannelPlaylistsNoEntries](#getchannelplaylistsnoentries) | Method | Handles cases where no playlists are found. |
| [testGetChannelPlaylistsFailure](#getchannelplaylistsfailure) | Method | Handles network failures during playlist retrieval. |
| [testGetStandaloneVideosSuccess](#getstandalonevideossuccess) | Method | Validates extraction of videos not in playlists. |
| [testGetStandaloneVideosLimited](#getstandalonevideoslimited) | Method | Checks video counting limits. |
| [testGetStandaloneVideosFailure](#getstandalonevideosfailure) | Method | Handles errors during standalone video retrieval. |
| [testScrapeChannelPlaylistFailure](#testscrapechannelplaylistfailure) | Method | Ensures robustness when individual playlists fail to scrape. |
| [testScrapeChannelRateLimiting](#testscrapechannelratelimiting) | Method | Verifies sleep intervals between playlist operations. |

## Overview
The `test_channel_scraper.py` file provides a comprehensive test suite for the `ChannelScraper` class. It covers URL normalization logic, metadata extraction via `yt-dlp`, and the coordination of `PlaylistScraper` for deep channel analysis.

## TestChannelScraper

**Class Responsibility:** This class manages the testing lifecycle for `ChannelScraper`, mocking external library `yt-dlp` to simulate network operations and validating internal state transitions and data transformations.

### setup_method

**Signature:**
```python
def setup_method(self)
```

**Purpose:** Initializes a standard test URL and a fresh `ChannelScraper` instance.

**Implementation (Executable Logic Only):**
* **Line 11:** `self.test_url = ...` — Sets the target test URL.
* **Line 12:** `self.scraper = ChannelScraper()` — Instantiates the scraper.

### testScrapeChannelSuccess

**Primary Library:** `yt_dlp`, `unittest.mock`  
**Purpose:** Validates the full workflow of scraping a channel including its playlists and standalone videos.

#### Overview
This test mocks several successive calls to `YoutubeDL.extract_info` to simulate the retrieval of channel metadata, a list of playlists, and a list of standalone videos. It also mocks `PlaylistScraper` to simulate the recursive scraping of playlist contents.

#### Signature
```python
@patch('src.ChannelScraper.PlaylistScraper')
@patch('yt_dlp.YoutubeDL')
def testScrapeChannelSuccess(self, mock_ydl_class, mock_playlist_scraper_class)
```

#### Workflow (Executable Logic Only)

**Phase 1: Mock yt-dlp Responses**
Configures three distinct return values for the `YoutubeDL` mock to satisfy consecutive calls.
* **Line 32:** Mocks channel name retrieval.
* **Line 38-43:** Mocks playlist enumeration.
* **Line 49-54:** Mocks standalone video listing.
* **Line 55:** `mock_ydl_class.side_effect = [...]` — Sequences these mocks for the scraper.

**Phase 2: Mock PlaylistScraper**
* **Line 59-62:** Sets up `scrapePlaylist` to return different video lists for each playlist found.

**Phase 3: Execution and Assertion**
* **Line 65:** Calls `scrapeChannel`.
* **Line 67-87:** Compares the returned dictionary with the expected nested structure.

*Code Context:*
```python
        mock_ydl_class.side_effect = [mock_ydl_channel, mock_ydl_playlists, mock_ydl_videos]
        mock_playlist_scraper_class.return_value = mock_playlist_scraper

        result = self.scraper.scrapeChannel(self.test_url)
```

#### Source Code
```python
    @patch('src.ChannelScraper.PlaylistScraper')
    @patch('yt_dlp.YoutubeDL')
    def testScrapeChannelSuccess(self, mock_ydl_class, mock_playlist_scraper_class):
        """Test successful channel scraping."""
        # Mock channel name extraction
        mock_ydl_channel = Mock()
        mock_ydl_channel.__enter__ = Mock(return_value=mock_ydl_channel)
        mock_ydl_channel.__exit__ = Mock(return_value=None)
        mock_ydl_channel.extract_info.return_value = {'channel': 'Test Channel'}

        # Mock playlists extraction
        mock_ydl_playlists = Mock()
        mock_ydl_playlists.__enter__ = Mock(return_value=mock_ydl_playlists)
        mock_ydl_playlists.__exit__ = Mock(return_value=None)
        mock_ydl_playlists.extract_info.return_value = {
            'entries': [
                {'title': 'Playlist 1', 'url': 'https://youtube.com/playlist?list=PL1'},
                {'title': 'Playlist 2', 'url': 'https://youtube.com/playlist?list=PL2'}
            ]
        }

        # Mock standalone videos extraction
        mock_ydl_videos = Mock()
        mock_ydl_videos.__enter__ = Mock(return_value=mock_ydl_videos)
        mock_ydl_videos.__exit__ = Mock(return_value=None)
        mock_ydl_videos.extract_info.return_value = {
            'entries': [
                {'id': 'video1', 'title': 'Standalone Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Standalone Video 2', 'duration': 250}
            ]
        }
        mock_ydl_class.side_effect = [mock_ydl_channel, mock_ydl_playlists, mock_ydl_videos]

        # Mock playlist scraper
        mock_playlist_scraper = Mock()
        mock_playlist_scraper.scrapePlaylist.side_effect = [
            [{'url': 'https://youtube.com/watch?v=pl1v1', 'title': 'PL1_Video_1', 'duration': 100}],
            [{'url': 'https://youtube.com/watch?v=pl2v1', 'title': 'PL2_Video_1', 'duration': 200}]
        ]
        mock_playlist_scraper_class.return_value = mock_playlist_scraper

        result = self.scraper.scrapeChannel(self.test_url)

        expected_result = {
            'channel_name': 'Test Channel',
            'playlists': [
                {
                    'title': 'Playlist 1',
                    'url': 'https://youtube.com/playlist?list=PL1',
                    'videos': [{'url': 'https://youtube.com/watch?v=pl1v1', 'title': 'PL1_Video_1', 'duration': 100}]
                },
                {
                    'title': 'Playlist 2',
                    'url': 'https://youtube.com/playlist?list=PL2',
                    'videos': [{'url': 'https://youtube.com/watch?v=pl2v1', 'title': 'PL2_Video_1', 'duration': 200}]
                }
            ],
            'standalone_videos': [
                {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Standalone_Video_1', 'duration': 300},
                {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Standalone_Video_2', 'duration': 250}
            ]
        }

        assert result == expected_result
```

### testNormalizeChannelUrlChannelFormat

**Signature:**
```python
def testNormalizeChannelUrlChannelFormat(self)
```

**Purpose:** Verifies that `/channel/` prefixed URLs are returned unchanged.

**Implementation (Executable Logic Only):**
* **Line 92:** Calls `normalizeChannelUrl`.
* **Line 93:** Asserts identity.

### testNormalizeChannelUrlUserFormat

**Purpose:** Verifies `/user/` URL normalization.

### testNormalizeChannelUrlCustomFormat

**Purpose:** Verifies `/c/` URL normalization.

### testNormalizeChannelUrlAtFormat

**Purpose:** Verifies handles (`/@`) URL normalization.

### testGetChannelNameSuccess

**Purpose:** Tests the successful extraction of a channel's display name.

**Implementation (Executable Logic Only):**
* **Line 125:** Mocks return of `{'channel': 'Test Channel Name'}`.
* **Line 128:** Triggers method.
* **Line 131:** Verifies `extract_info` call parameters.

### testGetChannelPlaylistsSuccess

**Purpose:** Verifies the identification and filtering of playlist entries from a list of channel uploads.

**Implementation (Executable Logic Only):**
* **Line 152-158:** Provides a mixed list of entries (playlists and a video).
* **Line 161:** Executes filtering logic.
* **Line 163-168:** Asserts that only playlist entries were retained.

### testGetStandaloneVideosSuccess

**Purpose:** Validates the extraction and naming cleanup of individual channel videos.

**Implementation (Executable Logic Only):**
* **Line 202-208:** Provides mock raw video entries.
* **Line 211:** Calls extraction with a generous limit.
* **Line 214-219:** Asserts transformed URLs and snake_cased titles.

### testScrapeChannelPlaylistFailure

**Primary Library:** `unittest.mock`  
**Purpose:** Verifies the robustness of the channel scraper when one or more of its playlists cannot be scraped.

#### Overview
This test covers an error recovery scenario where the `PlaylistScraper` raises an exception during a channel-wide scrape. The expected behavior is that the scraper catches the error and continues to return whatever data was successfully gathered (in this case, just the channel name).

#### Workflow (Executable Logic Only)
* **Line 279:** Configures the `PlaylistScraper` mock to raise an exception.
* **Line 287:** Sequences the mocks.
* **Line 289:** Executes the scrape.
* **Line 292-294:** Verifies that the channel name is still returned while playlists and video lists remain empty.

### testScrapeChannelRateLimiting

**Primary Library:** `time`, `unittest.mock`  
**Purpose:** Verifies that a pause is inserted between scraping consecutive playlists to avoid API rate limits.

#### Workflow (Executable Logic Only)
* **Line 312-315:** Configures the mock to find two playlists.
* **Line 330:** Initializes a scraper with a specific timeout.
* **Line 331:** Executes the scrape.
* **Line 334:** Verifies that `time.sleep` was called with the configured timeout.
