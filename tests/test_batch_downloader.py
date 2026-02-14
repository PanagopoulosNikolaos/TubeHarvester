import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.BatchDownloader import BatchDownloader


class TestBatchDownloader:
    """Test BatchDownloader functionality."""

    def setup_method(self):
        """Create temporary directory and downloader instance."""
        self.test_base_path = tempfile.mkdtemp()
        self.downloader = BatchDownloader(max_workers=2)

    def teardown_method(self):
        """Clean up temporary directory."""
        # Clean up any files created during tests
        if os.path.exists(self.test_base_path):
            for file in os.listdir(self.test_base_path):
                file_path = os.path.join(self.test_base_path, file)
                if os.path.isfile(file_path):
                    try:
                        os.unlink(file_path)
                    except:
                        pass  # Ignore cleanup errors
            try:
                os.rmdir(self.test_base_path)
            except:
                pass  # Ignore cleanup errors

    def testInit(self):
        """Test initialization."""
        downloader = BatchDownloader()
        assert downloader.max_workers == 3  # Default value
        assert downloader.progress_callback is None
        assert downloader.log_callback is None
        assert downloader.total_videos == 0
        assert downloader.completed_videos == 0

    def testInitWithParameters(self):
        """Test initialization with custom parameters."""
        progress_callback = Mock()
        log_callback = Mock()
        downloader = BatchDownloader(max_workers=5, progress_callback=progress_callback, log_callback=log_callback)
        assert downloader.max_workers == 5
        assert downloader.progress_callback == progress_callback
        assert downloader.log_callback == log_callback

    @patch('src.BatchDownloader.Mp4Downloader')
    def testDownloadBatchMp4Success(self, mock_mp4_downloader_class):
        """Test successful MP4 batch download."""
        # Mock MP4 downloader
        mock_mp4_downloader = Mock()
        mock_mp4_downloader_class.return_value = mock_mp4_downloader

        # Mock download methods
        mock_mp4_downloader.setUrl = Mock()
        mock_mp4_downloader.setPath = Mock()
        mock_mp4_downloader.downloadVideo = Mock()

        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': 'TestChannel/Playlist1'},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': 'TestChannel/Playlist1'}
        ]

        log_callback = Mock()
        progress_callback = Mock()

        downloader = BatchDownloader(max_workers=1, progress_callback=progress_callback, log_callback=log_callback)
        result = downloader.downloadBatch(video_list, 'MP4', self.test_base_path, 'highest')

        # Verify results
        assert result['successful'] == 2
        assert result['failed'] == 0
        assert result['errors'] == []

        # Verify MP4 downloader was called correctly
        assert mock_mp4_downloader_class.call_count == 2
        assert mock_mp4_downloader.setUrl.call_count == 2
        assert mock_mp4_downloader.setPath.call_count == 2
        assert mock_mp4_downloader.downloadVideo.call_count == 2

        # Verify callbacks were called
        assert log_callback.call_count >= 3  # Start, 2 completed, finished
        assert progress_callback.call_count >= 2  # Progress updates

    @patch('src.BatchDownloader.Mp3Downloader')
    def testDownloadBatchMp3Success(self, mock_mp3_downloader_class):
        """Test successful MP3 batch download."""
        # Mock MP3 downloader
        mock_mp3_downloader = Mock()
        mock_mp3_downloader_class.return_value = mock_mp3_downloader

        # Mock download methods
        mock_mp3_downloader.setUrl = Mock()
        mock_mp3_downloader.setPath = Mock()
        mock_mp3_downloader.downloadAsMp3 = Mock()

        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': 'TestChannel/Random'},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': 'TestChannel/Random'}
        ]

        log_callback = Mock()
        progress_callback = Mock()

        downloader = BatchDownloader(max_workers=1, progress_callback=progress_callback, log_callback=log_callback)
        result = downloader.downloadBatch(video_list, 'MP3', self.test_base_path, 'highest')

        # Verify results
        assert result['successful'] == 2
        assert result['failed'] == 0
        assert result['errors'] == []

        # Verify MP3 downloader was called correctly
        assert mock_mp3_downloader_class.call_count == 2
        assert mock_mp3_downloader.setUrl.call_count == 2
        assert mock_mp3_downloader.setPath.call_count == 2
        assert mock_mp3_downloader.downloadAsMp3.call_count == 2

    def testDownloadBatchEmptyList(self):
        """Test batch download with empty video list."""
        log_callback = Mock()
        downloader = BatchDownloader(log_callback=log_callback)

        result = downloader.downloadBatch([], 'MP4', self.test_base_path, 'highest')

        assert result['successful'] == 0
        assert result['failed'] == 0
        assert result['errors'] == []

        # Verify log callback was called
        log_callback.assert_called_with("No videos to download")

    def testDownloadBatchInvalidFormat(self):
        """Test batch download with invalid format."""
        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': ''}
        ]

        downloader = BatchDownloader()

        with patch('src.BatchDownloader.Mp4Downloader') as mock_mp4, \
             patch('src.BatchDownloader.Mp3Downloader') as mock_mp3:

            mock_mp4_downloader = Mock()
            mock_mp4.return_value = mock_mp4_downloader
            mock_mp4_downloader.setUrl = Mock()
            mock_mp4_downloader.setPath = Mock()
            mock_mp4_downloader.downloadVideo = Mock(side_effect=ValueError("Unsupported format: AVI"))

            result = downloader.downloadBatch(video_list, 'AVI', self.test_base_path, 'highest')

            assert result['successful'] == 0
            assert result['failed'] == 1
            assert len(result['errors']) == 1
            assert "Unsupported format: AVI" in result['errors'][0]

    @patch('src.BatchDownloader.Mp4Downloader')
    def testDownloadBatchPartialFailure(self, mock_mp4_downloader_class):
        """Test batch download with some failures."""
        # Mock downloaders - first succeeds, second fails
        mock_downloader1 = Mock()
        mock_downloader1.setUrl = Mock()
        mock_downloader1.setPath = Mock()
        mock_downloader1.downloadVideo = Mock()

        mock_downloader2 = Mock()
        mock_downloader2.setUrl = Mock()
        mock_downloader2.setPath = Mock()
        mock_downloader2.downloadVideo = Mock(side_effect=Exception("Download failed"))

        mock_mp4_downloader_class.side_effect = [mock_downloader1, mock_downloader2]

        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': ''},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': ''}
        ]

        log_callback = Mock()
        progress_callback = Mock()

        downloader = BatchDownloader(max_workers=1, progress_callback=progress_callback, log_callback=log_callback)
        result = downloader.downloadBatch(video_list, 'MP4', self.test_base_path, 'highest')

        assert result['successful'] == 1
        assert result['failed'] == 1
        assert len(result['errors']) == 1

    def testCancelDownload(self):
        """Test download cancellation."""
        log_callback = Mock()
        downloader = BatchDownloader(log_callback=log_callback)

        downloader.cancelDownload()

        assert downloader.cancel_event.is_set()
        log_callback.assert_called_with("Cancelling batch download...")

    def testCreateFolderStructureMp3(self):
        """Test folder structure creation for MP3 downloads."""
        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': 'Channel1/Playlist1'},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': 'Channel1/Random'},
            {'url': 'https://youtube.com/watch?v=3', 'title': 'Video 3', 'folder': ''}  # No folder
        ]

        organized_paths = self.downloader.createFolderStructure(video_list, self.test_base_path, 'MP3')

        expected_music_path = os.path.join(self.test_base_path, 'Music')
        expected_playlist_path = os.path.join(expected_music_path, 'Channel1', 'Playlist1')
        expected_random_path = os.path.join(expected_music_path, 'Channel1', 'Random')

        assert organized_paths['Channel1/Playlist1'] == expected_playlist_path
        assert organized_paths['Channel1/Random'] == expected_random_path
        assert organized_paths[''] == expected_music_path

        # Verify directories were created
        assert os.path.exists(expected_music_path)
        assert os.path.exists(expected_playlist_path)
        assert os.path.exists(expected_random_path)

    def testCreateFolderStructureMp4(self):
        """Test folder structure creation for MP4 downloads."""
        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': 'Channel1/Playlist1'}
        ]

        organized_paths = self.downloader.createFolderStructure(video_list, self.test_base_path, 'MP4')

        expected_videos_path = os.path.join(self.test_base_path, 'Videos')
        expected_playlist_path = os.path.join(expected_videos_path, 'Channel1', 'Playlist1')

        assert organized_paths['Channel1/Playlist1'] == expected_playlist_path

        # Verify directories were created
        assert os.path.exists(expected_videos_path)
        assert os.path.exists(expected_playlist_path)

    @patch('threading.Event')
    @patch('concurrent.futures.ThreadPoolExecutor')
    def testDownloadBatchCancellation(self, mock_executor_class, mock_event_class):
        """Test batch download cancellation during execution."""
        # Mock event
        mock_event = Mock()
        mock_event.is_set.side_effect = [False, False, True, True, True, True]  # Need more values for the mock
        mock_event_class.return_value = mock_event

        # Mock executor with context manager methods
        mock_executor = Mock()
        mock_executor_class.return_value = mock_executor
        mock_future = Mock()
        mock_future.result.return_value = (True, "")  # Success
        mock_executor.__enter__ = Mock(return_value=mock_executor)
        mock_executor.__exit__ = Mock(return_value=None)
        mock_executor.submit.return_value = mock_future

        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': ''},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': ''}
        ]

        log_callback = Mock()
        downloader = BatchDownloader(max_workers=1, log_callback=log_callback)

        with patch.object(downloader, 'downloadSingleVideo') as mock_download:
            mock_download.return_value = (True, "")
            result = downloader.downloadBatch(video_list, 'MP4', self.test_base_path, 'highest')

        # Should have cancelled after first video
        log_callback.assert_called_with("Batch download cancelled")

    @patch('src.BatchDownloader.Mp4Downloader')
    def testDownloadSingleVideoMp4(self, mock_mp4_downloader_class):
        """Test single MP4 video download."""
        mock_mp4_downloader = Mock()
        mock_mp4_downloader_class.return_value = mock_mp4_downloader

        video_info = {'url': 'https://youtube.com/watch?v=1', 'title': 'Test Video'}
        folder_path = os.path.join(self.test_base_path, 'test')

        success, error = self.downloader.downloadSingleVideo(video_info, 'MP4', folder_path, 'highest')

        assert success is True
        assert error == ""

        # Verify downloader was configured correctly
        mock_mp4_downloader.setUrl.assert_called_with('https://youtube.com/watch?v=1')
        mock_mp4_downloader.setPath.assert_called_with(folder_path)
        mock_mp4_downloader.downloadVideo.assert_called_once()

    @patch('src.BatchDownloader.Mp3Downloader')
    def testDownloadSingleVideoMp3(self, mock_mp3_downloader_class):
        """Test single MP3 video download."""
        mock_mp3_downloader = Mock()
        mock_mp3_downloader_class.return_value = mock_mp3_downloader

        video_info = {'url': 'https://youtube.com/watch?v=1', 'title': 'Test Video'}
        folder_path = os.path.join(self.test_base_path, 'test')

        success, error = self.downloader.downloadSingleVideo(video_info, 'MP3', folder_path, 'highest')

        assert success is True
        assert error == ""

        # Verify downloader was configured correctly
        mock_mp3_downloader.setUrl.assert_called_with('https://youtube.com/watch?v=1')
        mock_mp3_downloader.setPath.assert_called_with(folder_path)
        mock_mp3_downloader.downloadAsMp3.assert_called_once()

    def testDownloadSingleVideoInvalidFormat(self):
        """Test single video download with invalid format."""
        video_info = {'url': 'https://youtube.com/watch?v=1', 'title': 'Test Video'}
        folder_path = os.path.join(self.test_base_path, 'test')

        success, error = self.downloader.downloadSingleVideo(video_info, 'AVI', folder_path, 'highest')

        assert success is False
        assert "Unsupported format: AVI" in error

    @patch('src.BatchDownloader.Mp4Downloader')
    def testDownloadSingleVideoException(self, mock_mp4_downloader_class):
        """Test single video download with exception."""
        mock_mp4_downloader = Mock()
        mock_mp4_downloader_class.return_value = mock_mp4_downloader
        mock_mp4_downloader.downloadVideo.side_effect = Exception("Network error")

        video_info = {'url': 'https://youtube.com/watch?v=1', 'title': 'Test Video'}
        folder_path = os.path.join(self.test_base_path, 'test')

        success, error = self.downloader.downloadSingleVideo(video_info, 'MP4', folder_path, 'highest')

        assert success is False
        assert error == "Network error"
