import yt_dlp
import time
import logging
from urllib.parse import urlparse, parse_qs
from .CookieManager import CookieManager

class PlaylistScraper:
    def __init__(self, timeout=2.0, log_callback=None):
        """
        Initialize the PlaylistScraper with timeout and logging capabilities.

        Args:
            timeout (float): Timeout between requests in seconds (default: 2.0)
            log_callback (callable): Function to call with log messages
        """
        self.timeout = timeout
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    def _is_youtube_mix(self, playlist_id):
        """
        Check if the playlist ID corresponds to a YouTube mix/algorithmic playlist.
        
        YouTube mix IDs typically start with specific prefixes:
        - RD: General mix
        - RDAMVM: Music mix
        - RDCLAK: Custom mix
        - RDE: Video mix
        - etc.
        
        Args:
            playlist_id (str): The playlist ID to check
            
        Returns:
            bool: True if it's a YouTube mix, False otherwise
        """
        # common YouTube mix prefixes
        mix_prefixes = ['RD', 'RDE', 'RDCL', 'RDCLAK', 'RDAMVM', 'RDCM', 'RDEO', 'RDFM', 'RDKM', 'RDM', 'RDTM', 'RDV']
        
        return any(playlist_id.startswith(prefix) for prefix in mix_prefixes)

    def _normalize_playlist_url(self, url):
        """
        Normalize playlist URL to the proper format.
        Converts video URLs with playlist parameters to direct playlist URLs.

        Args:
            url (str): YouTube URL (can be playlist or video with playlist parameter)

        Returns:
            str: Normalized playlist URL
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # check if there's a playlist ID in the URL
            if 'list' in query_params:
                playlist_id = query_params['list'][0]
                
                # check if it's a YouTube mix
                if self._is_youtube_mix(playlist_id):
                    video_id = query_params.get('v', [None])[0]  # extract video ID if available
                    if video_id:
                        return f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                    else:
                        # if no video ID is present, try the playlist URL but with different options
                        return f"https://www.youtube.com/playlist?list={playlist_id}"
                
                # convert to proper playlist URL format for regular playlists
                return f"https://www.youtube.com/playlist?list={playlist_id}"
            
            # if it's already a playlist URL, return as-is
            return url
            
        except Exception as e:
            logging.warning(f"Error normalizing URL, using original: {e}")
            return url

    def scrape_playlist(self, url, max_videos=200, progress_callback=None):
        """
        Scrape all video URLs from a YouTube playlist.

        Args:
            url (str): YouTube playlist URL (or video URL with playlist parameter)
            max_videos (int): Maximum number of videos to scrape (default: 200)
            progress_callback (callable): Function to call with progress updates (current, total, percentage)

        Returns:
            list: List of dictionaries containing video info: [{'url': str, 'title': str, 'duration': int}, ...]
        """
        videos = []

        try:
            # normalize the URL to proper playlist format
            normalized_url = self._normalize_playlist_url(url)
            
            # parse the URL to check if it's a YouTube mix
            parsed_url = urlparse(normalized_url)
            query_params = parse_qs(parsed_url.query)
            playlist_id = query_params.get('list', [None])[0] if 'list' in query_params else None
            
            # use different options for YouTube mixes
            is_youtube_mix = playlist_id and self._is_youtube_mix(playlist_id)
            
            cookie_file = self.cookie_manager.get_cookie_file()
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # don't download, just extract info
            }
            if cookie_file:
                ydl_opts['cookies'] = cookie_file
            
            # for YouTube mixes, we might need to bypass some restrictions
            if is_youtube_mix:
                ydl_opts.update({
                    'extract_flat': 'in_playlist',  # extract only the playlist entries
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # extract playlist info
                try:
                    playlist_info = ydl.extract_info(normalized_url, download=False)
                except yt_dlp.DownloadError as e:
                    # if the first attempt fails, try alternative approach for mixes
                    if is_youtube_mix:
                        # try with a watch URL format if the playlist URL fails
                        if 'v' in query_params:
                            video_id = query_params['v'][0]
                            watch_url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                            playlist_info = ydl.extract_info(watch_url, download=False)
                        else:
                            # if no video ID is available, raise the original error
                            raise e
                    else:
                        raise e

                if 'entries' in playlist_info and playlist_info['entries']:
                    total_videos = min(len(playlist_info['entries']), max_videos)
                    
                    for idx, entry in enumerate(playlist_info['entries'][:max_videos], 1):
                        if entry:
                            # create video data from the entry directly
                            # check if the video is available before adding to the list
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                            
                            # add the entry even if it has missing fields, using defaults
                            video_data = {
                                'url': video_url,
                                'title': entry.get('title', 'Unknown Title'),
                                'duration': entry.get('duration', 0)
                            }
                            videos.append(video_data)
                            
                            # report progress
                            if progress_callback:
                                percentage = int((len(videos) / total_videos) * 100)  # update to reflect actual processed videos
                                progress_callback(len(videos), total_videos, percentage)

                            # rate limiting
                            time.sleep(self.timeout)
                else:
                    logging.warning(f"No entries found in playlist. URL used: {normalized_url}")
                    logging.warning("Make sure the URL is a valid YouTube playlist URL.")

        except Exception as e:
            logging.error(f"Error scraping playlist: {e}")
            raise

        return videos

    def get_playlist_title(self, url):
        """
        Get the title of a YouTube playlist.

        Args:
            url (str): YouTube playlist URL (or video URL with playlist parameter)

        Returns:
            str: Playlist title or 'Unknown Playlist' if not found
        """
        try:
            # normalize the URL to proper playlist format
            normalized_url = self._normalize_playlist_url(url)
            
            # parse the URL to check if it's a YouTube mix
            parsed_url = urlparse(normalized_url)
            query_params = parse_qs(parsed_url.query)
            playlist_id = query_params.get('list', [None])[0] if 'list' in query_params else None
            
            # use different options for YouTube mixes
            is_youtube_mix = playlist_id and self._is_youtube_mix(playlist_id)
            
            cookie_file = self.cookie_manager.get_cookie_file()
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            if cookie_file:
                ydl_opts['cookies'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(normalized_url, download=False)
                    return info.get('title', 'Unknown Playlist')
                except yt_dlp.DownloadError as e:
                    # if the first attempt fails for a mix, try alternative approach
                    if is_youtube_mix and 'v' in query_params:
                        # try with a watch URL format if the playlist URL fails
                        video_id = query_params['v'][0]
                        watch_url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
                        info = ydl.extract_info(watch_url, download=False)
                        return info.get('title', 'Unknown Playlist')
                    else:
                        raise e

        except Exception as e:
            logging.error(f"Error getting playlist title: {e}")
            return 'Unknown Playlist'
