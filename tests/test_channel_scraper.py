"""
Unit tests for ChannelScraper module.
"""

from unittest.mock import Mock, patch
import pytest

from src.extraction.channel_scraper import ChannelScraper


class TestChannelScraper:
    """
    Test suite for ChannelScraper operations and channel URL normalizations.
    """

    def setup_method(self) -> None:
        """
        Initializes test URL and ChannelScraper instance.
        """
        self.test_url = "https://www.youtube.com/channel/test123"
        self.scraper = ChannelScraper(timeout=0.0)

    def testInit(self) -> None:
        """
        Tests default initialization parameters.
        """
        scraper = ChannelScraper()
        assert scraper.timeout == 2.0

    def testInitCustomTimeout(self) -> None:
        """
        Tests custom timeout initialization.
        """
        scraper = ChannelScraper(timeout=5.0)
        assert scraper.timeout == 5.0

    @patch('time.sleep')
    @patch('src.extraction.channel_scraper.PlaylistScraper')
    @patch('yt_dlp.YoutubeDL')
    def testScrapeChannelSuccess(
        self,
        mock_ydl_class: Mock,
        mock_playlist_scraper_class: Mock,
        mock_sleep: Mock,
    ) -> None:
        """
        Tests successful scraping of channel playlists and standalone uploads.
        """
        mock_ydl_channel = Mock()
        mock_ydl_channel.__enter__ = Mock(return_value=mock_ydl_channel)
        mock_ydl_channel.__exit__ = Mock(return_value=None)
        mock_ydl_channel.extract_info.return_value = {'channel': 'Test Channel'}

        mock_ydl_playlists = Mock()
        mock_ydl_playlists.__enter__ = Mock(return_value=mock_ydl_playlists)
        mock_ydl_playlists.__exit__ = Mock(return_value=None)
        mock_ydl_playlists.extract_info.return_value = {
            'entries': [
                {'title': 'Playlist 1', 'url': 'https://youtube.com/playlist?list=PL1'},
                {'title': 'Playlist 2', 'url': 'https://youtube.com/playlist?list=PL2'},
            ]
        }

        mock_ydl_videos = Mock()
        mock_ydl_videos.__enter__ = Mock(return_value=mock_ydl_videos)
        mock_ydl_videos.__exit__ = Mock(return_value=None)
        mock_ydl_videos.extract_info.return_value = {
            'entries': [
                {'id': 'video1', 'title': 'Standalone Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Standalone Video 2', 'duration': 250},
            ]
        }
        mock_ydl_class.side_effect = [mock_ydl_channel, mock_ydl_playlists, mock_ydl_videos]

        mock_playlist_scraper = Mock()
        mock_playlist_scraper.scrapePlaylist.side_effect = [
            [{'url': 'https://youtube.com/watch?v=pl1v1', 'title': 'PL1_Video_1', 'duration': 100}],
            [{'url': 'https://youtube.com/watch?v=pl2v1', 'title': 'PL2_Video_1', 'duration': 200}],
        ]
        mock_playlist_scraper_class.return_value = mock_playlist_scraper

        result = self.scraper.scrapeChannel(self.test_url)

        expected_result = {
            'channel_name': 'Test Channel',
            'playlists': [
                {
                    'title': 'Playlist 1',
                    'url': 'https://youtube.com/playlist?list=PL1',
                    'videos': [{'url': 'https://youtube.com/watch?v=pl1v1', 'title': 'PL1_Video_1', 'duration': 100}],
                },
                {
                    'title': 'Playlist 2',
                    'url': 'https://youtube.com/playlist?list=PL2',
                    'videos': [{'url': 'https://youtube.com/watch?v=pl2v1', 'title': 'PL2_Video_1', 'duration': 200}],
                },
            ],
            'standalone_videos': [
                {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Standalone_Video_1', 'duration': 300},
                {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Standalone_Video_2', 'duration': 250},
            ],
        }

        assert result == expected_result

    def testNormalizeChannelUrlChannelFormat(self) -> None:
        """
        Tests URL normalization with /channel/ format.
        """
        url = "https://www.youtube.com/channel/UC123"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == url

    def testNormalizeChannelUrlUserFormat(self) -> None:
        """
        Tests URL normalization with /user/ format.
        """
        url = "https://www.youtube.com/user/testuser"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == "https://www.youtube.com/user/testuser"

    def testNormalizeChannelUrlCustomFormat(self) -> None:
        """
        Tests URL normalization with /c/ format.
        """
        url = "https://www.youtube.com/c/TestChannel"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == url

    def testNormalizeChannelUrlAtFormat(self) -> None:
        """
        Tests URL normalization with handle @ format.
        """
        url = "https://www.youtube.com/@TestChannel"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == url

    def testNormalizeChannelUrlUnknownFormat(self) -> None:
        """
        Tests fallback behavior for arbitrary channel URLs.
        """
        url = "https://www.youtube.com/someother/test"
        result = self.scraper.normalizeChannelUrl(url)
        assert result == url

    @patch('yt_dlp.YoutubeDL')
    def testGetChannelNameSuccess(self, mock_ydl_class: Mock) -> None:
        """
        Tests retrieval of channel display name.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {'channel': 'Test Channel Name'}
        mock_ydl_class.return_value = mock_ydl

        result = self.scraper.getChannelName(self.test_url)
        assert result == 'Test Channel Name'
        mock_ydl.extract_info.assert_called_with(self.test_url, download=False)

    @patch('yt_dlp.YoutubeDL')
    def testGetChannelNameFailure(self, mock_ydl_class: Mock) -> None:
        """
        Tests fallback value when channel name extraction fails.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        result = self.scraper.getChannelName(self.test_url)
        assert result == 'Unknown Channel'

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    def testGetChannelPlaylistsSuccess(self, mock_ydl_class: Mock, mock_sleep: Mock) -> None:
        """
        Tests extracting playlist entries belonging to a channel.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'entries': [
                {'title': 'Playlist 1', 'url': 'https://youtube.com/playlist?list=PL1'},
                {'title': 'Playlist 2', 'url': 'https://youtube.com/playlist?list=PL2'},
                {'title': 'Not a Playlist', 'url': 'https://youtube.com/watch?v=video1'},
            ]
        }
        mock_ydl_class.return_value = mock_ydl

        playlists = self.scraper.getChannelPlaylists(self.test_url)

        expected_playlists = [
            {'title': 'Playlist 1', 'url': 'https://youtube.com/playlist?list=PL1'},
            {'title': 'Playlist 2', 'url': 'https://youtube.com/playlist?list=PL2'},
        ]

        assert playlists == expected_playlists

    @patch('yt_dlp.YoutubeDL')
    def testGetChannelPlaylistsNoEntries(self, mock_ydl_class: Mock) -> None:
        """
        Tests handling empty playlist results.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {'entries': None}
        mock_ydl_class.return_value = mock_ydl

        playlists = self.scraper.getChannelPlaylists(self.test_url)
        assert playlists == []

    @patch('yt_dlp.YoutubeDL')
    def testGetChannelPlaylistsFailure(self, mock_ydl_class: Mock) -> None:
        """
        Tests graceful fallback when playlist fetching errors.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        playlists = self.scraper.getChannelPlaylists(self.test_url)
        assert playlists == []

    @patch('yt_dlp.YoutubeDL')
    def testGetStandaloneVideosSuccess(self, mock_ydl_class: Mock) -> None:
        """
        Tests extracting standalone upload videos from channel tab.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
                {'id': 'video3', 'title': 'Video 3', 'duration': 400},
            ]
        }
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.getStandaloneVideos(self.test_url, max_videos=5)

        expected_videos = [
            {'url': 'https://www.youtube.com/watch?v=video1', 'title': 'Video_1', 'duration': 300},
            {'url': 'https://www.youtube.com/watch?v=video2', 'title': 'Video_2', 'duration': 250},
            {'url': 'https://www.youtube.com/watch?v=video3', 'title': 'Video_3', 'duration': 400},
        ]

        assert videos == expected_videos

    @patch('yt_dlp.YoutubeDL')
    def testGetStandaloneVideosLimited(self, mock_ydl_class: Mock) -> None:
        """
        Tests limiting the number of retrieved standalone videos.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'entries': [
                {'id': 'video1', 'title': 'Video 1', 'duration': 300},
                {'id': 'video2', 'title': 'Video 2', 'duration': 250},
                {'id': 'video3', 'title': 'Video 3', 'duration': 400},
                {'id': 'video4', 'title': 'Video 4', 'duration': 200},
            ]
        }
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.getStandaloneVideos(self.test_url, max_videos=2)

        assert len(videos) == 2
        assert videos[0]['title'] == 'Video_1'
        assert videos[1]['title'] == 'Video_2'

    @patch('yt_dlp.YoutubeDL')
    def testGetStandaloneVideosFailure(self, mock_ydl_class: Mock) -> None:
        """
        Tests error fallback when video extraction fails.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value = mock_ydl

        videos = self.scraper.getStandaloneVideos(self.test_url)
        assert videos == []

    @patch('src.extraction.channel_scraper.PlaylistScraper')
    @patch('yt_dlp.YoutubeDL')
    def testScrapeChannelPlaylistFailure(
        self,
        mock_ydl_class: Mock,
        mock_playlist_scraper_class: Mock,
    ) -> None:
        """
        Tests handling failure of an individual playlist within channel scraping.
        """
        mock_ydl_channel = Mock()
        mock_ydl_channel.__enter__ = Mock(return_value=mock_ydl_channel)
        mock_ydl_channel.__exit__ = Mock(return_value=None)
        mock_ydl_channel.extract_info.return_value = {'channel': 'Test Channel'}

        mock_ydl_playlists = Mock()
        mock_ydl_playlists.__enter__ = Mock(return_value=mock_ydl_playlists)
        mock_ydl_playlists.__exit__ = Mock(return_value=None)
        mock_ydl_playlists.extract_info.return_value = {
            'entries': [
                {'title': 'Playlist 1', 'url': 'https://youtube.com/playlist?list=PL1'},
            ]
        }

        mock_playlist_scraper = Mock()
        mock_playlist_scraper.scrapePlaylist.side_effect = Exception("Playlist scrape failed")
        mock_playlist_scraper_class.return_value = mock_playlist_scraper

        mock_ydl_videos = Mock()
        mock_ydl_videos.__enter__ = Mock(return_value=mock_ydl_videos)
        mock_ydl_videos.__exit__ = Mock(return_value=None)
        mock_ydl_videos.extract_info.return_value = {'entries': None}
        mock_ydl_class.side_effect = [mock_ydl_channel, mock_ydl_playlists, mock_ydl_videos]

        result = self.scraper.scrapeChannel(self.test_url)

        assert result['channel_name'] == 'Test Channel'
        assert result['playlists'] == []
        assert result['standalone_videos'] == []

    @patch('time.sleep')
    @patch('src.extraction.channel_scraper.PlaylistScraper')
    @patch('yt_dlp.YoutubeDL')
    def testScrapeChannelRateLimiting(
        self,
        mock_ydl_class: Mock,
        mock_playlist_scraper_class: Mock,
        mock_sleep: Mock,
    ) -> None:
        """
        Tests that rate limiting sleeps between processing playlists.
        """
        mock_ydl_channel = Mock()
        mock_ydl_channel.__enter__ = Mock(return_value=mock_ydl_channel)
        mock_ydl_channel.__exit__ = Mock(return_value=None)
        mock_ydl_channel.extract_info.return_value = {'channel': 'Test Channel'}

        mock_ydl_playlists = Mock()
        mock_ydl_playlists.__enter__ = Mock(return_value=mock_ydl_playlists)
        mock_ydl_playlists.__exit__ = Mock(return_value=None)
        mock_ydl_playlists.extract_info.return_value = {
            'entries': [
                {'title': 'Playlist 1', 'url': 'https://youtube.com/playlist?list=PL1'},
                {'title': 'Playlist 2', 'url': 'https://youtube.com/playlist?list=PL2'},
            ]
        }

        mock_playlist_scraper = Mock()
        mock_playlist_scraper.scrapePlaylist.return_value = []
        mock_playlist_scraper_class.return_value = mock_playlist_scraper

        mock_ydl_videos = Mock()
        mock_ydl_videos.__enter__ = Mock(return_value=mock_ydl_videos)
        mock_ydl_videos.__exit__ = Mock(return_value=None)
        mock_ydl_videos.extract_info.return_value = {'entries': []}
        mock_ydl_class.side_effect = [mock_ydl_channel, mock_ydl_playlists, mock_ydl_videos]

        scraper = ChannelScraper(timeout=1.5)
        scraper.scrapeChannel(self.test_url)
        mock_sleep.assert_called_with(1.5)
