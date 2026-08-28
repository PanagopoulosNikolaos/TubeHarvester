"""
Extraction package for TubeHarvester.

Provides modules for video/audio downloading, playlist and channel scraping,
cookie management, and batch download coordination.
"""

from .utils import sanitizeFilename
from .cookie_manager import CookieManager
from .mp4_downloader import Mp4Downloader
from .mp3_downloader import Mp3Downloader
from .playlist_scraper import PlaylistScraper
from .channel_scraper import ChannelScraper
from .batch_downloader import BatchDownloader

__all__ = [
    "sanitizeFilename",
    "CookieManager",
    "Mp4Downloader",
    "Mp3Downloader",
    "PlaylistScraper",
    "ChannelScraper",
    "BatchDownloader",
]
