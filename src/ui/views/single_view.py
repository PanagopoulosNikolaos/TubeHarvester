"""
Single download view controller for processing individual YouTube video and audio links.

Orchestrates URL validation, metadata discovery, thumbnail preview, progress monitoring,
and background worker threads.
"""

import asyncio
from typing import Callable, Optional
from nicegui import ui

from ...extraction.mp3_downloader import Mp3Downloader
from ...extraction.mp4_downloader import Mp4Downloader
from ..components.format_picker import FormatPicker
from ..components.log_console import LogConsole
from ..components.path_selector import PathSelector
from ..components.progress import ProgressBar
from ..components.url_input import UrlInput


class SingleView:
    """
    Manages the Single Download view UI lifecycle, metadata preview, and download operations.
    """

    def __init__(self, on_mode_switch: Optional[Callable[[str, str], None]] = None) -> None:
        """
        Initializes SingleView components and state variables.

        Args:
            on_mode_switch (Optional[Callable[[str, str], None]], optional): Callback for auto-switching modes.
        """
        self.on_mode_switch = on_mode_switch
        self.url_input = UrlInput(
            placeholder="https://www.youtube.com/watch?v=...",
            label="YouTube Video URL",
            on_change_debounced=self.handleUrlDebounced,
        )
        self.format_picker = FormatPicker()
        self.path_selector = PathSelector()
        self.progress_bar = ProgressBar()
        self.log_console = LogConsole()

        self.last_fetched_url: str = ""
        self.is_downloading: bool = False
        self.download_task: Optional[asyncio.Task] = None
        self.active_downloader: Optional[object] = None

        self.card_container: Optional[ui.card] = None
        self.preview_card: Optional[ui.element] = None
        self.preview_thumb: Optional[ui.image] = None
        self.preview_title: Optional[ui.label] = None
        self.preview_author: Optional[ui.label] = None
        self.preview_duration: Optional[ui.label] = None
        self.action_button: Optional[ui.button] = None

    def render(self) -> None:
        """
        Builds the single download interface elements with metadata preview.
        """
        with ui.card().classes('glass-card w-full') as card:
            self.card_container = card

            # Form fields
            with ui.column().classes('w-full gap-4'):
                self.url_input.render()
                self.format_picker.render()
                self.path_selector.render()

                # Pre-download metadata preview card
                self.preview_card = ui.element('div').classes('metadata-preview-card w-full hidden')
                with self.preview_card:
                    with ui.element('div').classes('preview-thumb-box'):
                        self.preview_thumb = ui.image('').classes('preview-thumb-img')

                    with ui.column().classes('flex-1 gap-0'):
                        self.preview_title = ui.label('Loading video...').classes('preview-title')
                        with ui.element('div').classes('preview-meta'):
                            self.preview_author = ui.label('').classes('text-xs text-stone-400')
                            self.preview_duration = ui.label('').classes('text-xs text-orange-400')

                # Action button container
                with ui.row().classes('w-full justify-end mt-2'):
                    self.action_button = ui.button(
                        'Download Media',
                        icon='img:/images/icons/YouTube-download.png',
                        on_click=self.handleActionClicked,
                    ).classes('btn-primary w-full sm:w-auto')

                # Progress indicator
                self.progress_bar.render()

                # Real-time activity log
                self.log_console.render()

    def setUrl(self, url: str) -> None:
        """
        Sets the URL value and triggers metadata fetching.

        Args:
            url (str): Target YouTube URL.
        """
        self.url_input.setValue(url)
        self.handleUrlDebounced(url)

    def handleUrlDebounced(self, url: str) -> None:
        """
        Triggers link auto-detection and background metadata preview discovery.

        Args:
            url (str): The current URL text.
        """
        cleaned_url = url.strip()
        if not cleaned_url:
            self.hidePreview()
            return

        if cleaned_url == self.last_fetched_url:
            return

        link_type = UrlInput.detectUrlType(cleaned_url)

        # Auto-detects playlist or channel URL and delegates to batch view if handler registered
        if link_type in ['playlist', 'channel'] and self.on_mode_switch:
            self.last_fetched_url = cleaned_url
            ui.notify(f"Detected {link_type} link. Switching to Batch Download mode.", type="info", position="top-right")
            self.on_mode_switch('batch', cleaned_url)
            return

        if "youtube.com" in cleaned_url.lower() or "youtu.be" in cleaned_url.lower():
            self.last_fetched_url = cleaned_url
            asyncio.create_task(self.fetchResolutionsAndPreviewAsync(cleaned_url))

    async def fetchResolutionsAndPreviewAsync(self, url: str) -> None:
        """
        Queries video metadata and formats in a background thread.

        Args:
            url (str): The YouTube video URL to query.
        """
        self.format_picker.setLoadingResolutions(True)
        self.log_console.log(f"Fetching video info for: {url}")

        try:
            downloader = Mp4Downloader()
            downloader.setUrl(url)

            # Runs yt-dlp metadata extraction asynchronously in a worker thread.
            info = await asyncio.to_thread(downloader.fetchVideoInfo)
            if not info:
                self.hidePreview()
                return

            # Extracts preview metadata
            title = info.get('title', 'YouTube Video')
            uploader = info.get('uploader') or info.get('channel') or ''
            duration_sec = info.get('duration', 0)
            thumbnail = info.get('thumbnail', '')

            # Formats duration as MM:SS or HH:MM:SS
            duration_text = ""
            if duration_sec:
                mins, secs = divmod(int(duration_sec), 60)
                hrs, mins = divmod(mins, 60)
                duration_text = f"{hrs}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins}:{secs:02d}"

            self.showPreview(title, uploader, duration_text, thumbnail)

            # Discovers available resolutions
            formats = info.get('formats', [])
            resolutions_set = set()
            for fmt in formats:
                height = fmt.get('height')
                if height and isinstance(height, int) and height >= 144:
                    resolutions_set.add(f"{height}p")

            if resolutions_set:
                sorted_resolutions = sorted(
                    list(resolutions_set),
                    key=lambda r: int(r.replace('p', '')) if r.replace('p', '').isdigit() else 0,
                    reverse=True,
                )
                self.format_picker.setResolutions(sorted_resolutions)
                self.log_console.log(f"Discovered resolutions: {', '.join(sorted_resolutions)}", level="info")

        except Exception as exc:
            self.log_console.log(f"Failed to fetch video info: {str(exc)}", level="warn")
            self.hidePreview()

        finally:
            self.format_picker.setLoadingResolutions(False)

    def showPreview(self, title: str, uploader: str, duration: str, thumbnail: str) -> None:
        """
        Populates and displays the pre-download metadata preview card.

        Args:
            title (str): Video title.
            uploader (str): Uploader or channel name.
            duration (str): Formatted duration string.
            thumbnail (str): Thumbnail image URL.
        """
        if self.preview_card and self.preview_title and self.preview_author and self.preview_duration and self.preview_thumb:
            self.preview_title.text = title
            self.preview_author.text = uploader
            self.preview_duration.text = duration
            if thumbnail:
                self.preview_thumb.source = thumbnail
            self.preview_card.classes(remove='hidden')

    def hidePreview(self) -> None:
        """
        Hides the metadata preview card.
        """
        if self.preview_card:
            self.preview_card.classes(add='hidden')

    def handleActionClicked(self) -> None:
        """
        Dispatches primary action button clicks based on current processing state.
        """
        if self.is_downloading:
            self.cancelDownload()
        else:
            self.startDownload()

    def startDownload(self) -> None:
        """
        Validates form inputs and launches asynchronous download execution.
        """
        if not self.url_input.validate(is_batch=False):
            return

        if not self.path_selector.validate():
            return

        url = self.url_input.getValue()
        path = self.path_selector.getValue()
        media_format = self.format_picker.getFormat()
        quality = self.format_picker.getQuality()

        self.progress_bar.reset()
        self.progress_bar.setVisible(True)
        self.progress_bar.setProgress(0, "Starting download...")
        self.setDownloadingState(True)
        self.log_console.log(f"Starting {media_format} download for: {url}")

        self.download_task = asyncio.create_task(
            self.executeDownloadAsync(url, path, media_format, quality)
        )

    async def executeDownloadAsync(
        self,
        url: str,
        path: str,
        media_format: str,
        quality: str,
    ) -> None:
        """
        Runs the download worker in a background thread and streams progress.

        Args:
            url (str): Target video URL.
            path (str): Save destination folder.
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
                self.action_button.props('icon=""')
                self.action_button.classes(remove="btn-primary")
                self.action_button.classes(add="btn-danger")
            else:
                self.action_button.text = "Download Media"
                self.action_button.props('icon="img:/images/icons/YouTube-download.png"')
                self.action_button.classes(remove="btn-danger")
                self.action_button.classes(add="btn-primary")
