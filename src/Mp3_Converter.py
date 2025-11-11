import os
import logging
import yt_dlp
from tkinter import messagebox
from .CookieManager import CookieManager

logging.basicConfig(level=logging.INFO)

class MP3Downloader:
    def __init__(self, url=None, save_path=None, progress_callback=None, log_callback=None):
        """
        Initialize the MP3Downloader with URL, save path, and callback functions.

        Args:
            url (str): The URL of the YouTube video to download. If not provided, must be set using set_url() before downloading.
            save_path (str): The path where the downloaded MP3 file will be saved. If not provided, defaults to the user's home directory.
            progress_callback (function): A function that will be called with the percentage of download progress as an argument. If not provided, no progress messages will be displayed.
            log_callback (function): A function that will be called with log messages. If not provided, no log messages will be displayed.
        """
        self.url = url
        self.save_path = save_path if save_path else self.get_default_download_path()
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    def set_url(self, url):
        """
        Set the URL of the YouTube video to download.

        Args:
            url (str): The URL of the YouTube video to download.
        """
        self.url = url

    def set_path(self, save_path):
        """
        Set the path where the downloaded MP3 file will be saved.

        Args:
            save_path (str): The path where the downloaded MP3 file will be saved. If not provided, defaults to the user's home directory.
        """
        self.save_path = save_path if save_path else self.get_default_download_path()

    @staticmethod
    def get_default_download_path():
        """
        Get the default path where downloaded files are saved.

        Returns:
            str: The default path where downloaded files are saved. This is the user's home directory.
        """
        home_directory = os.path.expanduser('~')
        return os.path.join(home_directory, 'Downloads')

    def download_as_mp3(self, custom_title=None):

        """
        Download the audio from a YouTube video as an MP3 file and save it to the path set by set_path() or the default path.

        Args:
            custom_title (str): Custom title for the downloaded file. If None, uses the video's original title.

        Returns:
            str: The path where the downloaded MP3 file was saved.

        Raises:
            Exception: If the download and conversion fails, an exception is raised with a message describing the error.
        """
        try:
            cookie_file = self.cookie_manager.get_cookie_file()
            ydl_opts = {
                'noplaylist': True,
            }
            if cookie_file:
                ydl_opts['cookies'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                title = custom_title or info.get('title', 'Unknown Title')

            if self.log_callback:
                self.log_callback(f"Download started: \"{title}\" - Format: MP3. Saved at: \"{self.save_path}\"")

            options = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.save_path, f'{title}.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'keepvideo': False, # remove original video file after audio extraction
                'quiet': True, # suppress yt-dlp output
                'no_warnings': True, # suppress yt-dlp warnings
                'noplaylist': True,
            }
            if cookie_file:
                options['cookies'] = cookie_file

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])

            if self.log_callback:
                self.log_callback(f"Download complete at {self.save_path}")

            return self.save_path
        except yt_dlp.DownloadError as e:
            if "Private video" in str(e) or "This video is unavailable" in str(e) or "Copyright" in str(e) or "Sign in to confirm your age" in str(e):
                if self.log_callback:
                    self.log_callback(f"Cannot download private or restricted video: {title or 'Unknown Title'}")
                logging.info(f"Private or restricted video skipped: {self.url}")
            else:
                logging.error(f"An error occurred: {e}")
                if self.log_callback:
                    self.log_callback(f"An error occurred: {e}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            if self.log_callback:
                self.log_callback(f"An error occurred: {e}")
            raise

    def progress_hook(self, d):
        """
        Update the progress bar in the GUI with the given percentage value.

        Args:
            d (dict): A dictionary with information about the download progress.
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
