import yt_dlp
import time
import logging
from urllib.parse import urlparse, parse_qs

class PlaylistScraper:
    def __init__(self, timeout=2.0):
        """
        Initialize the PlaylistScraper.

        Parameters
        ----------
        timeout : float
            Timeout between requests in seconds (default: 2.0)
        """
        self.timeout = timeout

    def scrape_playlist(self, url, max_videos=200):
        """
        Scrape all video URLs from a YouTube playlist.

        Parameters
        ----------
        url : str
            YouTube playlist URL
        max_videos : int
            Maximum number of videos to scrape (default: 200)

        Returns
        -------
        list
            List of dictionaries containing video info: [{'url': str, 'title': str, 'duration': int}, ...]
        """
        videos = []

        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Don't download, just extract info
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract playlist info
                playlist_info = ydl.extract_info(url, download=False)

                if 'entries' in playlist_info and playlist_info['entries']:
                    for entry in playlist_info['entries'][:max_videos]:
                        if entry:
                            video_info = {
                                'url': f"https://www.youtube.com/watch?v={entry['id']}",
                                'title': entry.get('title', 'Unknown Title'),
                                'duration': entry.get('duration', 0)
                            }
                            videos.append(video_info)

                            # Rate limiting
                            time.sleep(self.timeout)

        except Exception as e:
            logging.error(f"Error scraping playlist: {e}")
            raise

        return videos

    def get_playlist_title(self, url):
        """
        Get the title of a YouTube playlist.

        Parameters
        ----------
        url : str
            YouTube playlist URL

        Returns
        -------
        str
            Playlist title or 'Unknown Playlist' if not found
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('title', 'Unknown Playlist')

        except Exception as e:
            logging.error(f"Error getting playlist title: {e}")
            return 'Unknown Playlist'
