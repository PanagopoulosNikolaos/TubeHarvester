import yt_dlp
import time
import logging
from .PlaylistScraper import PlaylistScraper
from .CookieManager import CookieManager
from .utils import sanitizeFilename

class ChannelScraper:
    """
    Scrapes content from YouTube channels.

    This class extracts playlists and standalone videos from a channel URL,
    coordinating with PlaylistScraper for detailed playlist extraction.
    """

    def __init__(self, timeout=2.0, log_callback=None):
        """
        Initializes the ChannelScraper.

        Args:
            timeout (float): Timeout between requests in seconds (default: 2.0).
            log_callback (callable, optional): Called with log messages.
        """
        self.timeout = timeout
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    def scrapeChannel(self, url, max_videos_per_playlist=200, progress_callback=None):
        """
        Scrapes playlists and videos from a channel.

        Args:
            url (str): The channel URL.
            max_videos_per_playlist (int): Limit for videos per playlist (default: 200).
            progress_callback (callable, optional): Called with progress updates.

        Returns:
            dict: Scraped channel content: {'channel_name': str, 'playlists': list, 'standalone_videos': list}.
        """
        channel_info = {
            'channel_name': 'Unknown Channel',
            'playlists': [],
            'standalone_videos': []
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
                    
                    def nestedProgress(current, total, percentage):
                        if progress_callback:
                            overall_percentage = int(((completed + (percentage / 100)) / total_tasks) * 100)
                            progress_callback(completed + 1, total_tasks, overall_percentage)
                    
                    videos = scraper.scrapePlaylist(playlist['url'], max_videos_per_playlist, nestedProgress)

                    playlist_info = {
                        'title': playlist['title'],
                        'url': playlist['url'],
                        'videos': videos
                    }
                    channel_info['playlists'].append(playlist_info)

                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total_tasks, int((completed / total_tasks) * 100))

                    time.sleep(self.timeout)

                except Exception as e:
                    logging.warning(f"Failed to scrape playlist {playlist.get('title')}: {e}")
                    completed += 1
                    continue

            channel_info['standalone_videos'] = self.getStandaloneVideos(channel_url, max_videos_per_playlist)
            
            completed += 1
            if progress_callback:
                progress_callback(completed, total_tasks, 100)

        except Exception as e:
            logging.error(f"Error scraping channel: {e}")
            raise

        return channel_info

    def normalizeChannelUrl(self, url):
        """
        Normalizes various YouTube channel URL formats.

        Args:
            url (str): The channel URL.

        Returns:
            str: The normalized URL.
        """
        if '/channel/' in url:
            return url
        elif '/user/' in url:
            username = url.split('/user/')[-1].split('/')[0]
            return f"https://www.youtube.com/user/{username}"
        return url

    def getChannelName(self, url):
        """
        Retrieves the name of the YouTube channel.

        Args:
            url (str): The channel URL.

        Returns:
            str: The channel name.
        """
        try:
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
                info = ydl.extract_info(url, download=False)
                return info.get('channel', 'Unknown Channel')

        except Exception as e:
            logging.error(f"Error getting channel name: {e}")
            return 'Unknown Channel'

    def getChannelPlaylists(self, channel_url):
        """
        Retrieves all playlists from a channel.

        Args:
            channel_url (str): The channel URL.

        Returns:
            list: List of playlist dicts.
        """
        playlists = []
        playlists_url = f"{channel_url}/playlists"

        try:
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
                info = ydl.extract_info(playlists_url, download=False)

                if 'entries' in info:
                    for entry in info['entries']:
                        if entry and entry.get('title') and 'playlist' in entry.get('url', '').lower():
                            playlists.append({
                                'title': entry['title'],
                                'url': entry['url']
                            })
                            time.sleep(self.timeout)

        except Exception as e:
            logging.warning(f"Could not extract playlists: {e}")

        return playlists

    def getStandaloneVideos(self, channel_url, max_videos=200):
        """
        Retrieves standalone videos from a channel.

        Args:
            channel_url (str): The channel URL.
            max_videos (int): Limit for videos (default: 200).

        Returns:
            list: List of video info dicts.
        """
        videos = []
        videos_url = f"{channel_url}/videos"

        try:
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
                info = ydl.extract_info(videos_url, download=False)

                if 'entries' in info:
                    for entry in info['entries'][:max_videos]:
                        if entry:
                            video_id = entry.get('id')
                            video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else entry.get('url', '')
                            
                            if video_url and entry.get('title'):
                                videos.append({
                                    'url': video_url,
                                    'title': sanitizeFilename(entry['title']),
                                    'duration': entry.get('duration', 0)
                                })

        except Exception as e:
            logging.warning(f"Could not extract standalone videos: {e}")

        return videos
