import os
import yt_dlp
import logging
from .CookieManager import CookieManager

class YouTubeDownloader:
    def __init__(self, progress_callback=None, log_callback=None):
        """
        Initialize the YouTubeDownloader with progress and log callbacks.

        Args:
            progress_callback (callable): A function that takes a single argument, an integer representing the download progress percentage,
                                         that will be called every time the download progress changes. If None, no callback is used.
            log_callback (callable): A function that will be called with log messages. If None, no log messages will be displayed.
        """
        self.url = None
        self.path = self.get_default_download_path()
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.video_title = None
        self.resolution = None
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    @staticmethod
    def get_default_download_path():
        """
        Get the default path where downloaded videos will be saved.

        Returns:
            str: The default path where downloaded videos will be saved. The default path is set to the user's home directory, in a folder named 'Downloads'.
        """
        home_directory = os.path.expanduser('~')
        return os.path.join(home_directory, 'Downloads')

    def set_url(self, url):
        """
        Set the URL of the YouTube video to download.

        Args:
            url (str): The URL of the YouTube video to download.
        """
        
        self.url = url

    def set_path(self, path):
        """
        Set the path where the downloaded video will be saved.

        Args:
            path (str): The path where the downloaded video will be saved. If None, the default path (user's home directory, in a
                       folder named 'Downloads') is used.
        """
        self.path = path if path else self.get_default_download_path()
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def download_video(self, custom_title=None):
        if not self.url:
            raise ValueError("URL is not set. Use set_url() method to set the URL before downloading.")

        try:
            info = self._get_video_info()
            self.video_title = custom_title or info.get('title', 'Unknown Title')
            self.resolution = info.get('height', 'Unknown Resolution')

            if self.log_callback:
                self.log_callback(f"Download started: \"{self.video_title}\" - Resolution: {self.resolution}p. Saved at: \"{self.path}\"")

            # download audio stream separately for better quality control
            self._download_stream('bestaudio', 'audio_temp', 0, 50)

            # download video stream separately for better quality control
            self._download_stream(f'bestvideo[height<={self.resolution}]', 'video_temp', 50, 100)

            self._merge_files()

            if self.log_callback:
                self.log_callback(f"Download complete at {self.path}")

        except yt_dlp.DownloadError as e:
            if "Private video" in str(e) or "This video is unavailable" in str(e) or "Copyright" in str(e) or "Sign in to confirm your age" in str(e):
                if self.log_callback:
                    self.log_callback(f"Cannot download private or restricted video: {self.video_title or 'Unknown Title'}")
                logging.info(f"Private or restricted video skipped: {self.url}")
            else:
                logging.error(f"An error occurred: {e}")
                if self.log_callback:
                    self.log_callback(f"An error occurred: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            if self.log_callback:
                self.log_callback(f"An error occurred: {e}")

    def fetch_video_info(self):
        """
        Fetch video information without downloading.

        This method is intended to be called from the GUI to populate resolution choices.
        """
        if not self.url:
            raise ValueError("URL is not set.")

        cookie_file = self.cookie_manager.get_cookie_file()
        ydl_opts = {
            'noplaylist': True,
        }

        if cookie_file:
            ydl_opts['cookies'] = cookie_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(self.url, download=False)

    def _get_video_info(self):
        return self.fetch_video_info()

    def _download_stream(self, format_selection, temp_filename, start_progress, end_progress):
        cookie_file = self.cookie_manager.get_cookie_file()
        options = {
            'format': format_selection,
            'outtmpl': os.path.join(self.path, f'{temp_filename}.%(ext)s'),
            'progress_hooks': [lambda d: self._progress_hook(d, start_progress, end_progress)],
            'noplaylist': True,
        }

        if cookie_file:
            options['cookies'] = cookie_file

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([self.url])

    def _merge_files(self):
        if self.log_callback:
            self.log_callback("Merging audio and video...")

        # find temporary files for merging
        temp_files = [f for f in os.listdir(self.path) if f.startswith('video_temp') or f.startswith('audio_temp')]
        video_file = next((f for f in temp_files if f.startswith('video_temp')), None)
        audio_file = next((f for f in temp_files if f.startswith('audio_temp')), None)

        if not video_file or not audio_file:
            if self.log_callback:
                self.log_callback("Error: Could not find temporary audio/video files to merge.")
            return

        video_path = os.path.join(self.path, video_file)
        audio_path = os.path.join(self.path, audio_file)
        output_path = os.path.join(self.path, f"{self.video_title}.mp4")

        # use ffmpeg to merge audio and video streams
        command = f"ffmpeg -i \"{video_path}\" -i \"{audio_path}\" -c:v copy -c:a aac \"{output_path}\""

        try:
            os.system(command)
            if self.log_callback:
                self.log_callback("Files merged successfully.")
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"Error during merge: {e}")
        finally:
            # clean up temporary files after merging
            os.remove(video_path)
            os.remove(audio_path)

    def _progress_hook(self, d, start_progress, end_progress):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)

            if total_bytes > 0:
                percentage = (downloaded_bytes / total_bytes) * 10
                scaled_progress = start_progress + (percentage / 100) * (end_progress - start_progress)

                if self.progress_callback:
                    self.progress_callback(int(scaled_progress))
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(end_progress)
