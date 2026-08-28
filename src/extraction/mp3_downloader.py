"""
MP3 audio extraction and downloader module leveraging yt-dlp and FFmpeg.

Extracts high-quality audio streams and converts them to MP3 files with
metadata sanitization and progress tracking.
"""

import logging
import os
from typing import Any, Callable, Dict, Optional
import yt_dlp

from .cookie_manager import CookieManager
from .utils import sanitizeFilename

logging.basicConfig(level=logging.INFO)


class Mp3Downloader:
    """
    Handles the downloading of YouTube audio converted to MP3 files.

    Provides methods to set audio sources, output directories, and run extraction
    with FFmpeg audio post-processing.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        save_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initializes the Mp3Downloader with URL, destination path, and callbacks.

        Args:
            url (Optional[str], optional): The URL of the YouTube video to extract audio from.
            save_path (Optional[str], optional): The destination directory path.
            progress_callback (Optional[Callable[[int], None]], optional): Called with progress percentage.
            log_callback (Optional[Callable[[str], None]], optional): Called with status messages.
        """
        self.url = url
        self.save_path = save_path if save_path else self.getDefaultDownloadPath()
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    def setUrl(self, url: str) -> None:
        """
        Sets the URL of the YouTube video to download and convert.

        Args:
            url (str): The URL of the target video.
        """
        self.url = url

    def setPath(self, save_path: Optional[str]) -> None:
        """
        Sets the destination directory path for the converted MP3 file.

        Args:
            save_path (Optional[str]): The destination directory path.
        """
        self.save_path = save_path if save_path else self.getDefaultDownloadPath()
        os.makedirs(self.save_path, exist_ok=True)

    @staticmethod
    def getDefaultDownloadPath() -> str:
        """
        Retrieves the default system path for downloaded audio files.

        Returns:
            str: The user's system Downloads directory path.
        """
        return os.path.join(os.path.expanduser('~'), 'Downloads')

    def downloadAsMp3(self, custom_title: Optional[str] = None) -> str:
        """
        Downloads audio from the specified YouTube URL and converts it to MP3.

        Args:
            custom_title (Optional[str]): Optional custom title for the output audio file.

        Returns:
            str: The path to the directory where the MP3 file was saved.

        Raises:
            yt_dlp.DownloadError: If download fails due to restrictions or network errors.
            Exception: If an unexpected error occurs during conversion.
        """
        title = "Unknown Title"
        try:
            cookie_file = self.cookie_manager.getCookieFile()

            common_opts: Dict[str, Any] = {
                'extractor_args': {
                    'youtube': {
                        'skip': ['translated_subs'],
                    }
                },
                'noplaylist': True,
                'quiet': False,
                'no_warnings': False,
                'compat_opts': ['no-live-chat'],
            }
            if cookie_file:
                common_opts['cookiefile'] = cookie_file

            # Extracts preliminary video metadata to determine clean sanitized title.
            with yt_dlp.YoutubeDL(common_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                title = sanitizeFilename(custom_title or info.get('title', 'Unknown Title'))

            if self.log_callback:
                self.log_callback(f'Download started: "{title}" - Format: MP3. Saved at: "{self.save_path}"')

            # Configures FFmpeg audio postprocessor for MP3 format encoding.
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

        except yt_dlp.DownloadError as exc:
            err_msg = str(exc)
            if any(keyword in err_msg for keyword in ["Private video", "unavailable", "Copyright", "Sign in"]):
                if self.log_callback:
                    self.log_callback(f"Video restricted or requires authentication: {title}")
                logging.info(f"Restricted video skipped: {self.url}")
            else:
                logging.error(f"yt-dlp error: {exc}")
                if self.log_callback:
                    self.log_callback(f"yt-dlp error: {exc}")
            raise

        except Exception as exc:
            logging.error(f"Unexpected error: {exc}")
            if self.log_callback:
                self.log_callback(f"Unexpected error: {exc}")
            raise

    def progressHook(self, d: Dict[str, Any]) -> None:
        """
        Updates download progress percentage from yt-dlp hook dictionary.

        Args:
            d (Dict[str, Any]): Dictionary containing stream progress stats.
        """
        if d.get('status') == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                percentage = (downloaded_bytes / total_bytes) * 100
                if self.progress_callback:
                    self.progress_callback(int(percentage))
        elif d.get('status') == 'finished':
            if self.progress_callback:
                self.progress_callback(100)
