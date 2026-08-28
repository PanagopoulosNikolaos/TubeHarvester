"""
Unit tests for Mp3Downloader module.
"""

import os
import tempfile
from unittest.mock import Mock, patch
import pytest

from src.extraction.mp3_downloader import Mp3Downloader


class TestMp3Downloader:
    """
    Test suite for Mp3Downloader functionality.
    """

    def setup_method(self) -> None:
        """
        Initializes test URL, directory, and Mp3Downloader instance.
        """
        self.test_url = "https://www.youtube.com/watch?v=test123"
        self.test_path = tempfile.mkdtemp()
        self.downloader = Mp3Downloader(self.test_url, self.test_path)

    def teardown_method(self) -> None:
        """
        Cleans up temporary directory after test execution.
        """
        for file in os.listdir(self.test_path):
            file_path = os.path.join(self.test_path, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(self.test_path)

    def testInitWithUrlAndPath(self) -> None:
        """
        Tests initialization with explicit URL and save directory.
        """
        downloader = Mp3Downloader(self.test_url, self.test_path)
        assert downloader.url == self.test_url
        assert downloader.save_path == self.test_path

    def testInitWithoutUrlAndPath(self) -> None:
        """
        Tests default initialization without explicit arguments.
        """
        downloader = Mp3Downloader()
        assert downloader.url is None
        assert downloader.save_path == Mp3Downloader.getDefaultDownloadPath()

    def testSetUrl(self) -> None:
        """
        Tests updating the target URL.
        """
        downloader = Mp3Downloader()
        downloader.setUrl(self.test_url)
        assert downloader.url == self.test_url

    def testSetPath(self) -> None:
        """
        Tests updating the target save directory path.
        """
        downloader = Mp3Downloader()
        downloader.setPath(self.test_path)
        assert downloader.save_path == self.test_path

    def testSetPathNoneUsesDefault(self) -> None:
        """
        Tests that setting save path to None defaults to system directory.
        """
        downloader = Mp3Downloader()
        downloader.setPath(None)
        assert downloader.save_path == Mp3Downloader.getDefaultDownloadPath()

    @staticmethod
    def testGetDefaultDownloadPath() -> None:
        """
        Tests retrieval of system Downloads folder.
        """
        home_dir = os.path.expanduser('~')
        expected_path = os.path.join(home_dir, 'Downloads')
        assert Mp3Downloader.getDefaultDownloadPath() == expected_path

    @patch('yt_dlp.YoutubeDL')
    def testDownloadAsMp3Success(self, mock_ydl_class: Mock) -> None:
        """
        Tests successful MP3 download workflow and callbacks.
        """
        mock_ydl_info = Mock()
        mock_ydl_info.__enter__ = Mock(return_value=mock_ydl_info)
        mock_ydl_info.__exit__ = Mock(return_value=None)
        mock_ydl_info.extract_info.return_value = {'title': 'Test Video'}

        mock_ydl_download = Mock()
        mock_ydl_download.__enter__ = Mock(return_value=mock_ydl_download)
        mock_ydl_download.__exit__ = Mock(return_value=None)

        mock_ydl_class.side_effect = [mock_ydl_info, mock_ydl_download]

        progress_callback = Mock()
        log_callback = Mock()

        downloader = Mp3Downloader(self.test_url, self.test_path, progress_callback, log_callback)
        result = downloader.downloadAsMp3()

        assert mock_ydl_class.call_count == 2
        assert result == self.test_path
        log_callback.assert_called()

    @patch('yt_dlp.YoutubeDL')
    def testDownloadAsMp3WithCustomTitle(self, mock_ydl_class: Mock) -> None:
        """
        Tests MP3 download execution with customized title string.
        """
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

        download_call = mock_ydl_download.download.call_args[0][0]
        assert download_call == [self.test_url]

    @patch('yt_dlp.YoutubeDL')
    def testDownloadAsMp3Failure(self, mock_ydl_class: Mock) -> None:
        """
        Tests exception handling and logging when download fails.
        """
        mock_ydl_info = Mock()
        mock_ydl_info.__enter__ = Mock(return_value=mock_ydl_info)
        mock_ydl_info.__exit__ = Mock(return_value=None)
        mock_ydl_info.extract_info.side_effect = Exception("Download failed")

        mock_ydl_class.return_value = mock_ydl_info

        log_callback = Mock()
        downloader = Mp3Downloader(self.test_url, self.test_path, log_callback=log_callback)

        with pytest.raises(Exception, match="Download failed"):
            downloader.downloadAsMp3()

        log_callback.assert_called()

    def testProgressHookDownloading(self) -> None:
        """
        Tests percentage calculation during downloading stage.
        """
        progress_callback = Mock()
        downloader = Mp3Downloader(progress_callback=progress_callback)

        data = {
            'status': 'downloading',
            'total_bytes': 1000,
            'downloaded_bytes': 500,
        }

        downloader.progressHook(data)
        progress_callback.assert_called_with(50)

    def testProgressHookFinished(self) -> None:
        """
        Tests reporting 100% when finished status is received.
        """
        progress_callback = Mock()
        downloader = Mp3Downloader(progress_callback=progress_callback)

        data = {'status': 'finished'}
        downloader.progressHook(data)
        progress_callback.assert_called_with(100)

    def testProgressHookNoTotalBytes(self) -> None:
        """
        Tests handling progress state when total byte count is missing.
        """
        progress_callback = Mock()
        downloader = Mp3Downloader(progress_callback=progress_callback)

        data = {
            'status': 'downloading',
            'downloaded_bytes': 500,
        }

        downloader.progressHook(data)
        progress_callback.assert_not_called()
