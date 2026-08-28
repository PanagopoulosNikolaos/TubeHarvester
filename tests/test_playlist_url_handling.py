"""
Tests for playlist URL handling and normalization.
"""

import logging
from unittest.mock import Mock, patch
import pytest

from src.extraction.playlist_scraper import PlaylistScraper


def testPlaylistUrlNormalization() -> None:
    """
    Tests playlist normalization for various YouTube URL patterns.
    """
    scraper = PlaylistScraper(timeout=0.0)

    video_url_with_playlist = "https://www.youtube.com/watch?v=zk3T2qtK2B0&list=PLrxcNWZXdQ2l9Jnr8-thveoeoQlBUSFOw"
    direct_playlist_url = "https://www.youtube.com/playlist?list=PLrxcNWZXdQ2l9Jnr8-thveoeoQlBUSFOw"

    normalized_from_watch = scraper.normalizePlaylistUrl(video_url_with_playlist)
    normalized_direct = scraper.normalizePlaylistUrl(direct_playlist_url)

    assert "playlist?list=PLrxcNWZXdQ2l9Jnr8-thveoeoQlBUSFOw" in normalized_from_watch
    assert "playlist?list=PLrxcNWZXdQ2l9Jnr8-thveoeoQlBUSFOw" in normalized_direct


@patch('time.sleep')
@patch('yt_dlp.YoutubeDL')
def testPlaylistScrapingMocked(mock_ydl_class: Mock, mock_sleep: Mock) -> None:
    """
    Tests playlist scraping workflow with mocked yt-dlp extractor.
    """
    mock_ydl = Mock()
    mock_ydl.__enter__ = Mock(return_value=mock_ydl)
    mock_ydl.__exit__ = Mock(return_value=None)
    mock_ydl.extract_info.return_value = {
        'title': 'Test Playlist',
        'entries': [
            {'id': 'zk3T2qtK2B0', 'title': 'Test Song', 'duration': 210},
        ],
    }
    mock_ydl_class.return_value = mock_ydl

    scraper = PlaylistScraper(timeout=0.0)
    title = scraper.getPlaylistTitle("https://www.youtube.com/playlist?list=PLtest")
    videos = scraper.scrapePlaylist("https://www.youtube.com/playlist?list=PLtest", max_videos=5)

    assert title == "Test_Playlist"
    assert len(videos) == 1
    assert videos[0]['url'] == "https://www.youtube.com/watch?v=zk3T2qtK2B0"
