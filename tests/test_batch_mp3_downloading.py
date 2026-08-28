"""
Tests for batch MP3 structure and downloader orchestration.
"""

import os
import tempfile
from unittest.mock import Mock, patch
import pytest

from src.extraction.batch_downloader import BatchDownloader
from src.extraction.playlist_scraper import PlaylistScraper


def testMp3BatchFolderStructure() -> None:
    """
    Tests folder hierarchy creation for batch MP3 audio conversion queues.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        batch_downloader = BatchDownloader(max_workers=1)
        video_list = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Song 1', 'folder': 'Playlists/Rock'},
            {'url': 'https://youtube.com/watch?v=2', 'title': 'Song 2', 'folder': 'Playlists/Rock'},
        ]

        organized_paths = batch_downloader.createFolderStructure(video_list, temp_dir, "MP3")
        expected_folder = os.path.join(temp_dir, "Music", "Playlists", "Rock")

        assert organized_paths['Playlists/Rock'] == expected_folder
        assert os.path.exists(expected_folder)
