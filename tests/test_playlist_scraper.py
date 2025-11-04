import pytest
from unittest.mock import Mock, patch
from src.PlaylistScraper import PlaylistScraper


class TestPlaylistScraper:
    """Test cases for PlaylistScraper class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_url = "https://www.youtube.com/playlist?list=test123"
        self.scraper = PlaylistScraper()

    def test_init(self):
        """Test initialization."""
        scraper = PlaylistScraper()
        assert scraper.timeout == 2.0

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        scraper = PlaylistScraper(timeout=5.0)
        assert scraper.timeout == 5.0

    @patch('yt_dlp.YoutubeDL')
    def test_scrape_playlist_success(self, mock_ydl_class):
        """Test successful playlist scraping."""
        # Mock playlist info with entries
        mock_playlist_info = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
                {'id': 'video3', 'title': 'Video 3', 'duration': 400}
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrape_playlist(self.test_url, max_videos=5)

        expected_videos = [
            {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Video 1', 'duration': 300},
            {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Video 2', 'duration': 250},
            {'url': 'https://www.youtube.com/watch?v=video3', 'title': 'Video 3', 'duration': 400}
        ]

        assert videos == expected_videos
        mock_ydl.extract_info.assert_called_with(self.test_url, download=False)

    @patch('yt_dlp.YoutubeDL')
    def test_scrape_playlist_limited_videos(self, mock_ydl_class):
        """Test playlist scraping with video limit."""
        # Mock playlist info with more entries than limit
        mock_playlist_info = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
                {'id': 'video3', 'title': 'Video 3', 'duration': 400},
                {'id': 'video4', 'title': 'Video 4', 'duration': 200},
                {'id': 'video5', 'title': 'Video 5', 'duration': 350}
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrape_playlist(self.test_url, max_videos=3)

        # Should only return first 3 videos
        assert len(videos) == 3
        assert videos[0]['title'] == 'Video 1'
        assert videos[1]['title'] == 'Video 2'
        assert videos[2]['title'] == 'Video 3'

    @patch('yt_dlp.YoutubeDL')
    def test_scrape_playlist_no_entries(self, mock_ydl_class):
        """Test playlist scraping with no entries."""
        mock_playlist_info = {'entries': None}

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrape_playlist(self.test_url)

        assert videos == []

    @patch('yt_dlp.YoutubeDL')
    def test_scrape_playlist_empty_entries(self, mock_ydl_class):
        """Test playlist scraping with empty entries list."""
        mock_playlist_info = {'entries': []}

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrape_playlist(self.test_url)

        assert videos == []

    @patch('yt_dlp.YoutubeDL')
    def test_scrape_playlist_with_none_entries(self, mock_ydl_class):
        """Test playlist scraping with None entries in list."""
        mock_playlist_info = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                None,  # None entry
                {'id': 'video2', 'title': 'Video 2', 'duration': 250}
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrape_playlist(self.test_url)

        # Should skip None entries
        expected_videos = [
            {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Video 1', 'duration': 300},
            {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Video 2', 'duration': 250}
        ]

        assert videos == expected_videos

    @patch('yt_dlp.YoutubeDL')
    def test_scrape_playlist_failure(self, mock_ydl_class):
        """Test playlist scraping failure."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        with pytest.raises(Exception, match="Network error"):
            self.scraper.scrape_playlist(self.test_url)

    @patch('yt_dlp.YoutubeDL')
    def test_get_playlist_title_success(self, mock_ydl_class):
        """Test successful playlist title retrieval."""
        mock_playlist_info = {'title': 'Test Playlist'}

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        title = self.scraper.get_playlist_title(self.test_url)

        assert title == 'Test Playlist'
        mock_ydl.extract_info.assert_called_with(self.test_url, download=False)

    @patch('yt_dlp.YoutubeDL')
    def test_get_playlist_title_failure(self, mock_ydl_class):
        """Test playlist title retrieval failure."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        title = self.scraper.get_playlist_title(self.test_url)

        assert title == 'Unknown Playlist'

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    def test_scrape_playlist_rate_limiting(self, mock_ydl_class, mock_sleep):
        """Test that rate limiting is applied between video processing."""
        mock_playlist_info = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250}
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        scraper = PlaylistScraper(timeout=1.5)
        scraper.scrape_playlist(self.test_url)

        # Should sleep once between the two videos
        mock_sleep.assert_called_with(1.5)

    @patch('yt_dlp.YoutubeDL')
    def test_scrape_playlist_missing_fields(self, mock_ydl_class):
        """Test playlist scraping with missing fields in entries."""
        mock_playlist_info = {
            'entries': [
                {'id': 'video1'},  # Missing title and duration
                {'id': 'video2', 'title': 'Video 2'},  # Missing duration
                {'id': 'video3', 'title': 'Video 3', 'duration': 400}
            ]
        }

        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.scrape_playlist(self.test_url)

        expected_videos = [
            {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Unknown Title', 'duration': 0},
            {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Video 2', 'duration': 0},
            {'url': 'https://www.youtube.com/watch?v=video3', 'title': 'Video 3', 'duration': 400}
        ]

        assert videos == expected_videos
