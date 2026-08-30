"""
Batch download view module for TubeHarvester.

Manages playlist and channel scraping, parallel batch download queues,
cancellation confirmation dialogs, metadata previews, and progress tracking.
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional
from nicegui import ui

from ...extraction.batch_downloader import BatchDownloader
from ...extraction.channel_scraper import ChannelScraper
from ...extraction.playlist_scraper import PlaylistScraper
from ..components.format_picker import FormatPicker
from ..components.log_console import LogConsole
from ..components.path_selector import PathSelector
from ..components.progress import ProgressBar
from ..components.url_input import UrlInput


class BatchView:
    """
    Coordinates UI and background processing for batch playlist and channel downloads.
    """

    def __init__(self, on_mode_switch: Optional[Callable[[str, str], None]] = None) -> None:
        """
        Initializes the BatchView component state.

        Args:
            on_mode_switch (Optional[Callable[[str, str], None]], optional): Callback for auto-switching modes.
        """
        self.on_mode_switch = on_mode_switch
        self.is_downloading = False
        self.mode_value = "playlist"
        self.max_videos_value = "100"
        self.active_batch_downloader: Optional[BatchDownloader] = None
        self.batch_task: Optional[asyncio.Task] = None
        self.last_fetched_url: str = ""

        self.url_input = UrlInput(
            placeholder="https://www.youtube.com/playlist?list=...",
            label="Playlist URL",
            on_change_debounced=self.handleUrlDebounced,
        )
        self.path_selector = PathSelector()
        self.format_picker = FormatPicker()
        self.progress_bar = ProgressBar()
        self.log_console = LogConsole()

        self.playlist_btn: Optional[ui.button] = None
        self.channel_btn: Optional[ui.button] = None
        self.max_videos_input: Optional[ui.input] = None
        self.preview_card: Optional[ui.element] = None
        self.preview_title: Optional[ui.label] = None
        self.preview_count: Optional[ui.label] = None
        self.action_button: Optional[ui.button] = None
        self.client: Optional[object] = None

    def notifyUser(self, message: str, type: str = "info") -> None:
        """
        Sends a toast notification safely using the captured client context.

        Args:
            message (str): Toast notification text.
            type (str): Notification type ('info', 'positive', 'warning', 'negative').
        """
        try:
            if self.client:
                with self.client:
                    ui.notify(message, type=type, position="top-right")
            else:
                ui.notify(message, type=type, position="top-right")
        except Exception:
            pass

    def render(self) -> None:
        """
        Builds the batch download interface elements.
        """
        try:
            self.client = ui.context.client
        except Exception:
            pass

        with ui.card().classes('glass-card w-full'):
            # Root card flex container distributing form fields and anchored bottom controls
            with ui.column().classes('w-full h-full flex flex-col justify-between flex-1 gap-4'):
                # Dynamically spaced form field container matching single view dimensions
                with ui.column().classes('w-full flex-1 flex flex-col justify-between gap-3 sm:gap-4'):
                    # Mode selector with custom icons
                    with ui.column().classes('w-full gap-1'):
                        ui.label('Batch Mode').classes('field-label')

                        with ui.element('div').classes('glass-tabs w-full flex flex-row items-center gap-1'):
                            self.playlist_btn = ui.button(
                                'Playlist Download',
                                icon='img:/images/icons/playlist.png',
                                on_click=lambda: self.setMode('playlist'),
                            ).props('flat no-caps').classes('nav-tab-btn flex-1')

                            self.channel_btn = ui.button(
                                'Channel / Profile Scrape',
                                icon='img:/images/icons/channel.png',
                                on_click=lambda: self.setMode('channel'),
                            ).props('flat no-caps').classes('nav-tab-btn flex-1')

                        self.updateModeStyles()

                    # URL input
                    self.url_input.render()

                    # Format and Quality selector
                    self.format_picker.render()

                    # Options row: Max videos limit and destination path
                    with ui.row().classes('w-full items-start gap-4 flex-wrap sm:flex-nowrap'):
                        with ui.column().classes('w-full sm:w-1/3 gap-1'):
                            ui.label('Max Videos').classes('field-label')
                            self.max_videos_input = ui.input(
                                value=self.max_videos_value,
                                placeholder="100 or ALL",
                                on_change=self.handleMaxVideosChanged,
                            ).props('outlined dense').classes('glass-input w-full')

                        with ui.column().classes('flex-1 gap-1'):
                            self.path_selector.render()

                    # Batch preview card
                    self.preview_card = ui.element('div').classes('metadata-preview-card w-full hidden')
                    with self.preview_card:
                        with ui.column().classes('flex-1 gap-0'):
                            self.preview_title = ui.label('Queue target: ...').classes('preview-title')
                            with ui.element('div').classes('preview-meta'):
                                self.preview_count = ui.label('').classes('text-xs text-orange-400')

                # Action button container with circular download icon anchored at bottom
                with ui.row().classes('w-full justify-end mt-2'):
                    self.action_button = ui.button(
                        'Start Batch Download',
                        icon='img:/images/icons/download-circular-button.png',
                        on_click=self.handleActionClicked,
                    ).props('flat no-caps').classes('btn-primary w-full sm:w-auto')

                # Progress indicator
                self.progress_bar.render()

                # Real-time activity log
                self.log_console.render()

    def setUrl(self, url: str) -> None:
        """
        Sets the URL value and triggers processing.

        Args:
            url (str): Target batch URL.
        """
        self.url_input.setValue(url)
        self.handleUrlDebounced(url)

    def handleUrlDebounced(self, url: str) -> None:
        """
        Processes batch link typing, link type auto-detection, and title discovery.

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

        # Auto-detects single video URL and switches to Single view if handler registered
        if link_type == 'single' and self.on_mode_switch:
            self.last_fetched_url = cleaned_url
            self.notifyUser("Detected single video link. Switching to Single Download mode.", type="info")
            self.on_mode_switch('single', cleaned_url)
            return

        if "youtube.com" in cleaned_url.lower() or "youtu.be" in cleaned_url.lower():
            self.last_fetched_url = cleaned_url
            asyncio.create_task(self.fetchBatchPreviewAsync(cleaned_url))

    async def fetchBatchPreviewAsync(self, url: str) -> None:
        """
        Queries playlist or channel title in a background thread.

        Args:
            url (str): Target batch URL.
        """
        try:
            if self.mode_value == 'playlist':
                scraper = PlaylistScraper(timeout=0.0)
                title = await asyncio.to_thread(scraper.getPlaylistTitle, url)
                if title:
                    self.showPreview(f"Playlist: {title}", "Ready to scrape videos")
            else:
                channel_scraper = ChannelScraper(timeout=0.0)
                name = await asyncio.to_thread(channel_scraper.getChannelName, url)
                if name:
                    self.showPreview(f"Channel: {name}", "Ready to scan channel playlists and uploads")
        except Exception:
            self.hidePreview()

    def showPreview(self, title: str, subtitle: str) -> None:
        """
        Displays batch queue target preview.

        Args:
            title (str): Title description.
            subtitle (str): Subtitle note.
        """
        if self.preview_card and self.preview_title and self.preview_count:
            self.preview_title.text = title
            self.preview_count.text = subtitle
            self.preview_card.classes(remove='hidden')

    def hidePreview(self) -> None:
        """
        Hides the batch preview card.
        """
        if self.preview_card:
            self.preview_card.classes(add='hidden')

    def setMode(self, new_mode: str) -> None:
        """
        Updates batch mode setting and adjusts URL placeholder and max limits.

        Args:
            new_mode (str): 'playlist' or 'channel'.
        """
        self.mode_value = new_mode
        self.updateModeStyles()

        if self.mode_value == 'playlist':
            self.url_input.label = "Playlist URL"
            self.max_videos_value = "100"
            if self.max_videos_input:
                self.max_videos_input.value = "100"
        else:
            self.url_input.label = "Channel / User URL"
            self.max_videos_value = "ALL"
            if self.max_videos_input:
                self.max_videos_input.value = "ALL"

    def updateModeStyles(self) -> None:
        """
        Updates button visual styles, applying brown-8 background to the selected mode button.
        """
        if not self.playlist_btn or not self.channel_btn:
            return

        if self.mode_value == 'playlist':
            self.playlist_btn.classes(remove='tab-inactive', add='tab-active')
            self.channel_btn.classes(remove='tab-active', add='tab-inactive')
        else:
            self.channel_btn.classes(remove='tab-inactive', add='tab-active')
            self.playlist_btn.classes(remove='tab-active', add='tab-inactive')

    def handleModeChanged(self, e: object) -> None:
        """
        Compatibility handler for mode toggle events.

        Args:
            e (object): Toggle event containing the selected mode key.
        """
        new_mode = getattr(e, 'value', '') or 'playlist'
        self.setMode(str(new_mode))

    def handleMaxVideosChanged(self, e: object) -> None:
        """
        Handles user input updates to the maximum video count setting.

        Args:
            e (object): Input event carrying the text value.
        """
        val = getattr(e, 'value', '') or '100'
        self.max_videos_value = str(val).strip()

    def handleActionClicked(self) -> None:
        """
        Handles primary button clicks, triggering cancellation confirmation or job start.
        """
        if self.is_downloading:
            self.openCancelConfirmationDialog()
        else:
            self.startBatchDownload()

    def openCancelConfirmationDialog(self) -> None:
        """
        Opens a modal confirmation dialog to prevent accidental batch cancellation.
        """
        with ui.dialog() as dialog, ui.card().classes('glass-card min-w-[320px] max-w-[420px]'):
            ui.label('Cancel Batch Download?').classes('text-lg font-bold text-white mb-1')
            ui.label(
                'Are you sure you want to stop the batch download? '
                'Any files downloaded so far will be kept.'
            ).classes('text-xs text-stone-300 mb-4')

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Go Back', on_click=dialog.close).classes('btn-secondary px-4')

                def confirmCancel() -> None:
                    dialog.close()
                    self.cancelBatchDownload()

                ui.button('Cancel Download', on_click=confirmCancel).classes('btn-danger px-4')

        dialog.open()

    def startBatchDownload(self) -> None:
        """
        Validates form inputs and launches asynchronous batch scraping and downloads.
        """
        if not self.url_input.validate(is_batch=True):
            return

        if not self.path_selector.validate():
            return

        url = self.url_input.getValue()
        base_path = self.path_selector.getValue()
        media_format = self.format_picker.getFormat()
        quality = self.format_picker.getQuality()
        max_count = 100
        if self.max_videos_value.upper() == "ALL":
            max_count = 10000
        else:
            try:
                max_count = int(self.max_videos_value)
            except ValueError:
                max_count = 100

        self.setDownloadingState(True)
        self.progress_bar.reset()
        self.progress_bar.setProgress(0, "Scanning video queue...")
        self.log_console.log(f"Starting batch operation in {self.mode_value} mode.")

        self.batch_task = asyncio.create_task(
            self.runBatchAsync(url, base_path, media_format, quality, max_count)
        )

    async def runBatchAsync(
        self,
        url: str,
        base_path: str,
        media_format: str,
        quality: str,
        max_videos: int,
    ) -> None:
        """
        Coordinates playlist/channel discovery and multi-threaded batch downloading.

        Args:
            url (str): Source playlist or channel URL.
            base_path (str): Root destination directory.
            media_format (str): Target format ('MP4' or 'MP3').
            quality (str): Quality resolution.
            max_videos (int): Maximum video limit count.
        """
        video_queue: List[Dict[str, Any]] = []

        try:
            self.log_console.log(f"Scraping media items from {url}...")

            if self.mode_value == 'playlist':
                scraper = PlaylistScraper(
                    timeout=0.2,
                    log_callback=lambda msg: self.log_console.log(msg),
                )
                playlist_title = await asyncio.to_thread(scraper.getPlaylistTitle, url)

                def fetchProgress(current: int, total: int, pct: int) -> None:
                    self.progress_bar.setProgress(pct, f"Discovered {current}/{total} videos ({pct}%)")

                raw_videos = await asyncio.to_thread(
                    scraper.scrapePlaylist,
                    url,
                    max_videos,
                    fetchProgress,
                )

                for item in raw_videos:
                    video_queue.append({
                        'url': item['url'],
                        'title': item['title'],
                        'folder': f"Playlists/{playlist_title}",
                    })

            else:
                channel_scraper = ChannelScraper(
                    timeout=0.2,
                    log_callback=lambda msg: self.log_console.log(msg),
                )
                channel_info = await asyncio.to_thread(
                    channel_scraper.scrapeChannel,
                    url,
                    max_videos,
                )
                channel_name = channel_info.get('channel_name', 'Channel')

                # Adds videos from channel playlists.
                for pl in channel_info.get('playlists', []):
                    pl_title = pl.get('title', 'Playlist')
                    for v in pl.get('videos', []):
                        video_queue.append({
                            'url': v['url'],
                            'title': v['title'],
                            'folder': f"{channel_name}/{pl_title}",
                        })

                # Adds standalone upload videos.
                for sv in channel_info.get('standalone_videos', []):
                    video_queue.append({
                        'url': sv['url'],
                        'title': sv['title'],
                        'folder': f"{channel_name}/Uploads",
                    })

            if not video_queue:
                self.log_console.log("No videos found to download.", level="error")
                self.notifyUser("No videos discovered at the specified URL.", type="warning")
                self.setDownloadingState(False)
                return

            self.log_console.log(f"Queued {len(video_queue)} videos for download.", level="info")
            self.progress_bar.setProgress(0, f"Downloading 0/{len(video_queue)} videos")

            # Launches concurrent multi-threaded batch downloader.
            def batchProgress(pct: int) -> None:
                self.progress_bar.setProgress(pct, "Downloading queue")

            batch_downloader = BatchDownloader(
                max_workers=1,
                progress_callback=batchProgress,
                log_callback=lambda msg: self.log_console.log(msg),
            )
            self.active_batch_downloader = batch_downloader

            is_custom = self.path_selector.isCustom()
            if is_custom:
                self.log_console.log(f"Custom path selected: files will be dumped directly into {base_path}", level="info")

            summary = await asyncio.to_thread(
                batch_downloader.downloadBatch,
                video_queue,
                media_format,
                base_path,
                quality,
                is_custom,
            )

            successful = summary.get('successful', 0)
            failed = summary.get('failed', 0)

            if failed == 0:
                self.progress_bar.setProgress(100, f"Batch complete: {successful}/{len(video_queue)} successful")
                self.log_console.log(f"Batch completed: {successful} successful.", level="success")
                self.notifyUser(f"Batch complete: {successful}/{len(video_queue)} downloaded", type="positive")
            else:
                self.log_console.log(f"Batch finished: {successful} successful, {failed} failed.", level="error")
                self.notifyUser(f"Batch complete with {failed} failures.", type="warning")

        except asyncio.CancelledError:
            self.log_console.log("Batch process cancelled by user.", level="error")
            self.notifyUser("Batch download cancelled", type="warning")

        except Exception as exc:
            self.log_console.log(f"Batch processing error: {str(exc)}", level="error")
            self.notifyUser(f"Batch error: {str(exc)}", type="negative")

        finally:
            self.setDownloadingState(False)
            self.active_batch_downloader = None

    def cancelBatchDownload(self) -> None:
        """
        Cancels active background scraping and terminates pending downloads.
        """
        if self.active_batch_downloader:
            self.active_batch_downloader.cancelDownload()
        if self.batch_task and not self.batch_task.done():
            self.batch_task.cancel()
        self.setDownloadingState(False)

    def setDownloadingState(self, downloading: bool) -> None:
        """
        Updates batch action button text and visual danger cues.

        Args:
            downloading (bool): True if batch operation is running, False otherwise.
        """
        self.is_downloading = downloading
        if self.action_button:
            if downloading:
                self.action_button.text = "Cancel Batch"
                self.action_button.props('icon=""')
                self.action_button.classes(remove="btn-primary")
                self.action_button.classes(add="btn-danger")
            else:
                self.action_button.text = "Start Batch Download"
                self.action_button.props('icon="img:/images/icons/download-circular-button.png"')
                self.action_button.classes(remove="btn-danger")
                self.action_button.classes(add="btn-primary")
