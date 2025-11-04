import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.Mp4_Converter import YouTubeDownloader


class TestYouTubeDownloader:
    """Test cases for YouTubeDownloader class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_url = "https://www.youtube.com/watch?v=test123"
        self.test_path = tempfile.mkdtemp()
        self.downloader = YouTubeDownloader()

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
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

    def test_init(self):
        """Test initialization."""
        downloader = YouTubeDownloader()
        assert downloader.url is None
        assert downloader.path == YouTubeDownloader.get_default_download_path()
        assert downloader.progress_callback is None
        assert downloader.log_callback is None

    def test_init_with_callbacks(self):
        """Test initialization with callbacks."""
        progress_callback = Mock()
        log_callback = Mock()
        downloader = YouTubeDownloader(progress_callback, log_callback)
        assert downloader.progress_callback == progress_callback
        assert downloader.log_callback == log_callback

    @staticmethod
    def test_get_default_download_path():
        """Test getting default download path."""
        home_dir = os.path.expanduser('~')
        expected_path = os.path.join(home_dir, 'Downloads')
        assert YouTubeDownloader.get_default_download_path() == expected_path

    def test_set_url(self):
        """Test setting URL."""
        self.downloader.set_url(self.test_url)
        assert self.downloader.url == self.test_url

    def test_set_path(self):
        """Test setting save path."""
        self.downloader.set_path(self.test_path)
        assert self.downloader.path == self.test_path
        # Verify directory was created
        assert os.path.exists(self.test_path)

    def test_set_path_none_uses_default(self):
        """Test setting path to None uses default."""
        self.downloader.set_path(None)
        assert self.downloader.path == YouTubeDownloader.get_default_download_path()

    @patch('yt_dlp.YoutubeDL')
    def test_fetch_video_info_success(self, mock_ydl_class):
        """Test successful video info fetching."""
        mock_ydl = Mock()
        mock_ydl.__enter__ = Mock(return_value=mock_ydl)
        mock_ydl.__exit__ = Mock(return_value=None)
        mock_info = {'title': 'Test Video', 'height': 720}
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value = mock_ydl

        self.downloader.set_url(self.test_url)
        result = self.downloader.fetch_video_info()

        assert result == mock_info
        mock_ydl.extract_info.assert_called_with(self.test_url, download=False)

    def test_fetch_video_info_no_url(self):
        """Test fetching video info without URL set."""
        with pytest.raises(ValueError, match="URL is not set"):
            self.downloader.fetch_video_info()

    @patch('yt_dlp.YoutubeDL')
    @patch('os.system')
    @patch('os.remove')
    @patch('os.listdir')
    def test_download_video_success(self, mock_listdir, mock_remove, mock_system, mock_ydl_class):
        """Test successful video download."""
        # Mock video info
        mock_ydl_info = Mock()
        mock_ydl_info.__enter__ = Mock(return_value=mock_ydl_info)
        mock_ydl_info.__exit__ = Mock(return_value=None)
        mock_ydl_info.extract_info.return_value = {
            'title': 'Test Video',
            'height': 720
        }

        # Mock download instances as context managers
        mock_ydl_audio = Mock()
        mock_ydl_audio.__enter__ = Mock(return_value=mock_ydl_audio)
        mock_ydl_audio.__exit__ = Mock(return_value=None)

        mock_ydl_video = Mock()
        mock_ydl_video.__enter__ = Mock(return_value=mock_ydl_video)
        mock_ydl_video.__exit__ = Mock(return_value=None)

        mock_ydl_class.side_effect = [mock_ydl_info, mock_ydl_audio, mock_ydl_video]

        # Mock file system operations
        mock_listdir.return_value = ['video_temp.mp4', 'audio_temp.m4a']
        mock_system.return_value = 0  # Success

        # Mock callbacks
        progress_callback = Mock()
        log_callback = Mock()

        self.downloader = YouTubeDownloader(progress_callback, log_callback)
        self.downloader.set_url(self.test_url)
        self.downloader.set_path(self.test_path)
        self.downloader.resolution = 720

        self.downloader.download_video()

        # Verify downloads were called
        assert mock_ydl_class.call_count == 3

        # Verify merge command was executed
        expected_command = f"ffmpeg -i \"{os.path.join(self.test_path, 'video_temp.mp4')}\" -i \"{os.path.join(self.test_path, 'audio_temp.m4a')}\" -c:v copy -c:a aac \"{os.path.join(self.test_path, 'Test Video.mp4')}\""
        mock_system.assert_called_with(expected_command)

        # Verify cleanup was called
        assert mock_remove.call_count == 2

        # Verify log callback was called
        log_callback.assert_called()

    def test_download_video_no_url(self):
        """Test downloading video without URL set."""
        with pytest.raises(ValueError, match="URL is not set"):
            self.downloader.download_video()

    @patch('yt_dlp.YoutubeDL')
    def test_download_video_with_custom_title(self, mock_ydl_class):
        """Test video download with custom title."""
        mock_ydl_info = Mock()
        mock_ydl_info.__enter__ = Mock(return_value=mock_ydl_info)
        mock_ydl_info.__exit__ = Mock(return_value=None)
        mock_ydl_info.extract_info.return_value = {
            'title': 'Original Title',
            'height': 720
        }

        mock_ydl_audio = Mock()
        mock_ydl_audio.__enter__ = Mock(return_value=mock_ydl_audio)
        mock_ydl_audio.__exit__ = Mock(return_value=None)

        mock_ydl_video = Mock()
        mock_ydl_video.__enter__ = Mock(return_value=mock_ydl_video)
        mock_ydl_video.__exit__ = Mock(return_value=None)

        mock_ydl_class.side_effect = [mock_ydl_info, mock_ydl_audio, mock_ydl_video]

        self.downloader.set_url(self.test_url)
        self.downloader.set_path(self.test_path)
        self.downloader.resolution = 720

        with patch('os.system'), patch('os.remove'), patch('os.listdir', return_value=['video_temp.mp4', 'audio_temp.m4a']):
            self.downloader.download_video(custom_title="Custom Title")

        # Verify the title was set correctly
        assert self.downloader.video_title == "Custom Title"

    def test_progress_hook_downloading(self):
        """Test progress hook during downloading."""
        progress_callback = Mock()
        self.downloader.progress_callback = progress_callback

        # Simulate download progress
        d = {
            'status': 'downloading',
            'total_bytes': 1000,
            'downloaded_bytes': 500
        }

        self.downloader._progress_hook(d, 0, 100)

        # Verify progress callback was called with scaled progress
        progress_callback.assert_called_with(50)

    def test_progress_hook_finished(self):
        """Test progress hook when finished."""
        progress_callback = Mock()
        self.downloader.progress_callback = progress_callback

        # Simulate download finished
        d = {'status': 'finished'}

        self.downloader._progress_hook(d, 0, 100)

        # Verify progress callback was called with end progress
        progress_callback.assert_called_with(100)

    def test_progress_hook_no_total_bytes(self):
        """Test progress hook with no total bytes."""
        progress_callback = Mock()
        self.downloader.progress_callback = progress_callback

        # Simulate download progress without total_bytes
        d = {
            'status': 'downloading',
            'downloaded_bytes': 500
        }

        self.downloader._progress_hook(d, 0, 100)

        # Verify progress callback was not called
        progress_callback.assert_not_called()

    @patch('os.system')
    @patch('os.remove')
    @patch('os.listdir')
    def test_merge_files_success(self, mock_listdir, mock_remove, mock_system):
        """Test successful file merging."""
        mock_listdir.return_value = ['video_temp.mp4', 'audio_temp.m4a']
        mock_system.return_value = 0

        log_callback = Mock()
        self.downloader.log_callback = log_callback
        self.downloader.path = self.test_path
        self.downloader.video_title = "Test Video"

        self.downloader._merge_files()

        # Verify ffmpeg command was called
        expected_command = f"ffmpeg -i \"{os.path.join(self.test_path, 'video_temp.mp4')}\" -i \"{os.path.join(self.test_path, 'audio_temp.m4a')}\" -c:v copy -c:a aac \"{os.path.join(self.test_path, 'Test Video.mp4')}\""
        mock_system.assert_called_with(expected_command)

        # Verify cleanup
        assert mock_remove.call_count == 2

        # Verify success log
        log_callback.assert_called_with("Files merged successfully.")

    @patch('os.listdir')
    def test_merge_files_missing_temp_files(self, mock_listdir):
        """Test merging when temporary files are missing."""
        mock_listdir.return_value = ['other_file.mp4']  # No temp files

        log_callback = Mock()
        self.downloader.log_callback = log_callback

        self.downloader._merge_files()

        # Verify error log
        log_callback.assert_called_with("Error: Could not find temporary audio/video files to merge.")
