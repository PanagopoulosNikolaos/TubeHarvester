"""
Unit tests for Mp4Downloader module.
"""

import os
import tempfile
from unittest.mock import Mock, patch
import pytest

from src.extraction.mp4_downloader import Mp4Downloader


class TestMp4Downloader:
    """
    Test suite for Mp4Downloader functionality.
    """

    def setup_method(self) -> None:
        """
        Initializes test environment and Mp4Downloader instance.
        """
        self.test_url = "https://www.youtube.com/watch?v=test123"
        self.test_path = tempfile.mkdtemp()
        self.downloader = Mp4Downloader()

    def teardown_method(self) -> None:
        """
        Cleans up temporary directory after test execution.
        """
        if os.path.exists(self.test_path):
            for file in os.listdir(self.test_path):
                file_path = os.path.join(self.test_path, file)
                if os.path.isfile(file_path):
                    try:
                        os.unlink(file_path)
                    except Exception:
                        pass
            try:
                os.rmdir(self.test_path)
            except Exception:
                pass

    def testInit(self) -> None:
        """
        Tests default initialization attributes.
        """
        downloader = Mp4Downloader()
        assert downloader.url is None
        assert downloader.path == Mp4Downloader.getDefaultDownloadPath()
        assert downloader.progress_callback is None
        assert downloader.log_callback is None

    def testInitWithCallbacks(self) -> None:
        """
        Tests initialization with provided callbacks.
        """
        progress_callback = Mock()
        log_callback = Mock()
        downloader = Mp4Downloader(progress_callback, log_callback)
        assert downloader.progress_callback == progress_callback
        assert downloader.log_callback == log_callback

    @staticmethod
    def testGetDefaultDownloadPath() -> None:
        """
        Tests retrieval of default system download path.
        """
        home_dir = os.path.expanduser('~')
        expected_path = os.path.join(home_dir, 'Downloads')
        assert Mp4Downloader.getDefaultDownloadPath() == expected_path

    def testSetUrl(self) -> None:
        """
        Tests setting the target video URL.
        """
        self.downloader.setUrl(self.test_url)
        assert self.downloader.url == self.test_url

    def testSetPath(self) -> None:
        """
        Tests setting a custom save path and verifying directory creation.
        """
        self.downloader.setPath(self.test_path)
        assert self.downloader.path == self.test_path
        assert os.path.exists(self.test_path)

    def testSetPathNoneUsesDefault(self) -> None:
        """
        Tests that setting path to None falls back to default.
        """
        self.downloader.setPath(None)
        assert self.downloader.path == Mp4Downloader.getDefaultDownloadPath()

    @patch('yt_dlp.YoutubeDL')
    def testFetchVideoInfoSuccess(self, mock_ydl_class: Mock) -> None:
        """
        Tests fetching video metadata with yt-dlp.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_info = {'title': 'Test Video', 'height': 720}
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value = mock_ydl

        self.downloader.setUrl(self.test_url)
        result = self.downloader.fetchVideoInfo()

        opts_capture = mock_ydl_class.call_args[0][0]
        assert 'javascript_executor' not in opts_capture
        assert opts_capture.get('noplaylist') is True

        assert result == mock_info
        mock_ydl.extract_info.assert_called_with(self.test_url, download=False)

    def testFetchVideoInfoNoUrl(self) -> None:
        """
        Tests that fetchVideoInfo raises ValueError when URL is not set.
        """
        with pytest.raises(ValueError, match="URL is not set"):
            self.downloader.fetchVideoInfo()

    @patch('yt_dlp.YoutubeDL')
    def testDownloadVideoSuccess(self, mock_ydl_class: Mock) -> None:
        """
        Tests successful MP4 download execution.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'title': 'Test Video',
            'height': 720,
        }
        mock_ydl_class.return_value = mock_ydl

        progress_callback = Mock()
        log_callback = Mock()

        self.downloader = Mp4Downloader(progress_callback, log_callback)
        self.downloader.setUrl(self.test_url)
        self.downloader.setPath(self.test_path)
        self.downloader.resolution = 720

        self.downloader.downloadVideo()

        opts_capture = mock_ydl_class.call_args[0][0]
        assert 'javascript_executor' not in opts_capture
        assert opts_capture.get('noplaylist') is True

        mock_ydl.extract_info.assert_called_with(self.test_url, download=True)
        log_callback.assert_any_call("Download complete: Test_Video")

    def testDownloadVideoNoUrl(self) -> None:
        """
        Tests that downloadVideo raises ValueError when URL is not set.
        """
        with pytest.raises(ValueError, match="URL is not set"):
            self.downloader.downloadVideo()

    @patch('yt_dlp.YoutubeDL')
    def testDownloadVideoWithCustomTitle(self, mock_ydl_class: Mock) -> None:
        """
        Tests download execution with a specified custom title.
        """
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'title': 'Original Title',
            'height': 720,
        }
        mock_ydl_class.return_value = mock_ydl

        self.downloader.setUrl(self.test_url)
        self.downloader.setPath(self.test_path)
        self.downloader.resolution = 720

        self.downloader.downloadVideo(custom_title="Custom Title")
        assert self.downloader.video_title == "Original_Title"

    def testProgressHookDownloading(self) -> None:
        """
        Tests progress callback invocation during active downloading.
        """
        progress_callback = Mock()
        self.downloader.progress_callback = progress_callback

        data = {
            'status': 'downloading',
            '_percent_str': ' 50.0%',
        }

        self.downloader.progressHook(data)
        progress_callback.assert_called_with(50)

    def testProgressHookFinished(self) -> None:
        """
        Tests that finished status in progress hook does not error.
        """
        progress_callback = Mock()
        self.downloader.progress_callback = progress_callback

        data = {
            'status': 'finished',
            '_percent_str': '100.0%',
        }

        self.downloader.progressHook(data)
        progress_callback.assert_not_called()

    def testProgressHookNoTotalBytes(self) -> None:
        """
        Tests progress hook parsing percentage without explicit byte totals.
        """
        progress_callback = Mock()
        self.downloader.progress_callback = progress_callback

        data = {
            'status': 'downloading',
            '_percent_str': ' 50.0%',
        }

        self.downloader.progressHook(data)
        progress_callback.assert_called_with(50)

    @patch('logging.error')
    def testHandleError(self, mock_logging_error: Mock) -> None:
        """
        Tests error categorization and callback logging.
        """
        log_callback = Mock()
        self.downloader.log_callback = log_callback

        self.downloader.handleError(Exception("This video is Private"))
        mock_logging_error.assert_called_with("Video restricted or requires authentication.")
        log_callback.assert_called_with("Video restricted or requires authentication.")

        self.downloader.handleError(Exception("Some other error"))
        log_callback.assert_called_with("Error: Some other error")
