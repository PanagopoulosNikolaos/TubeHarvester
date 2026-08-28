"""
Unit tests for BatchDownloader module.
"""

import os
import tempfile
from unittest.mock import Mock, patch
import pytest

from src.extraction.batch_downloader import BatchDownloader


class TestBatchDownloader:
    """
    Test suite for BatchDownloader operations, threading, and queue management.
    """

    def setup_method(self) -> None:
        """
        Initializes temporary directory and BatchDownloader instance.
        """
        self.test_base_path = tempfile.mkdtemp()
        self.downloader = BatchDownloader(max_workers=2)

    def teardown_method(self) -> None:
        """
        Cleans up temporary files and directories after test runs.
        """
        if os.path.exists(self.test_base_path):
            for file in os.listdir(self.test_base_path):
                file_path = os.path.join(self.test_base_path, file)
                if os.path.isfile(file_path):
                    try:
                        os.unlink(file_path)
                    except Exception:
                        pass
            try:
                os.rmdir(self.test_base_path)
            except Exception:
                pass

    def testInit(self) -> None:
        """
        Tests default initialization attributes.
        """
        downloader = BatchDownloader()
        assert downloader.max_workers == 3
        assert downloader.progress_callback is None
        assert downloader.log_callback is None
        assert downloader.total_videos == 0
        assert downloader.completed_videos == 0

    def testInitWithParameters(self) -> None:
        """
        Tests initialization with explicit parameters and callbacks.
        """
        progress_callback = Mock()
        log_callback = Mock()
        downloader = BatchDownloader(
            max_workers=5,
            progress_callback=progress_callback,
            log_callback=log_callback,
        )
        assert downloader.max_workers == 5
        assert downloader.progress_callback == progress_callback
        assert downloader.log_callback == log_callback

    @patch('src.extraction.batch_downloader.Mp4Downloader')
    def testDownloadBatchMp4Success(self, mock_mp4_downloader_class: Mock) -> None:
        """
        Tests successful MP4 batch download execution.
        """
        mock_mp4_downloader = Mock()
        mock_mp4_downloader_class.return_value = mock_mp4_downloader
        mock_mp4_downloader.setUrl = Mock()
        mock_mp4_downloader.setPath = Mock()
        mock_mp4_downloader.downloadVideo = Mock()

        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': 'TestChannel/Playlist1'},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': 'TestChannel/Playlist1'},
        ]

        log_callback = Mock()
        progress_callback = Mock()

        downloader = BatchDownloader(max_workers=1, progress_callback=progress_callback, log_callback=log_callback)
        result = downloader.downloadBatch(video_list, 'MP4', self.test_base_path, 'highest')

        assert result['successful'] == 2
        assert result['failed'] == 0
        assert result['errors'] == []

        assert mock_mp4_downloader_class.call_count == 2
        assert mock_mp4_downloader.setUrl.call_count == 2
        assert mock_mp4_downloader.setPath.call_count == 2
        assert mock_mp4_downloader.downloadVideo.call_count == 2

        assert log_callback.call_count >= 3
        assert progress_callback.call_count >= 2

    @patch('src.extraction.batch_downloader.Mp3Downloader')
    def testDownloadBatchMp3Success(self, mock_mp3_downloader_class: Mock) -> None:
        """
        Tests successful MP3 batch download execution.
        """
        mock_mp3_downloader = Mock()
        mock_mp3_downloader_class.return_value = mock_mp3_downloader
        mock_mp3_downloader.setUrl = Mock()
        mock_mp3_downloader.setPath = Mock()
        mock_mp3_downloader.downloadAsMp3 = Mock()

        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': 'TestChannel/Random'},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': 'TestChannel/Random'},
        ]

        log_callback = Mock()
        progress_callback = Mock()

        downloader = BatchDownloader(max_workers=1, progress_callback=progress_callback, log_callback=log_callback)
        result = downloader.downloadBatch(video_list, 'MP3', self.test_base_path, 'highest')

        assert result['successful'] == 2
        assert result['failed'] == 0
        assert result['errors'] == []

        assert mock_mp3_downloader_class.call_count == 2
        assert mock_mp3_downloader.setUrl.call_count == 2
        assert mock_mp3_downloader.setPath.call_count == 2
        assert mock_mp3_downloader.downloadAsMp3.call_count == 2

    def testDownloadBatchEmptyList(self) -> None:
        """
        Tests batch download handling with an empty queue.
        """
        log_callback = Mock()
        downloader = BatchDownloader(log_callback=log_callback)

        result = downloader.downloadBatch([], 'MP4', self.test_base_path, 'highest')

        assert result['successful'] == 0
        assert result['failed'] == 0
        assert result['errors'] == []
        log_callback.assert_called_with("No videos to download")

    def testDownloadBatchInvalidFormat(self) -> None:
        """
        Tests error tracking when an invalid format is supplied.
        """
        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': ''},
        ]

        downloader = BatchDownloader()
        result = downloader.downloadBatch(video_list, 'AVI', self.test_base_path, 'highest')

        assert result['successful'] == 0
        assert result['failed'] == 1
        assert len(result['errors']) == 1
        assert "Unsupported format: AVI" in result['errors'][0]

    @patch('src.extraction.batch_downloader.Mp4Downloader')
    def testDownloadBatchPartialFailure(self, mock_mp4_downloader_class: Mock) -> None:
        """
        Tests batch download with a mixture of successful and failing downloads.
        """
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
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': ''},
        ]

        log_callback = Mock()
        progress_callback = Mock()

        downloader = BatchDownloader(max_workers=1, progress_callback=progress_callback, log_callback=log_callback)
        result = downloader.downloadBatch(video_list, 'MP4', self.test_base_path, 'highest')

        assert result['successful'] == 1
        assert result['failed'] == 1
        assert len(result['errors']) == 1

    def testCancelDownload(self) -> None:
        """
        Tests cancellation signal propagation.
        """
        log_callback = Mock()
        downloader = BatchDownloader(log_callback=log_callback)

        downloader.cancelDownload()

        assert downloader.cancel_event.is_set()
        log_callback.assert_called_with("Cancelling batch download...")

    def testCreateFolderStructureMp3(self) -> None:
        """
        Tests folder hierarchy generation for MP3 files.
        """
        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': 'Channel1/Playlist1'},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Video 2', 'folder': 'Channel1/Random'},
            {'url': 'https://youtube.com/watch?v=3', 'title': 'Video 3', 'folder': ''},
        ]

        organized_paths = self.downloader.createFolderStructure(video_list, self.test_base_path, 'MP3')

        expected_music_path = os.path.join(self.test_base_path, 'Music')
        expected_playlist_path = os.path.join(expected_music_path, 'Channel1', 'Playlist1')
        expected_random_path = os.path.join(expected_music_path, 'Channel1', 'Random')

        assert organized_paths['Channel1/Playlist1'] == expected_playlist_path
        assert organized_paths['Channel1/Random'] == expected_random_path
        assert organized_paths[''] == expected_music_path

        assert os.path.exists(expected_music_path)
        assert os.path.exists(expected_playlist_path)
        assert os.path.exists(expected_random_path)

    def testCreateFolderStructureMp4(self) -> None:
        """
        Tests folder hierarchy generation for MP4 files.
        """
        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'folder': 'Channel1/Playlist1'},
        ]

        organized_paths = self.downloader.createFolderStructure(video_list, self.test_base_path, 'MP4')

        expected_videos_path = os.path.join(self.test_base_path, 'Videos')
        expected_playlist_path = os.path.join(expected_videos_path, 'Channel1', 'Playlist1')

        assert organized_paths['Channel1/Playlist1'] == expected_playlist_path
        assert os.path.exists(expected_videos_path)
        assert os.path.exists(expected_playlist_path)

    @patch('src.extraction.batch_downloader.Mp4Downloader')
    def testDownloadSingleVideoMp4(self, mock_mp4_downloader_class: Mock) -> None:
        """
        Tests downloading a single MP4 video task.
        """
        mock_mp4_downloader = Mock()
        mock_mp4_downloader_class.return_value = mock_mp4_downloader

        video_info = {'url': 'https://youtube.com/watch?v=1', 'title': 'Test Video'}
        folder_path = os.path.join(self.test_base_path, 'test')

        success, error = self.downloader.downloadSingleVideo(video_info, 'MP4', folder_path, 'highest')

        assert success is True
        assert error == ""
        mock_mp4_downloader.setUrl.assert_called_with('https://youtube.com/watch?v=1')
        mock_mp4_downloader.setPath.assert_called_with(folder_path)
        mock_mp4_downloader.downloadVideo.assert_called_once()

    @patch('src.extraction.batch_downloader.Mp3Downloader')
    def testDownloadSingleVideoMp3(self, mock_mp3_downloader_class: Mock) -> None:
        """
        Tests downloading a single MP3 audio task.
        """
        mock_mp3_downloader = Mock()
        mock_mp3_downloader_class.return_value = mock_mp3_downloader

        video_info = {'url': 'https://youtube.com/watch?v=1', 'title': 'Test Video'}
        folder_path = os.path.join(self.test_base_path, 'test')

        success, error = self.downloader.downloadSingleVideo(video_info, 'MP3', folder_path, 'highest')

        assert success is True
        assert error == ""
        mock_mp3_downloader.setUrl.assert_called_with('https://youtube.com/watch?v=1')
        mock_mp3_downloader.setPath.assert_called_with(folder_path)
        mock_mp3_downloader.downloadAsMp3.assert_called_once()

    def testDownloadSingleVideoInvalidFormat(self) -> None:
        """
        Tests single video error handling for unsupported formats.
        """
        video_info = {'url': 'https://youtube.com/watch?v=1', 'title': 'Test Video'}
        folder_path = os.path.join(self.test_base_path, 'test')

        success, error = self.downloader.downloadSingleVideo(video_info, 'AVI', folder_path, 'highest')
        assert success is False
        assert "Unsupported format: AVI" in error

    @patch('src.extraction.batch_downloader.Mp4Downloader')
    def testDownloadSingleVideoException(self, mock_mp4_downloader_class: Mock) -> None:
        """
        Tests exception propagation during single video execution.
        """
        mock_mp4_downloader = Mock()
        mock_mp4_downloader_class.return_value = mock_mp4_downloader
        mock_mp4_downloader.downloadVideo.side_effect = Exception("Network error")

        video_info = {'url': 'https://youtube.com/watch?v=1', 'title': 'Test Video'}
        folder_path = os.path.join(self.test_base_path, 'test')

        success, error = self.downloader.downloadSingleVideo(video_info, 'MP4', folder_path, 'highest')

        assert success is False
        assert error == "Network error"
