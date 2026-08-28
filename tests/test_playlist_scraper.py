"""
Unit tests for PlaylistScraper module.
"""

from unittest.mock import Mock, patch
import pytest

from src.extraction.playlist_scraper import PlaylistScraper


class TestPlaylistScraper:
    """
    Test suite for PlaylistScraper functionality and normalization.
    """

    def setup_method(self) -> None:
        """
        Initializes test URL and scraper instance.
        """
        self.test_url = "https://www.youtube.com/playlist?list=test123"
        self.scraper = PlaylistScraper(timeout=0.0)

    def testInit(self) -> None:
        """
        Tests default initialization parameters.
        """
        scraper = PlaylistScraper()
        assert scraper.timeout == 2.0

    def testInitCustomTimeout(self) -> None:
        """
        Tests custom timeout parameter configuration.
        """
        scraper = PlaylistScraper(timeout=5.0)
        assert scraper.timeout == 5.0

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    def testScrapePlaylistSuccess(self, mock_ydl_class: Mock, mock_sleep: Mock) -> None:
        """
        Tests successful playlist scraping and formatting.
        """
        mock_playlist_info = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
                {'id': 'video3', 'title': 'Video 3', 'duration': 400},
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrapePlaylist(self.test_url, max_videos=5)

        expected_videos = [
            {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Video_1', 'duration': 300},
            {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Video_2', 'duration': 250},
            {'url': 'https://www.youtube.com/watch?v=video3', 'title': 'Video_3', 'duration': 400},
        ]

        assert videos == expected_videos
        mock_ydl.extract_info.assert_called_with(self.test_url, download=False)

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    def testScrapePlaylistLimitedVideos(self, mock_ydl_class: Mock, mock_sleep: Mock) -> None:
        """
        Tests limiting the number of scraped videos.
        """
        mock_playlist_info = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
                {'id': 'video3', 'title': 'Video 3', 'duration': 400},
                {'id': 'video4', 'title': 'Video 4', 'duration': 200},
                {'id': 'video5', 'title': 'Video 5', 'duration': 350},
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrapePlaylist(self.test_url, max_videos=3)

        assert len(videos) == 3
        assert videos[0]['title'] == 'Video_1'
        assert videos[1]['title'] == 'Video_2'
        assert videos[2]['title'] == 'Video_3'

    @patch('yt_dlp.YoutubeDL')
    def testScrapePlaylistNoEntries(self, mock_ydl_class: Mock) -> None:
        """
        Tests scraping playlist when entries object is None.
        """
        mock_playlist_info = {'entries': None}

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrapePlaylist(self.test_url)
        assert videos == []

    @patch('yt_dlp.YoutubeDL')
    def testScrapePlaylistEmptyEntries(self, mock_ydl_class: Mock) -> None:
        """
        Tests scraping playlist when entries list is empty.
        """
        mock_playlist_info = {'entries': []}

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrapePlaylist(self.test_url)
        assert videos == []

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    def testScrapePlaylistWithNoneEntries(self, mock_ydl_class: Mock, mock_sleep: Mock) -> None:
        """
        Tests that None items in entries list are gracefully skipped.
        """
        mock_playlist_info = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                None,
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrapePlaylist(self.test_url)

        expected_videos = [
            {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Video_1', 'duration': 300},
            {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Video_2', 'duration': 250},
        ]

        assert videos == expected_videos

    @patch('yt_dlp.YoutubeDL')
    def testScrapePlaylistFailure(self, mock_ydl_class: Mock) -> None:
        """
        Tests error propagation when scraping encounters an exception.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        with pytest.raises(Exception, match="Network error"):
            self.scraper.scrapePlaylist(self.test_url)

    @patch('yt_dlp.YoutubeDL')
    def testGetPlaylistTitleSuccess(self, mock_ydl_class: Mock) -> None:
        """
        Tests retrieval of sanitized playlist title.
        """
        mock_playlist_info = {'title': 'Test Playlist'}

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        title = self.scraper.getPlaylistTitle(self.test_url)
        assert title == 'Test_Playlist'
        mock_ydl.extract_info.assert_called_with(self.test_url, download=False)

    @patch('yt_dlp.YoutubeDL')
    def testGetPlaylistTitleFailure(self, mock_ydl_class: Mock) -> None:
        """
        Tests fallback playlist title when network or extraction fails.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        title = self.scraper.getPlaylistTitle(self.test_url)
        assert title == 'Unknown Playlist'

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    def testScrapePlaylistRateLimiting(self, mock_ydl_class: Mock, mock_sleep: Mock) -> None:
        """
        Tests that rate limiting sleeps between items.
        """
        mock_playlist_info = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        scraper = PlaylistScraper(timeout=1.5)
        scraper.scrapePlaylist(self.test_url)
        mock_sleep.assert_called_with(1.5)

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    def testScrapePlaylistMissingFields(self, mock_ydl_class: Mock, mock_sleep: Mock) -> None:
        """
        Tests defaults for video entries with missing fields.
        """
        mock_playlist_info = {
            'entries': [
                {'id': 'video1'},
                {'id': 'video2', 'title': 'Video 2'},
                {'id': 'video3', 'title': 'Video 3', 'duration': 400},
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrapePlaylist(self.test_url)

        expected_videos = [
            {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Unknown_Title', 'duration': 0},
            {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Video_2', 'duration': 0},
            {'url': 'https://www.youtube.com/watch?v=video3', 'title': 'Video_3', 'duration': 400},
        ]

        assert videos == expected_videos
