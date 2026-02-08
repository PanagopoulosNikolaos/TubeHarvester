import yt_dlp
import time
import logging
from urllib.parse import urlparse, parse_qs
from .CookieManager import CookieManager
from .utils import sanitizeFilename

class PlaylistScraper:
    """
    Scrapes video information from YouTube playlists.

    This class provides functionality to extract video URLs, titles, and durations
    from standard playlists and YouTube algorithmic mixes.
    """

    def __init__(self, timeout=2.0, log_callback=None):
        """
        Initializes the PlaylistScraper.

        Args:
            timeout (float): Timeout between requests in seconds (default: 2.0).
            log_callback (callable, optional): Called with log messages.
        """
        self.timeout = timeout
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    def isYoutubeMix(self, playlist_id):
        """
        Checks if the playlist ID corresponds to a YouTube mix.

        Args:
            playlist_id (str): The playlist ID to check.

        Returns:
            bool: True if it's a mix, False otherwise.
        """
        mix_prefixes = ['RD', 'RDE', 'RDCL', 'RDCLAK', 'RDAMVM', 'RDCM', 'RDEO', 'RDFM', 'RDKM', 'RDM', 'RDTM', 'RDV']
        return any(playlist_id.startswith(prefix) for prefix in mix_prefixes)

    def normalizePlaylistUrl(self, url):
        """
        Normalizes a playlist URL to a standard format.

        Args:
            url (str): The input YouTube URL.

        Returns:
            str: The normalized playlist URL.
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if 'list' in query_params:
                playlist_id = query_params['list'][0]
                
                if self.isYoutubeMix(playlist_id):
                    video_id = query_params.get('v', [None])[0]
                    if video_id:
                        return f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                
                return f"https://www.youtube.com/playlist?list={playlist_id}"
            
            return url
            
        except Exception as e:
            logging.warning(f"Error normalizing URL: {e}")
            return url

    def scrapePlaylist(self, url, max_videos=200, progress_callback=None):
        """
        Extracts video list from a YouTube playlist.

        Args:
            url (str): The playlist URL.
            max_videos (int): Limit for videos scraped (default: 200).
            progress_callback (callable, optional): Called with (current, total, percentage).

        Returns:
            list: List of video info dicts.
        """
        videos = []

        try:
            normalized_url = self.normalizePlaylistUrl(url)
            parsed_url = urlparse(normalized_url)
            query_params = parse_qs(parsed_url.query)
            playlist_id = query_params.get('list', [None])[0] if 'list' in query_params else None
            
            is_mix = playlist_id and self.isYoutubeMix(playlist_id)
            cookie_file = self.cookie_manager.getCookieFile()
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'javascript_executor': 'deno',
            }
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file
            
            if is_mix:
                ydl_opts['extract_flat'] = 'in_playlist'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    playlist_info = ydl.extract_info(normalized_url, download=False)
                except yt_dlp.DownloadError as e:
                    if is_mix and 'v' in query_params:
                        video_id = query_params['v'][0]
                        watch_url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                        playlist_info = ydl.extract_info(watch_url, download=False)
                    else:
                        raise e

                if 'entries' in playlist_info and playlist_info['entries']:
                    entries = playlist_info['entries'][:max_videos]
                    total = len(entries)
                    
                    for idx, entry in enumerate(entries, 1):
                        if entry:
                            video_url = f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                            video_data = {
                                'url': video_url,
                                'title': sanitizeFilename(entry.get('title', 'Unknown Title')),
                                'duration': entry.get('duration', 0)
                            }
                            videos.append(video_data)
                            
                            if progress_callback:
                                percentage = int((len(videos) / total) * 100)
                                progress_callback(len(videos), total, percentage)

                            time.sleep(self.timeout)
                else:
                    logging.warning(f"No entries found in playlist: {normalized_url}")

        except Exception as e:
            logging.error(f"Error scraping playlist: {e}")
            raise

        return videos

    def getPlaylistTitle(self, url):
        """
        Retrieves the title of a YouTube playlist.

        Args:
            url (str): The playlist URL.

        Returns:
            str: The playlist title.
        """
        try:
            normalized_url = self.normalizePlaylistUrl(url)
            parsed_url = urlparse(normalized_url)
            query_params = parse_qs(parsed_url.query)
            playlist_id = query_params.get('list', [None])[0] if 'list' in query_params else None
            
            is_mix = playlist_id and self.isYoutubeMix(playlist_id)
            cookie_file = self.cookie_manager.getCookieFile()
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'javascript_executor': 'deno',
            }
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(normalized_url, download=False)
                    return sanitizeFilename(info.get('title', 'Unknown Playlist'))
                except yt_dlp.DownloadError as e:
                    if is_mix and 'v' in query_params:
                        video_id = query_params['v'][0]
                        watch_url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                        info = ydl.extract_info(watch_url, download=False)
                        return sanitizeFilename(info.get('title', 'Unknown Playlist'))
                    else:
                        raise e

        except Exception as e:
            logging.error(f"Error getting playlist title: {e}")
            return 'Unknown Playlist'
