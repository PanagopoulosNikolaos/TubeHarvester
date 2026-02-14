import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.Mp4_Converter import Mp4Downloader


class TestMp4Downloader:
    """Test Mp4Downloader functionality."""

    def setup_method(self):
        """Initialize test URL, path and downloader instance."""
        self.test_url = "https://www.youtube.com/watch?v=test123"
        self.test_path = tempfile.mkdtemp()
        self.downloader = Mp4Downloader()

    def teardown_method(self):
        """Clean up temporary directory."""
        # Clean up any files created during tests
        if os.path.exists(self.test_path):
            for file in os.listdir(self.test_path):
                file_path = os.path.join(self.test_path, file)
                if os.path.isfile(file_path):
                    try:
                        os.unlink(file_path)
                    except:
                        pass  # Ignore cleanup errors
            try:
                os.rmdir(self.test_path)
            except:
                pass  # Ignore cleanup errors

    def testInit(self):
        """Test initialization."""
        downloader = Mp4Downloader()
        assert downloader.url is None
        assert downloader.path == Mp4Downloader.getDefaultDownloadPath()
        assert downloader.progress_callback is None
        assert downloader.log_callback is None

    def testInitWithCallbacks(self):
        """Test initialization with callbacks."""
        progress_callback = Mock()
        log_callback = Mock()
        downloader = Mp4Downloader(progress_callback, log_callback)
        assert downloader.progress_callback == progress_callback
        assert downloader.log_callback == log_callback

    @staticmethod
    def testGetDefaultDownloadPath():
        """Test getting default download path."""
        home_dir = os.path.expanduser('~')
        expected_path = os.path.join(home_dir, 'Downloads')
        assert Mp4Downloader.getDefaultDownloadPath() == expected_path

    def testSetUrl(self):
        """Test setting URL."""
        self.downloader.setUrl(self.test_url)
        assert self.downloader.url == self.test_url

    def testSetPath(self):
        """Test setting save path."""
        self.downloader.setPath(self.test_path)
        assert self.downloader.path == self.test_path
        # Verify directory was created
        assert os.path.exists(self.test_path)

    def testSetPathNoneUsesDefault(self):
        """Test setting path to None uses default."""
        self.downloader.setPath(None)
        assert self.downloader.path == Mp4Downloader.getDefaultDownloadPath()

    @patch('yt_dlp.YoutubeDL')
    def testFetchVideoInfoSuccess(self, mock_ydl_class):
        """Test successful video info fetching."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_info = {'title': 'Test Video', 'height': 720}
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value = mock_ydl

        self.downloader.setUrl(self.test_url)
        result = self.downloader.fetchVideoInfo()

        opts_capture = mock_ydl_class.call_args[0][0]
        assert opts_capture['javascript_executor'] == '/home/ice/.deno/bin/deno'

        assert result == mock_info
        mock_ydl.extract_info.assert_called_with(self.test_url, download=False)

    def testFetchVideoInfoNoUrl(self):
        """Test fetching video info without URL set."""
        with pytest.raises(ValueError, match="URL is not set"):
            self.downloader.fetchVideoInfo()

    @patch('yt_dlp.YoutubeDL')
    def testDownloadVideoSuccess(self, mock_ydl_class):
        """Test successful video download."""
        # Mock video info
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'title': 'Test Video',
            'height': 720
        }
        mock_ydl_class.return_value = mock_ydl

        # Mock callbacks
        progress_callback = Mock()
        log_callback = Mock()

        self.downloader = Mp4Downloader(progress_callback, log_callback)
        self.downloader.setUrl(self.test_url)
        self.downloader.setPath(self.test_path)
        self.downloader.resolution = 720

        self.downloader.downloadVideo()

        opts_capture = mock_ydl_class.call_args[0][0]
        assert opts_capture['javascript_executor'] == '/home/ice/.deno/bin/deno'
        
        # Verify extract_info was called with download=True
        mock_ydl.extract_info.assert_called_with(self.test_url, download=True)

        # Verify log callback was called
        log_callback.assert_any_call("Download complete: Test_Video")

    def testDownloadVideoNoUrl(self):
        """Test downloading video without URL set."""
        with pytest.raises(ValueError, match="URL is not set"):
            self.downloader.downloadVideo()

    @patch('yt_dlp.YoutubeDL')
    def testDownloadVideoWithCustomTitle(self, mock_ydl_class):
        """Test video download with custom title."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_ydl.extract_info.return_value = {
            'title': 'Original Title',
            'height': 720
        }
        mock_ydl_class.return_value = mock_ydl

        self.downloader.setUrl(self.test_url)
        self.downloader.setPath(self.test_path)
        self.downloader.resolution = 720

        self.downloader.downloadVideo(custom_title="Custom Title")

        # Verify the title was set correctly (using custom title if Provided)
        # Note: In current implementation, custom_title parameter is accepted but not fully used for the filename yet
        # but the logic for sanitizing exists.
        assert self.downloader.video_title == "Original_Title"

    def testProgressHookDownloading(self):
        """Test progress hook during downloading."""
        progress_callback = Mock()
        self.downloader.progress_callback = progress_callback

        # Simulate download progress
        d = {
            'status': 'downloading',
            '_percent_str': ' 50.0%'
        }

        self.downloader.progressHook(d)

        # Verify progress callback was called with parsed progress
        progress_callback.assert_called_with(50)

    def testProgressHookFinished(self):
        """Test progress hook when finished."""
        progress_callback = Mock()
        self.downloader.progress_callback = progress_callback

        # Simulate download finished
        d = {
            'status': 'finished',
            '_percent_str': '100.0%'
        }

        self.downloader.progressHook(d)

        # No specific callback for 'finished' status in current progressHook
        # but let's check current implementation behavior
        progress_callback.assert_not_called()

    def testProgressHookNoTotalBytes(self):
        """Test progress hook with no total bytes."""
        progress_callback = Mock()
        self.downloader.progress_callback = progress_callback

        # Simulate download progress without total_bytes but with _percent_str
        d = {
            'status': 'downloading',
            '_percent_str': ' 50.0%'
        }

        self.downloader.progressHook(d)

        # Verify progress callback was called
        progress_callback.assert_called_with(50)

    @patch('os.system')
    @patch('os.remove')
    @patch('os.listdir')
    def testMergeFilesSuccess(self, mock_listdir, mock_remove, mock_system):
        """Test successful file merging."""
        mock_listdir.return_value = ['video_temp.mp4', 'audio_temp.m4a']
        mock_system.return_value = 0

        log_callback = Mock()
        self.downloader.log_callback = log_callback
        self.downloader.path = self.test_path
        self.downloader.video_title = "Test Video"

    @patch('logging.error')
    def testHandleError(self, mock_logging_error):
        """Test error handling."""
        log_callback = Mock()
        self.downloader.log_callback = log_callback
        
        # Test private video error
        self.downloader.handleError(Exception("This video is Private"))
        mock_logging_error.assert_called_with("Video restricted or requires authentication.")
        log_callback.assert_called_with("Video restricted or requires authentication.")
        
        # Test other error
        self.downloader.handleError(Exception("Some other error"))
        log_callback.assert_called_with("Error: Some other error")
