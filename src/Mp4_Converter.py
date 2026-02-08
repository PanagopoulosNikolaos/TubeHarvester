import os
import yt_dlp
import logging
from .CookieManager import CookieManager
from .utils import sanitizeFilename

class Mp4Downloader:
    """
    Handles the downloading of YouTube videos as MP4 files.

    This class provides methods to select resolutions, set download paths,
    and manage the download process using yt-dlp.
    """

    def __init__(self, progress_callback=None, log_callback=None):
        """
        Initializes the Mp4Downloader with callback functions.

        Args:
            progress_callback (callable, optional): Called with the percentage of download progress.
            log_callback (callable, optional): Called with log messages.
        """
        self.url = None
        self.path = self.getDefaultDownloadPath()
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.video_title = None
        self.resolution = "1080"  # Default target
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    @staticmethod
    def getDefaultDownloadPath():
        """
        Gets the default path where downloaded files are saved.

        Returns:
            str: The user's Downloads directory.
        """
        return os.path.join(os.path.expanduser('~'), 'Downloads')

    def setUrl(self, url):
        """
        Sets the URL of the YouTube video to download.

        Args:
            url (str): The URL of the YouTube video.
        """
        self.url = url

    def setPath(self, path):
        """
        Sets the path where the downloaded MP4 file will be saved.

        Args:
            path (str, optional): The destination directory.
        """
        self.path = path or self.getDefaultDownloadPath()
        os.makedirs(self.path, exist_ok=True)

    def downloadVideo(self, custom_title=None):
        """
        Downloads the video from YouTube in MP4 format.

        Args:
            custom_title (str, optional): Custom title for the file. Defaults to video title.

        Raises:
            ValueError: If the URL is not set.
        """
        if not self.url:
            raise ValueError("URL is not set.")

        ydl_opts = {
            'format': f'bestvideo[height<={self.resolution}]+bestaudio/best[height<={self.resolution}]/best',
            'outtmpl': os.path.join(self.path, f"{custom_title or '%(title)s'}.%(ext)s"),
            'progress_hooks': [self.progressHook],
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'extractor_args': {
                'youtube': {
                    'hl': 'en-US',
                    'gl': 'US',
                    'skip': ['translated_subs'],
                }
            },
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }, {
                'key': 'FFmpegMerger',
            }],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Client-Version': '2.20240523.01.00',
                'X-Youtube-Client-Name': '1',
                'Origin': 'https://www.youtube.com',
                'Referer': 'https://www.youtube.com/',
            },
            'quiet': False,
            'no_warnings': False,
            'age_limit': 99,
            'check_formats': 'selected',
            'youtube_include_dash_manifest': True,
            'youtube_include_hls_manifest': True,
            'javascript_executor': '/home/ice/.deno/bin/deno',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                self.video_title = sanitizeFilename(info.get('title', 'Unknown'))
                
            if self.log_callback:
                self.log_callback(f"Download complete: {self.video_title}")

        except Exception as e:
            self.handleError(e)

    def fetchVideoInfo(self):
        """
        Fetches information about the video without downloading.

        Returns:
            dict: The information extracted by yt-dlp.
        """
        if not self.url:
            raise ValueError("URL is not set")

        opts = {
            'noplaylist': True, 
            'cookiefile': self.cookie_manager.getCookieFile(),
            'javascript_executor': '/home/ice/.deno/bin/deno',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'hl': 'en-US',
                    'gl': 'US',
                }
            },
            'youtube_include_dash_manifest': True,
            'youtube_include_hls_manifest': True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(self.url, download=False)

    def progressHook(self, d):
        """
        Updates the progress via the provided callback.

        Args:
            d (dict): Dictionary with download progress information.
        """
        if d['status'] == 'downloading' and self.progress_callback:
            p = d.get('_percent_str', '0%').replace('%','')
            try:
                self.progress_callback(int(float(p)))
            except ValueError:
                pass

    def handleError(self, e):
        """
        Handles errors that occur during the download process.

        Args:
            e (Exception): The exception to handle.
        """
        err_msg = str(e)
        if any(x in err_msg for x in ["Private", "unavailable", "Sign in"]):
            msg = "Video restricted or requires authentication."
        else:
            msg = f"Error: {err_msg}"
        
        logging.error(msg)
        if self.log_callback:
            self.log_callback(msg)
