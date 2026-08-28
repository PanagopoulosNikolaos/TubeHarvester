"""
Tests for YouTube mix detection and normalization.
"""

from unittest.mock import Mock, patch
import pytest

from src.extraction.playlist_scraper import PlaylistScraper


def testYoutubeMixDetection() -> None:
    """
    Tests detection of algorithmic mix identifiers.
    """
    scraper = PlaylistScraper()
    mix_ids = ['RDxxxx', 'RDExxxx', 'RDCLxxxx', 'RDCLAKxxxx', 'RDAMVMxxxx', 'RDCMxxxx']
    non_mix_ids = ['PLxxxx', 'UUxxxx', 'UCxxxx']

    for mix_id in mix_ids:
        assert scraper.isYoutubeMix(mix_id) is True

    for non_mix_id in non_mix_ids:
        assert scraper.isYoutubeMix(non_mix_id) is False


def testUrlNormalization() -> None:
    """
    Tests normalizing mix URLs vs regular playlist URLs.
    """
    scraper = PlaylistScraper()

    mix_url_with_video = "https://www.youtube.com/watch?v=xxx&list=RDNrIhy2b54NE"
    normalized_mix = scraper.normalizePlaylistUrl(mix_url_with_video)
    assert "watch?v=xxx&list=RDNrIhy2b54NE" in normalized_mix

    regular_url = "https://www.youtube.com/playlist?list=PLxxxx"
    normalized_regular = scraper.normalizePlaylistUrl(regular_url)
    assert "playlist?list=PLxxxx" in normalized_regular
