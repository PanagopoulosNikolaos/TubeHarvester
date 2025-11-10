import yt_dlp
import time
import logging
import re
from urllib.parse import urlparse, parse_qs
from .PlaylistScraper import PlaylistScraper

class ChannelScraper:
    def __init__(self, timeout=2.0):
        """
        Initialize the ChannelScraper.

        Parameters
        ----------
        timeout : float
            Timeout between requests in seconds (default: 2.0)
        """
        self.timeout = timeout

    def scrape_channel(self, url, max_videos_per_playlist=200, progress_callback=None):
        """
        Scrape all playlists and standalone videos from a YouTube channel.

        Parameters
        ----------
        url : str
            YouTube channel URL
        max_videos_per_playlist : int
            Maximum number of videos to scrape per playlist (default: 200)
        progress_callback : callable, optional
            Function to call with progress updates (current, total, percentage)

        Returns
        -------
        dict
            Dictionary with channel info and content:
            {
                'channel_name': str,
                'playlists': [{'title': str, 'url': str, 'videos': [video_info...]}, ...],
                'standalone_videos': [video_info...]
            }
        """
        channel_info = {
            'channel_name': 'Unknown Channel',
            'playlists': [],
            'standalone_videos': []
        }

        try:
            # Convert various channel URL formats to a standard format
            channel_url = self._normalize_channel_url(url)

            # Get channel name
            channel_info['channel_name'] = self._get_channel_name(channel_url)

            # Report initial progress
            if progress_callback:
                progress_callback(0, 100, 0)

            # Get all playlists from the channel
            playlists = self._get_channel_playlists(channel_url)

            # Calculate progress steps
            total_playlists = len(playlists) + 1  # +1 for standalone videos
            completed = 0

            # Scrape videos from each playlist
            for playlist in playlists:
                try:
                    scraper = PlaylistScraper(timeout=self.timeout)
                    
                    # Create a nested progress callback for playlist scraping
                    def nested_progress(current, total, percentage):
                        if progress_callback:
                            # Calculate overall progress including this playlist's progress
                            playlist_weight = (1 / total_playlists)
                            overall_percentage = int(((completed + (percentage / 100)) / total_playlists) * 100)
                            progress_callback(completed + 1, total_playlists, overall_percentage)
                    
                    videos = scraper.scrape_playlist(playlist['url'], max_videos_per_playlist, nested_progress)

                    playlist_info = {
                        'title': playlist['title'],
                        'url': playlist['url'],
                        'videos': videos
                    }
                    channel_info['playlists'].append(playlist_info)

                    completed += 1
                    if progress_callback:
                        percentage = int((completed / total_playlists) * 100)
                        progress_callback(completed, total_playlists, percentage)

                    # Rate limiting between playlists
                    time.sleep(self.timeout)

                except Exception as e:
                    logging.warning(f"Failed to scrape playlist {playlist['title']}: {e}")
                    completed += 1
                    continue

            # Get standalone videos (videos not in playlists)
            channel_info['standalone_videos'] = self._get_standalone_videos(channel_url, max_videos_per_playlist)
            
            completed += 1
            if progress_callback:
                progress_callback(completed, total_playlists, 100)

        except Exception as e:
            logging.error(f"Error scraping channel: {e}")
            raise

        return channel_info

    def _normalize_channel_url(self, url):
        """
        Normalize various YouTube channel URL formats to a standard format.

        Parameters
        ----------
        url : str
            Input channel URL

        Returns
        -------
        str
            Normalized channel URL
        """
        # Handle different YouTube URL formats
        if '/channel/' in url:
            # Already in channel format
            return url
        elif '/user/' in url:
            # Convert user URL to channel URL
            username = url.split('/user/')[-1].split('/')[0]
            return f"https://www.youtube.com/user/{username}"
        elif '/c/' in url or '/@' in url:
            # Handle custom channel URLs
            return url
        else:
            # Assume it's already a proper channel URL
            return url

    def _get_channel_name(self, url):
        """
        Extract channel name from channel URL.

        Parameters
        ----------
        url : str
            Channel URL

        Returns
        -------
        str
            Channel name
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('channel', 'Unknown Channel')

        except Exception as e:
            logging.error(f"Error getting channel name: {e}")
            return 'Unknown Channel'

    def _get_channel_playlists(self, channel_url):
        """
        Get all playlists from a YouTube channel.

        Parameters
        ----------
        channel_url : str
            Channel URL

        Returns
        -------
        list
            List of playlist dictionaries: [{'title': str, 'url': str}, ...]
        """
        playlists = []

        try:
            # Try to get playlists from channel's playlists tab
            playlists_url = f"{channel_url}/playlists"

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlists_url, download=False)

                if 'entries' in info:
                    for entry in info['entries']:
                        if entry and entry.get('title') and 'playlist' in entry.get('url', '').lower():
                            playlist_info = {
                                'title': entry['title'],
                                'url': entry['url']
                            }
                            playlists.append(playlist_info)

                            # Rate limiting
                            time.sleep(self.timeout)

        except Exception as e:
            logging.warning(f"Could not extract playlists from channel: {e}")

        return playlists

    def _get_standalone_videos(self, channel_url, max_videos=200):
        """
        Get standalone videos from a channel (not in playlists).

        Parameters
        ----------
        channel_url : str
            Channel URL
        max_videos : int
            Maximum number of videos to get

        Returns
        -------
        list
            List of video info dictionaries
        """
        videos = []

        try:
            # Get videos from channel's videos tab
            videos_url = f"{channel_url}/videos"

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(videos_url, download=False)

                if 'entries' in info:
                    for entry in info['entries'][:max_videos]:
                        if entry:
                            # Create video URL from entry ID if available
                            video_id = entry.get('id')
                            if video_id:
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                            else:
                                # If no ID, try to use the URL directly if available
                                video_url = entry.get('url', '')
                            
                            # Add video to the list if it has a valid URL and title
                            if video_url and entry.get('title'):
                                video_data = {
                                    'url': video_url,
                                    'title': entry.get('title', 'Unknown Title'),
                                    'duration': entry.get('duration', 0)
                                }
                                videos.append(video_data)
                            else:
                                # If the entry doesn't have a proper format, skip it
                                continue

        except Exception as e:
            logging.warning(f"Could not extract standalone videos from channel: {e}")

        return videos
