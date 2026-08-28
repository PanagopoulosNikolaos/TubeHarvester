"""
Playlist scraper module for extracting video links and metadata from YouTube playlists.

Supports standard public and unlisted playlists as well as YouTube algorithmic mixes.
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import parse_qs, urlparse
import yt_dlp

from .cookie_manager import CookieManager
from .utils import sanitizeFilename


class PlaylistScraper:
    """
    Scrapes video items and metadata from YouTube playlists.

    Provides functionality to extract video URLs, titles, and durations
    from standard playlists and YouTube algorithmic mixes.
    """

    def __init__(
        self,
        timeout: float = 2.0,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initializes the PlaylistScraper with rate-limit timeout and logging callback.

        Args:
            timeout (float): Timeout interval between requests in seconds (default: 2.0).
            log_callback (Optional[Callable[[str], None]], optional): Logging callback.
        """
        self.timeout = timeout
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    def isYoutubeMix(self, playlist_id: str) -> bool:
        """
        Determines whether the given playlist ID represents an algorithmic YouTube mix.

        Args:
            playlist_id (str): The playlist ID to inspect.

        Returns:
            bool: True if the playlist ID matches known mix prefixes, False otherwise.
        """
        mix_prefixes = [
            'RD', 'RDE', 'RDCL', 'RDCLAK', 'RDAMVM', 'RDCM',
            'RDEO', 'RDFM', 'RDKM', 'RDM', 'RDTM', 'RDV',
        ]
        return any(playlist_id.startswith(prefix) for prefix in mix_prefixes)

    def normalizePlaylistUrl(self, url: str) -> str:
        """
        Normalizes arbitrary YouTube playlist URLs to canonical structure.

        Args:
            url (str): The raw input YouTube playlist or video URL.

        Returns:
            str: The normalized canonical playlist URL.
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)

            if 'list' in query_params:
                playlist_id = query_params['list'][0]

                # Constructs watch-list URL for YouTube algorithmic mixes.
                if self.isYoutubeMix(playlist_id):
                    video_id = query_params.get('v', [None])[0]
                    if video_id:
                        return f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"

                return f"https://www.youtube.com/playlist?list={playlist_id}"

            return url

        except Exception as exc:
            logging.warning(f"Error normalizing URL: {exc}")
            return url

    def scrapePlaylist(
        self,
        url: str,
        max_videos: int = 200,
        progress_callback: Optional[Callable[[int, int, int], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extracts a list of video entries from the specified YouTube playlist.

        Args:
            url (str): The playlist URL to scrape.
            max_videos (int): Maximum number of videos to scrape (default: 200).
            progress_callback (Optional[Callable[[int, int, int]], optional): Called with (current, total, percentage).

        Returns:
            List[Dict[str, Any]]: List of video dictionary items containing url, title, and duration.

        Raises:
            Exception: If playlist extraction fails completely.
        """
        videos: List[Dict[str, Any]] = []

        try:
            normalized_url = self.normalizePlaylistUrl(url)
            parsed_url = urlparse(normalized_url)
            query_params = parse_qs(parsed_url.query)
            playlist_id = query_params.get('list', [None])[0] if 'list' in query_params else None

            is_mix = bool(playlist_id and self.isYoutubeMix(playlist_id))
            cookie_file = self.cookie_manager.getCookieFile()

            ydl_opts: Dict[str, Any] = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file

            if is_mix:
                ydl_opts['extract_flat'] = 'in_playlist'

            # Extracts flat playlist entries without downloading video media.
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    playlist_info = ydl.extract_info(normalized_url, download=False)
                except yt_dlp.DownloadError as exc:
                    if is_mix and 'v' in query_params:
                        video_id = query_params['v'][0]
                        watch_url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                        playlist_info = ydl.extract_info(watch_url, download=False)
                    else:
                        raise exc

                if playlist_info and 'entries' in playlist_info and playlist_info['entries']:
                    entries = playlist_info['entries'][:max_videos]
                    total = len(entries)

                    for idx, entry in enumerate(entries, 1):
                        if entry:
                            video_id = entry.get('id', '')
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            video_data = {
                                'url': video_url,
                                'title': sanitizeFilename(entry.get('title', 'Unknown Title')),
                                'duration': entry.get('duration', 0),
                            }
                            videos.append(video_data)

                            if progress_callback:
                                percentage = int((len(videos) / total) * 100)
                                progress_callback(len(videos), total, percentage)

                            # Applies rate limiting between video item parsing.
                            time.sleep(self.timeout)
                else:
                    logging.warning(f"No entries found in playlist: {normalized_url}")

        except Exception as exc:
            logging.error(f"Error scraping playlist: {exc}")
            raise

        return videos

    def getPlaylistTitle(self, url: str) -> str:
        """
        Retrieves the sanitized title of a YouTube playlist.

        Args:
            url (str): The playlist URL.

        Returns:
            str: The sanitized playlist title string.
        """
        try:
            normalized_url = self.normalizePlaylistUrl(url)
            parsed_url = urlparse(normalized_url)
            query_params = parse_qs(parsed_url.query)
            playlist_id = query_params.get('list', [None])[0] if 'list' in query_params else None

            is_mix = bool(playlist_id and self.isYoutubeMix(playlist_id))
            cookie_file = self.cookie_manager.getCookieFile()

            ydl_opts: Dict[str, Any] = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(normalized_url, download=False)
                    return sanitizeFilename(info.get('title', 'Unknown Playlist'))
                except yt_dlp.DownloadError as exc:
                    if is_mix and 'v' in query_params:
                        video_id = query_params['v'][0]
                        watch_url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                        info = ydl.extract_info(watch_url, download=False)
                        return sanitizeFilename(info.get('title', 'Unknown Playlist'))
                    else:
                        raise exc

        except Exception as exc:
            logging.error(f"Error getting playlist title: {exc}")
            return 'Unknown Playlist'
