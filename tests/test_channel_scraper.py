import pytest
from unittest.mock import Mock, patch
from src.ChannelScraper import ChannelScraper


class TestChannelScraper:
    """Test ChannelScraper functionality."""

    def setup_method(self):
        """Initialize test URL and scraper instance."""
        self.test_url = "https://www.youtube.com/channel/test123"
        self.scraper = ChannelScraper()

    def test_init(self):
        """Test initialization."""
        scraper = ChannelScraper()
        assert scraper.timeout == 2.0

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        scraper = ChannelScraper(timeout=5.0)
        assert scraper.timeout == 5.0

    @patch('src.ChannelScraper.PlaylistScraper')
    @patch('yt_dlp.YoutubeDL')
    def test_scrape_channel_success(self, mock_ydl_class, mock_playlist_scraper_class):
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

    def test_normalize_channel_url_channel_format(self):
        """Test URL normalization for already correct channel format."""
        url = "https://www.youtube.com/channel/UC123"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == url

    def test_normalize_channel_url_user_format(self):
        """Test URL normalization for user format."""
        url = "https://www.youtube.com/user/testuser"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == "https://www.youtube.com/user/testuser"

    def test_normalize_channel_url_custom_format(self):
        """Test URL normalization for custom channel format."""
        url = "https://www.youtube.com/c/TestChannel"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == url

    def test_normalize_channel_url_at_format(self):
        """Test URL normalization for @ format."""
        url = "https://www.youtube.com/@TestChannel"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == url

    def test_normalize_channel_url_unknown_format(self):
        """Test URL normalization for unknown format."""
        url = "https://www.youtube.com/someother/test"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == url

    @patch('yt_dlp.YoutubeDL')
    def test_get_channel_name_success(self, mock_ydl_class):
        """Test successful channel name retrieval."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {'channel': 'Test Channel Name'}
        mock_ydl_class.return_value = mock_ydl

        result = self.scraper.getChannelName(self.test_url)

        assert result == 'Test Channel Name'
        mock_ydl.extract_info.assert_called_with(self.test_url, download=False)

    @patch('yt_dlp.YoutubeDL')
    def test_get_channel_name_failure(self, mock_ydl_class):
        """Test channel name retrieval failure."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        result = self.scraper.getChannelName(self.test_url)

        assert result == 'Unknown Channel'

    @patch('yt_dlp.YoutubeDL')
    def test_get_channel_playlists_success(self, mock_ydl_class):
        """Test successful channel playlists retrieval."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'entries': [
                {'title': 'Playlist 1', 'url': 'https://youtube.com/playlist?list=PL1'},
                {'title': 'Playlist 2', 'url': 'https://youtube.com/playlist?list=PL2'},
                {'title': 'Not a Playlist', 'url': 'https://youtube.com/watch?v=video1'}  # Should be filtered out
            ]
        }
        mock_ydl_class.return_value = mock_ydl

        playlists = self.scraper.getChannelPlaylists(self.test_url)

        expected_playlists = [
            {'title': 'Playlist 1', 'url': 'https://youtube.com/playlist?list=PL1'},
            {'title': 'Playlist 2', 'url': 'https://youtube.com/playlist?list=PL2'}
        ]

        assert playlists == expected_playlists

    @patch('yt_dlp.YoutubeDL')
    def test_get_channel_playlists_no_entries(self, mock_ydl_class):
        """Test channel playlists retrieval with no entries."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {'entries': None}
        mock_ydl_class.return_value = mock_ydl

        playlists = self.scraper.getChannelPlaylists(self.test_url)

        assert playlists == []

    @patch('yt_dlp.YoutubeDL')
    def test_get_channel_playlists_failure(self, mock_ydl_class):
        """Test channel playlists retrieval failure."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        playlists = self.scraper.getChannelPlaylists(self.test_url)

        assert playlists == []

    @patch('yt_dlp.YoutubeDL')
    def test_get_standalone_videos_success(self, mock_ydl_class):
        """Test successful standalone videos retrieval."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
                {'id': 'video3', 'title': 'Video 3', 'duration': 400}
            ]
        }
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.getStandaloneVideos(self.test_url, max_videos=5)

        expected_videos = [
            {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Video_1', 'duration': 300},
            {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Video_2', 'duration': 250},
            {'url': 'https://www.youtube.com/watch?v=video3', 'title': 'Video_3', 'duration': 400}
        ]

        assert videos == expected_videos

    @patch('yt_dlp.YoutubeDL')
    def test_get_standalone_videos_limited(self, mock_ydl_class):
        """Test standalone videos retrieval with limit."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
                {'id': 'video3', 'title': 'Video 3', 'duration': 400},
                {'id': 'video4', 'title': 'Video 4', 'duration': 200}
            ]
        }
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.getStandaloneVideos(self.test_url, max_videos=2)

        # Should only return first 2 videos
        assert len(videos) == 2
        assert videos[0]['title'] == 'Video_1'
        assert videos[1]['title'] == 'Video_2'

    @patch('yt_dlp.YoutubeDL')
    def test_get_standalone_videos_failure(self, mock_ydl_class):
        """Test standalone videos retrieval failure."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.getStandaloneVideos(self.test_url)

        assert videos == []

    @patch('src.ChannelScraper.PlaylistScraper')
    @patch('yt_dlp.YoutubeDL')
    def test_scrape_channel_playlist_failure(self, mock_ydl_class, mock_playlist_scraper_class):
        """Test channel scraping when playlist scraping fails."""
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
                {'title': 'Playlist 1', 'url': 'https://youtube.com/playlist?list=PL1'}
            ]
        }

        # Mock playlist scraper failure
        mock_playlist_scraper = Mock()
        mock_playlist_scraper.scrapePlaylist.side_effect = Exception("Playlist scrape failed")
        mock_playlist_scraper_class.return_value = mock_playlist_scraper

        # Mock standalone videos (empty)
        mock_ydl_videos = Mock()
        mock_ydl_videos.__enter__ = Mock(return_value=mock_ydl_videos)
        mock_ydl_videos.__exit__ = Mock(return_value=None)
        mock_ydl_videos.extract_info.return_value = {'entries': None}
        mock_ydl_class.side_effect = [mock_ydl_channel, mock_ydl_playlists, mock_ydl_videos]

        result = self.scraper.scrapeChannel(self.test_url)

        # Should still return result with empty playlists and standalone videos
        assert result['channel_name'] == 'Test Channel'
        assert result['playlists'] == []
        assert result['standalone_videos'] == []

    @patch('time.sleep')
    @patch('src.ChannelScraper.PlaylistScraper')
    @patch('yt_dlp.YoutubeDL')
    def test_scrape_channel_rate_limiting(self, mock_ydl_class, mock_playlist_scraper_class, mock_sleep):
        """Test that rate limiting is applied between playlist processing."""
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

        # Mock playlist scraper
        mock_playlist_scraper = Mock()
        mock_playlist_scraper.scrapePlaylist.return_value = []
        mock_playlist_scraper_class.return_value = mock_playlist_scraper

        # Mock standalone videos
        mock_ydl_videos = Mock()
        mock_ydl_videos.__enter__ = Mock(return_value=mock_ydl_videos)
        mock_ydl_videos.__exit__ = Mock(return_value=None)
        mock_ydl_videos.extract_info.return_value = {'entries': []}
        mock_ydl_class.side_effect = [mock_ydl_channel, mock_ydl_playlists, mock_ydl_videos]

        scraper = ChannelScraper(timeout=1.5)
        scraper.scrapeChannel(self.test_url)

        # Should sleep once between the two playlists
        mock_sleep.assert_called_with(1.5)
