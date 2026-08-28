"""
MP4 video downloader module leveraging yt-dlp.

Manages video quality resolution selection, destination folders, and
download execution with progress hooks and error handling.
"""

import logging
import os
from typing import Any, Callable, Dict, Optional
import yt_dlp

from .cookie_manager import CookieManager
from .utils import sanitizeFilename


class Mp4Downloader:
    """
    Handles the downloading of YouTube videos as MP4 files.

    Provides methods to set download target parameters, retrieve available video
    metadata, and run downloads with callback-driven updates.
    """

    def __init__(
        self,
        progress_callback: Optional[Callable[[int], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initializes the Mp4Downloader with callback functions.

        Args:
            progress_callback (Callable[[int], None], optional): Called with the percentage of progress.
            log_callback (Callable[[str], None], optional): Called with log status messages.
        """
        self.url: Optional[str] = None
        self.path: str = self.getDefaultDownloadPath()
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.video_title: Optional[str] = None
        self.resolution: Any = "1080"
        self.cookie_manager = CookieManager(log_callback=self.log_callback)

    @staticmethod
    def getDefaultDownloadPath() -> str:
        """
        Retrieves the default path where downloaded files are saved.

        Returns:
            str: The user's system Downloads directory path.
        """
        return os.path.join(os.path.expanduser('~'), 'Downloads')

    def setUrl(self, url: str) -> None:
        """
        Sets the URL of the YouTube video to download.

        Args:
            url (str): The URL of the YouTube video.
        """
        self.url = url

    def setPath(self, path: Optional[str]) -> None:
        """
        Sets the destination directory path for the downloaded MP4 file.

        Args:
            path (Optional[str]): The destination directory path.
        """
        self.path = path or self.getDefaultDownloadPath()
        os.makedirs(self.path, exist_ok=True)

    def downloadVideo(self, custom_title: Optional[str] = None) -> None:
        """
        Downloads the video from YouTube in MP4 container format.

        Args:
            custom_title (Optional[str]): Optional custom title for the destination file.

        Raises:
            ValueError: If the video URL has not been specified.
        """
        if not self.url:
            raise ValueError("URL is not set.")

        cookie_file = self.cookie_manager.getCookieFile()
        ydl_opts: Dict[str, Any] = {
            'format': f'bestvideo[height<={self.resolution}]+bestaudio/best[height<={self.resolution}]/best',
            'outtmpl': os.path.join(self.path, f"{custom_title or '%(title)s'}.%(ext)s"),
            'progress_hooks': [self.progressHook],
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'extractor_args': {
                'youtube': {
                    'skip': ['translated_subs'],
                }
            },
            'quiet': False,
            'no_warnings': False,
        }
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file

        try:
            # Executes the download operation via YoutubeDL context manager.
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                self.video_title = sanitizeFilename(info.get('title', 'Unknown'))

            if self.log_callback:
                self.log_callback(f"Download complete: {self.video_title}")

        except Exception as exc:
            self.handleError(exc)

    def fetchVideoInfo(self) -> Dict[str, Any]:
        """
        Fetches metadata for the configured video URL without downloading.

        Returns:
            Dict[str, Any]: The video metadata dictionary extracted by yt-dlp.

        Raises:
            ValueError: If the video URL has not been specified.
        """
        if not self.url:
            raise ValueError("URL is not set")

        opts: Dict[str, Any] = {
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'skip': ['translated_subs'],
                }
            },
        }
        cookie_file = self.cookie_manager.getCookieFile()
        if cookie_file:
            opts['cookiefile'] = cookie_file

        # Extracts metadata dictionary with download disabled.
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(self.url, download=False)

    def progressHook(self, d: Dict[str, Any]) -> None:
        """
        Receives download progress dictionaries and forwards percentages to callback.

        Args:
            d (Dict[str, Any]): Dictionary containing download progress state.
        """
        if d.get('status') == 'downloading' and self.progress_callback:
            raw_percent = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                self.progress_callback(int(float(raw_percent)))
            except ValueError:
                # Ignores formatting anomalies in yt-dlp percentage strings.
                pass

    def handleError(self, exc: Exception) -> None:
        """
        Processes errors encountered during the download pipeline.

        Args:
            exc (Exception): The caught exception instance.
        """
        err_msg = str(exc)
        if any(keyword in err_msg for keyword in ["Private", "unavailable", "Sign in"]):
            msg = "Video restricted or requires authentication."
        else:
            msg = f"Error: {err_msg}"

        logging.error(msg)
        if self.log_callback:
            self.log_callback(msg)
