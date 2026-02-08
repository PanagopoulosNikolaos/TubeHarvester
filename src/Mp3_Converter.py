import os
import logging
import yt_dlp
from .CookieManager import CookieManager
from .utils import sanitizeFilename

logging.basicConfig(level=logging.INFO)

class Mp3Downloader:
    """
    Handles the downloading of YouTube videos and converting them to MP3 files.

    This class provides methods to set the video URL, save path, and download the
    audio content using yt-dlp. It also supports progress and log callbacks.
    """

    def __init__(self, url=None, save_path=None, progress_callback=None, log_callback=None):
        """
        Initializes the Mp3Downloader with URL, save path, and callback functions.

        Args:
            url (str, optional): The URL of the YouTube video to download.
            save_path (str, optional): The path where the downloaded MP3 file will be saved.
            progress_callback (callable, optional): Called with the percentage of download progress.
            log_callback (callable, optional): Called with log messages.
        """
        self.url = url
        self.save_path = save_path if save_path else self.getDefaultDownloadPath()
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    def setUrl(self, url):
        """
        Sets the URL of the YouTube video to download.

        Args:
            url (str): The URL of the YouTube video.
        """
        self.url = url

    def setPath(self, save_path):
        """
        Sets the path where the downloaded MP3 file will be saved.

        Args:
            save_path (str, optional): The destination directory. Defaults to the Downloads folder.
        """
        self.save_path = save_path if save_path else self.getDefaultDownloadPath()

    @staticmethod
    def getDefaultDownloadPath():
        """
        Gets the default path where downloaded files are saved.

        Returns:
            str: The default path (user's Downloads directory).
        """
        home_directory = os.path.expanduser('~')
        return os.path.join(home_directory, 'Downloads')

    def downloadAsMp3(self, custom_title=None):
        """
        Downloads the audio from a YouTube video as an MP3 file.

        Args:
            custom_title (str, optional): Custom title for the file. Defaults to video title.

        Returns:
            str: The path where the MP3 file was saved.

        Raises:
            Exception: If the download or conversion fails.
        """
        try:
            cookie_file = self.cookie_manager.getCookieFile()
            
            # Common options for modern YouTube handling
            common_opts = {
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
                'extractor_args': {
                    'youtube': {
                        'hl': 'en-US',
                        'gl': 'US',
                        'skip': ['translated_subs'],
                    }
                },
                'cookiefile': cookie_file,
                'noplaylist': True,
                'quiet': False,
                'no_warnings': False,
                'age_limit': 99,
                'youtube_include_dash_manifest': True,
                'youtube_include_hls_manifest': True,
                'compat_opts': ['no-live-chat'],
            }


            # First extraction to get title
            with yt_dlp.YoutubeDL(common_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                title = sanitizeFilename(custom_title or info.get('title', 'Unknown Title'))

            if self.log_callback:
                self.log_callback(f"Download started: \"{title}\" - Format: MP3. Saved at: \"{self.save_path}\"")

            options = common_opts.copy()
            options.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.save_path, f'{title}.%(ext)s'),
                'progress_hooks': [self.progressHook],
                'keepvideo': False,
            })

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])

            if self.log_callback:
                self.log_callback(f"Download complete at {self.save_path}")

            return self.save_path
            
        except yt_dlp.DownloadError as e:
            err_msg = str(e)
            if any(x in err_msg for x in ["Private video", "unavailable", "Copyright", "Sign in"]):
                if self.log_callback:
                    self.log_callback(f"Video restricted or requires authentication: {title or 'Unknown Title'}")
                logging.info(f"Restricted video skipped: {self.url}")
            else:
                logging.error(f"yt-dlp error: {e}")
                if self.log_callback:
                    self.log_callback(f"yt-dlp error: {e}")
            raise
            
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            if self.log_callback:
                self.log_callback(f"Unexpected error: {e}")
            raise

    def progressHook(self, d):
        """
        Updates the progress via the provided callback.

        Args:
            d (dict): Dictionary with download progress information.
        """
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                percentage = (downloaded_bytes / total_bytes) * 100
                if self.progress_callback:
                    self.progress_callback(int(percentage))
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(100)
