"""
Single download view module for TubeHarvester.

Manages standalone video/audio download workflows including resolution extraction,
background thread processing, progress tracking, and notifications.
"""

import asyncio
from typing import List, Optional
from nicegui import ui

from ..components.format_picker import FormatPicker
from ..components.log_console import LogConsole
from ..components.path_selector import PathSelector
from ..components.progress import ProgressBar
from ..components.url_input import UrlInput
from ...extraction.mp3_downloader import Mp3Downloader
from ...extraction.mp4_downloader import Mp4Downloader


class SingleView:
    """
    Coordinates UI and background processing for single video and audio downloads.
    """

    def __init__(self) -> None:
        """
        Initializes the SingleView component state.
        """
        self.is_downloading = False
        self.last_fetched_url = ""
        self.active_downloader = None
        self.download_task: Optional[asyncio.Task] = None

        self.url_input = UrlInput(
            placeholder="https://www.youtube.com/watch?v=...",
            label="YouTube Video URL",
            on_change_debounced=self.handleUrlDebounced,
        )
        self.path_selector = PathSelector()
        self.format_picker = FormatPicker()
        self.progress_bar = ProgressBar()
        self.log_console = LogConsole()

        self.action_button: Optional[ui.button] = None
        self.card_container: Optional[ui.card] = None

    def render(self) -> None:
        """
        Builds the single download interface elements.
        """
        with ui.card().classes('glass-card w-full') as card:
            self.card_container = card

            # Form fields
            with ui.column().classes('w-full gap-4'):
                self.url_input.render()
                self.format_picker.render()
                self.path_selector.render()

                # Action button container
                with ui.row().classes('w-full justify-end mt-2'):
                    self.action_button = ui.button(
                        'Download Video',
                        icon='download',
                        on_click=self.handleActionClicked,
                    ).classes('btn-primary w-full sm:w-auto')

                # Progress indicator
                self.progress_bar.render()

                # Real-time activity log
                self.log_console.render()

    def handleUrlDebounced(self, url: str) -> None:
        """
        Triggers background resolution discovery when a valid URL is typed.

        Args:
            url (str): The current URL text.
        """
        cleaned_url = url.strip()
        if not cleaned_url or cleaned_url == self.last_fetched_url:
            return

        if "youtube.com" in cleaned_url.lower() or "youtu.be" in cleaned_url.lower():
            self.last_fetched_url = cleaned_url
            asyncio.create_task(self.fetchResolutionsAsync(cleaned_url))

    async def fetchResolutionsAsync(self, url: str) -> None:
        """
        Queries video formats in a background thread and updates available resolutions.

        Args:
            url (str): The YouTube video URL to query.
        """
        self.format_picker.setLoadingResolutions(True)
        self.log_console.log(f"Fetching available formats for: {url}")

        try:
            downloader = Mp4Downloader()
            downloader.setUrl(url)

            # Runs yt-dlp metadata extraction asynchronously in a worker thread.
            info = await asyncio.to_thread(downloader.fetchVideoInfo)
            formats = info.get('formats', []) if info else []

            resolutions_set = set()
            for fmt in formats:
                height = fmt.get('height')
                # Collects distinct video resolutions.
                if height and isinstance(height, int) and height >= 144:
                    resolutions_set.add(f"{height}p")

            # Sorts resolutions descending by numerical height.
            sorted_res = sorted(
                list(resolutions_set),
                key=lambda r: int(r.replace('p', '')),
                reverse=True,
            )

            if sorted_res:
                self.format_picker.setResolutions(sorted_res)
                self.log_console.log(f"Available resolutions: {', '.join(sorted_res)}", level="info")
            else:
                self.log_console.log("No specific resolutions detected, using default profiles.")

        except Exception as exc:
            self.log_console.log(f"Format fetch notice: {str(exc)}", level="error")

        finally:
            self.format_picker.setLoadingResolutions(False)

    def handleActionClicked(self) -> None:
        """
        Handles primary button clicks to start or cancel single media downloads.
        """
        if self.is_downloading:
            self.cancelDownload()
        else:
            self.startDownload()

    def startDownload(self) -> None:
        """
        Validates inputs and launches single download execution in a background thread.
        """
        if not self.url_input.validate(is_batch=False):
            return

        if not self.path_selector.validate():
            return

        url = self.url_input.getValue()
        path = self.path_selector.getValue()
        media_format = self.format_picker.getFormat()
        quality = self.format_picker.getQuality()

        self.setDownloadingState(True)
        self.progress_bar.reset()
        self.progress_bar.setProgress(0, f"Starting {media_format} download...")
        self.log_console.log(f"Initiating {media_format} download for: {url}")

        self.download_task = asyncio.create_task(
            self.runDownloadAsync(url, path, media_format, quality)
        )

    async def runDownloadAsync(
        self,
        url: str,
        path: str,
        media_format: str,
        quality: str,
    ) -> None:
        """
        Executes download and conversion logic in a background worker thread.

        Args:
            url (str): The video source URL.
            path (str): The target destination folder.
            media_format (str): Selected format ('MP4' or 'MP3').
            quality (str): Target quality setting.
        """
        def progressCallback(pct: int) -> None:
            # Pushes progress updates safely to NiceGUI frontend.
            self.progress_bar.setProgress(pct, f"Downloading {media_format} ({pct}%)")

        def logCallback(msg: str) -> None:
            self.log_console.log(msg)

        try:
            if media_format == "MP4":
                downloader = Mp4Downloader(
                    progress_callback=progressCallback,
                    log_callback=logCallback,
                )
                downloader.setUrl(url)
                downloader.setPath(path)
                downloader.resolution = quality.replace('p', '') if 'p' in quality else quality
                self.active_downloader = downloader

                await asyncio.to_thread(downloader.downloadVideo)

            else:
                downloader = Mp3Downloader(
                    url=url,
                    save_path=path,
                    progress_callback=progressCallback,
                    log_callback=logCallback,
                )
                self.active_downloader = downloader

                await asyncio.to_thread(downloader.downloadAsMp3)

            self.progress_bar.setProgress(100, "Download completed successfully")
            self.log_console.log("Download task finished successfully.", level="success")
            ui.notify("Download completed successfully", type="positive", position="top-right")

        except asyncio.CancelledError:
            self.log_console.log("Download operation was cancelled by user.", level="error")
            ui.notify("Download cancelled", type="warning", position="top-right")

        except Exception as exc:
            self.log_console.log(f"Download failed: {str(exc)}", level="error")
            ui.notify(f"Download failed: {str(exc)}", type="negative", position="top-right")

        finally:
            self.setDownloadingState(False)
            self.active_downloader = None

    def cancelDownload(self) -> None:
        """
        Cancels the active download task.
        """
        if self.download_task and not self.download_task.done():
            self.download_task.cancel()
        self.log_console.log("Cancelling single download...")
        self.setDownloadingState(False)

    def setDownloadingState(self, downloading: bool) -> None:
        """
        Updates button text and styling based on active processing state.

        Args:
            downloading (bool): True if downloading is in progress, False otherwise.
        """
        self.is_downloading = downloading
        if self.action_button:
            if downloading:
                self.action_button.text = "Cancel Download"
                self.action_button.props(remove="icon=download")
                self.action_button.props("icon=close")
                self.action_button.classes(remove="btn-primary")
                self.action_button.classes(add="btn-danger")
            else:
                self.action_button.text = "Download Media"
                self.action_button.props(remove="icon=close")
                self.action_button.props("icon=download")
                self.action_button.classes(remove="btn-danger")
                self.action_button.classes(add="btn-primary")
