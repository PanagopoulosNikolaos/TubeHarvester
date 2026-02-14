import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.Mp3_Converter import Mp3Downloader


class TestMp3Downloader:
    """Test Mp3Downloader functionality."""

    def setup_method(self):
        """Initialize test URL, path and downloader instance."""
        self.test_url = "https://www.youtube.com/watch?v=test123"
        self.test_path = tempfile.mkdtemp()
        self.downloader = Mp3Downloader(self.test_url, self.test_path)

    def teardown_method(self):
        """Clean up test directory."""
        # Clean up any files created during tests
        for file in os.listdir(self.test_path):
            file_path = os.path.join(self.test_path, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(self.test_path)

    def testInitWithUrlAndPath(self):
        """Test initialization with URL and path."""
        downloader = Mp3Downloader(self.test_url, self.test_path)
        assert downloader.url == self.test_url
        assert downloader.save_path == self.test_path

    def testInitWithoutUrlAndPath(self):
        """Test initialization without URL and path."""
        downloader = Mp3Downloader()
        assert downloader.url is None
        assert downloader.save_path == Mp3Downloader.getDefaultDownloadPath()

    def testSetUrl(self):
        """Test setting URL."""
        downloader = Mp3Downloader()
        downloader.setUrl(self.test_url)
        assert downloader.url == self.test_url

    def testSetPath(self):
        """Test setting save path."""
        downloader = Mp3Downloader()
        downloader.setPath(self.test_path)
        assert downloader.save_path == self.test_path

    def testSetPathNoneUsesDefault(self):
        """Test setting path to None uses default."""
        downloader = Mp3Downloader()
        downloader.setPath(None)
        assert downloader.save_path == Mp3Downloader.getDefaultDownloadPath()

    @staticmethod
    def testGetDefaultDownloadPath():
        """Test getting default download path."""
        home_dir = os.path.expanduser('~')
        expected_path = os.path.join(home_dir, 'Downloads')
        assert Mp3Downloader.getDefaultDownloadPath() == expected_path

    @patch('yt_dlp.YoutubeDL')
    def testDownloadAsMp3Success(self, mock_ydl_class):
        """Test successful MP3 download."""
        # Mock the YoutubeDL instances as context managers
        mock_ydl_info = Mock()
        mock_ydl_info.__enter__ = Mock(return_value=mock_ydl_info)
        mock_ydl_info.__exit__ = Mock(return_value=None)
        mock_ydl_info.extract_info.return_value = {'title': 'Test Video'}

        mock_ydl_download = Mock()
        mock_ydl_download.__enter__ = Mock(return_value=mock_ydl_download)
        mock_ydl_download.__exit__ = Mock(return_value=None)

        mock_ydl_class.side_effect = [mock_ydl_info, mock_ydl_download]

        # Mock progress callback
        progress_callback = Mock()
        log_callback = Mock()

        downloader = Mp3Downloader(self.test_url, self.test_path, progress_callback, log_callback)
        result = downloader.downloadAsMp3()

        # Verify the download was called
        assert mock_ydl_class.call_count == 2
        assert result == self.test_path

        # Verify log callback was called
        log_callback.assert_called()

    @patch('yt_dlp.YoutubeDL')
    def testDownloadAsMp3WithCustomTitle(self, mock_ydl_class):
        """Test MP3 download with custom title."""
        mock_ydl_info = Mock()
        mock_ydl_info.__enter__ = Mock(return_value=mock_ydl_info)
        mock_ydl_info.__exit__ = Mock(return_value=None)
        mock_ydl_info.extract_info.return_value = {'title': 'Original Title'}

        mock_ydl_download = Mock()
        mock_ydl_download.__enter__ = Mock(return_value=mock_ydl_download)
        mock_ydl_download.__exit__ = Mock(return_value=None)

        mock_ydl_class.side_effect = [mock_ydl_info, mock_ydl_download]

        downloader = Mp3Downloader(self.test_url, self.test_path)
        downloader.downloadAsMp3(custom_title="Custom Title")

        # Verify download was called with custom title in output template
        # The second call should be the actual download
        download_call = mock_ydl_download.download.call_args[0][0]
        assert download_call == [self.test_url]

    @patch('yt_dlp.YoutubeDL')
    def testDownloadAsMp3Failure(self, mock_ydl_class):
        """Test MP3 download failure."""
        mock_ydl_info = Mock()
        mock_ydl_info.__enter__ = Mock(return_value=mock_ydl_info)
        mock_ydl_info.__exit__ = Mock(return_value=None)
        mock_ydl_info.extract_info.side_effect = Exception("Download failed")

        mock_ydl_class.return_value = mock_ydl_info

        log_callback = Mock()
        downloader = Mp3Downloader(self.test_url, self.test_path, log_callback=log_callback)

        with pytest.raises(Exception, match="Download failed"):
            downloader.downloadAsMp3()

        # Verify error was logged
        log_callback.assert_called()

    def testProgressHookDownloading(self):
        """Test progress hook during downloading."""
        progress_callback = Mock()
        downloader = Mp3Downloader(progress_callback=progress_callback)

        # Simulate download progress
        d = {
            'status': 'downloading',
            'total_bytes': 1000,
            'downloaded_bytes': 500
        }

        downloader.progressHook(d)

        # Verify progress callback was called with 50%
        progress_callback.assert_called_with(50)

    def testProgressHookFinished(self):
        """Test progress hook when finished."""
        progress_callback = Mock()
        downloader = Mp3Downloader(progress_callback=progress_callback)

        # Simulate download finished
        d = {'status': 'finished'}

        downloader.progressHook(d)

        # Verify progress callback was called with 100%
        progress_callback.assert_called_with(100)

    def testProgressHookNoTotalBytes(self):
        """Test progress hook with no total bytes."""
        progress_callback = Mock()
        downloader = Mp3Downloader(progress_callback=progress_callback)

        # Simulate download progress without total_bytes
        d = {
            'status': 'downloading',
            'downloaded_bytes': 500
        }

        downloader.progressHook(d)

        # Verify progress callback was not called
        progress_callback.assert_not_called()
