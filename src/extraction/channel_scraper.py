"""
Channel scraper module for extracting playlists and uploaded videos from YouTube channels.

Coordinates channel discovery and integrates with PlaylistScraper to extract
all videos across channel playlists and uploads.
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional
import yt_dlp

from .cookie_manager import CookieManager
from .playlist_scraper import PlaylistScraper
from .utils import sanitizeFilename


class ChannelScraper:
    """
    Scrapes content from YouTube channels.

    Extracts playlists and standalone uploaded videos from a channel URL,
    coordinating with PlaylistScraper for detailed playlist extraction.
    """

    def __init__(
        self,
        timeout: float = 2.0,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initializes the ChannelScraper instance with request timeout and logging callback.

        Args:
            timeout (float): Interval timeout between requests in seconds (default: 2.0).
            log_callback (Optional[Callable[[str], None]], optional): Logging callback.
        """
        self.timeout = timeout
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    def scrapeChannel(
        self,
        url: str,
        max_videos_per_playlist: int = 200,
        progress_callback: Optional[Callable[[int, int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Scrapes playlists and standalone videos from a YouTube channel.

        Args:
            url (str): The channel URL to scrape.
            max_videos_per_playlist (int): Limit for videos per playlist (default: 200).
            progress_callback (Optional[Callable[[int, int, int]], optional): Progress update callback.

        Returns:
            Dict[str, Any]: Scraped channel dictionary: {'channel_name': str, 'playlists': list, 'standalone_videos': list}.

        Raises:
            Exception: If channel extraction fails.
        """
        channel_info: Dict[str, Any] = {
            'channel_name': 'Unknown Channel',
            'playlists': [],
            'standalone_videos': [],
        }

        try:
            channel_url = self.normalizeChannelUrl(url)
            channel_info['channel_name'] = self.getChannelName(channel_url)

            if progress_callback:
                progress_callback(0, 100, 0)

            playlists = self.getChannelPlaylists(channel_url)
            total_tasks = len(playlists) + 1
            completed = 0

            for playlist in playlists:
                try:
                    scraper = PlaylistScraper(timeout=self.timeout, log_callback=self.log_callback)

                    def nestedProgress(current: int, total: int, percentage: int) -> None:
                        if progress_callback:
                            overall_percentage = int(((completed + (percentage / 100)) / total_tasks) * 100)
                            progress_callback(completed + 1, total_tasks, overall_percentage)

                    videos = scraper.scrapePlaylist(playlist['url'], max_videos_per_playlist, nestedProgress)

                    playlist_info = {
                        'title': playlist['title'],
                        'url': playlist['url'],
                        'videos': videos,
                    }
                    channel_info['playlists'].append(playlist_info)

                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total_tasks, int((completed / total_tasks) * 100))

                    time.sleep(self.timeout)

                except Exception as exc:
                    logging.warning(f"Failed to scrape playlist {playlist.get('title')}: {exc}")
                    completed += 1
                    continue

            channel_info['standalone_videos'] = self.getStandaloneVideos(channel_url, max_videos_per_playlist)

            completed += 1
            if progress_callback:
                progress_callback(completed, total_tasks, 100)

        except Exception as exc:
            logging.error(f"Error scraping channel: {exc}")
            raise

        return channel_info

    def normalizeChannelUrl(self, url: str) -> str:
        """
        Normalizes various YouTube channel URL formats to consistent structure.

        Args:
            url (str): The raw channel URL.

        Returns:
            str: The normalized channel URL.
        """
        if '/channel/' in url:
            return url
        elif '/user/' in url:
            username = url.split('/user/')[-1].split('/')[0]
            return f"https://www.youtube.com/user/{username}"
        return url

    def getChannelName(self, url: str) -> str:
        """
        Retrieves the name of the YouTube channel.

        Args:
            url (str): The channel URL.

        Returns:
            str: The extracted channel name.
        """
        try:
            cookie_file = self.cookie_manager.getCookieFile()
            ydl_opts: Dict[str, Any] = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('channel', 'Unknown Channel')

        except Exception as exc:
            logging.error(f"Error getting channel name: {exc}")
            return 'Unknown Channel'

    def getChannelPlaylists(self, channel_url: str) -> List[Dict[str, str]]:
        """
        Retrieves all playlists from a channel URL.

        Args:
            channel_url (str): The base channel URL.

        Returns:
            List[Dict[str, str]]: List of playlist item dictionaries containing title and url.
        """
        playlists: List[Dict[str, str]] = []
        playlists_url = f"{channel_url}/playlists"

        try:
            cookie_file = self.cookie_manager.getCookieFile()
            ydl_opts: Dict[str, Any] = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlists_url, download=False)

                if info and 'entries' in info:
                    for entry in info['entries']:
                        if entry and entry.get('title') and 'playlist' in entry.get('url', '').lower():
                            playlists.append({
                                'title': entry['title'],
                                'url': entry['url'],
                            })
                            time.sleep(self.timeout)

        except Exception as exc:
            logging.warning(f"Could not extract playlists: {exc}")

        return playlists

    def getStandaloneVideos(self, channel_url: str, max_videos: int = 200) -> List[Dict[str, Any]]:
        """
        Retrieves standalone uploaded videos from a channel.

        Args:
            channel_url (str): The base channel URL.
            max_videos (int): Maximum number of videos to retrieve (default: 200).

        Returns:
            List[Dict[str, Any]]: List of video dictionaries with url, title, and duration.
        """
        videos: List[Dict[str, Any]] = []
        videos_url = f"{channel_url}/videos"

        try:
            cookie_file = self.cookie_manager.getCookieFile()
            ydl_opts: Dict[str, Any] = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(videos_url, download=False)

                if info and 'entries' in info:
                    for entry in info['entries'][:max_videos]:
                        if entry:
                            video_id = entry.get('id')
                            video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else entry.get('url', '')

                            if video_url and entry.get('title'):
                                videos.append({
                                    'url': video_url,
                                    'title': sanitizeFilename(entry['title']),
                                    'duration': entry.get('duration', 0),
                                })

        except Exception as exc:
            logging.warning(f"Could not extract standalone videos: {exc}")

        return videos
