"""
Format and quality selector component for choosing between MP4 video and MP3 audio.

Provides format toggle buttons with custom PNG icons, dynamic resolution dropdown
for video, bitrate quality selector for audio, and skeleton loading states.
"""

from typing import Callable, List, Optional
from nicegui import ui


class FormatPicker:
    """
    Renders and manages media format and quality resolution/bitrate selection.
    """

    DEFAULT_RESOLUTIONS = ["1080p", "720p", "480p", "360p"]
    DEFAULT_BITRATES = ["320 kbps (Best)", "256 kbps (High)", "192 kbps (Medium)", "128 kbps (Standard)"]

    def __init__(
        self,
        default_format: str = "MP4",
        default_quality: str = "1080p",
        on_format_change: Optional[Callable[[str], None]] = None,
        on_quality_change: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initializes the FormatPicker component.

        Args:
            default_format (str): Initial format ('MP4' or 'MP3').
            default_quality (str): Initial quality setting.
            on_format_change (Optional[Callable[[str], None]], optional): Format switch callback.
            on_quality_change (Optional[Callable[[str], None]], optional): Quality change callback.
        """
        self.format_value = default_format
        self.quality_value = default_quality
        self.bitrate_value = self.DEFAULT_BITRATES[0]
        self.resolutions = list(self.DEFAULT_RESOLUTIONS)
        self.bitrates = list(self.DEFAULT_BITRATES)
        self.is_loading_resolutions = False

        self.on_format_change = on_format_change
        self.on_quality_change = on_quality_change

        self.mp4_btn: Optional[ui.button] = None
        self.mp3_btn: Optional[ui.button] = None
        self.quality_label: Optional[ui.label] = None
        self.quality_select: Optional[ui.select] = None
        self.skeleton_container: Optional[ui.element] = None
        self.select_container: Optional[ui.element] = None

    def render(self) -> None:
        """
        Builds format buttons with custom PNG icons and quality dropdown elements.
        """
        with ui.row().classes('w-full items-start gap-4 flex-wrap sm:flex-nowrap'):
            # Format selection column
            with ui.column().classes('flex-1 min-w-[140px] gap-1'):
                ui.label('Media Format').classes('field-label')

                with ui.element('div').classes('glass-tabs w-full flex flex-row items-center gap-1'):
                    self.mp4_btn = ui.button(
                        'MP4 Video',
                        icon='img:/images/icons/download-mp4.png',
                        on_click=lambda: self.setFormat('MP4'),
                    ).props('flat no-caps').classes('nav-tab-btn flex-1')

                    self.mp3_btn = ui.button(
                        'MP3 Audio',
                        icon='img:/images/icons/download-mp3.png',
                        on_click=lambda: self.setFormat('MP3'),
                    ).props('flat no-caps').classes('nav-tab-btn flex-1')

                self.updateFormatStyles()

            # Quality / Bitrate selection column
            with ui.column().classes('flex-1 min-w-[140px] gap-1'):
                initial_label = 'Quality / Resolution' if self.format_value == 'MP4' else 'Audio Bitrate'
                self.quality_label = ui.label(initial_label).classes('field-label')

                self.skeleton_container = ui.element('div').classes('skeleton-shimmer hidden')

                self.select_container = ui.column().classes('w-full')
                with self.select_container:
                    initial_options = self.resolutions if self.format_value == 'MP4' else self.bitrates
                    initial_val = self.quality_value if self.format_value == 'MP4' else self.bitrate_value

                    self.quality_select = ui.select(
                        options=initial_options,
                        value=initial_val,
                        on_change=self.handleQualityChanged,
                    ).props('outlined dense options-dense').classes('glass-input w-full')

    def setFormat(self, new_format: str) -> None:
        """
        Sets the active media format and updates dropdown options between resolution and bitrate.

        Args:
            new_format (str): 'MP4' or 'MP3'.
        """
        self.format_value = new_format
        self.updateFormatStyles()

        if self.quality_select and self.quality_label:
            if self.format_value == 'MP3':
                self.quality_label.text = 'Audio Bitrate'
                self.quality_select.options = self.bitrates
                self.quality_select.value = self.bitrate_value
            else:
                self.quality_label.text = 'Quality / Resolution'
                self.quality_select.options = self.resolutions
                self.quality_select.value = self.quality_value

        if self.on_format_change:
            self.on_format_change(self.format_value)

    def handleFormatChanged(self, e: object) -> None:
        """
        Processes media format toggle updates and adjusts quality selector availability.

        Args:
            e (object): Toggle event containing the selected format string.
        """
        new_val = getattr(e, 'value', '') or 'MP4'
        self.setFormat(str(new_val))

    def updateFormatStyles(self) -> None:
        """
        Updates button visual styles, applying brown-8 background to the selected format button.
        """
        if not self.mp4_btn or not self.mp3_btn:
            return

        if self.format_value == 'MP4':
            self.mp4_btn.classes(remove='tab-inactive', add='tab-active')
            self.mp3_btn.classes(remove='tab-active', add='tab-inactive')
        else:
            self.mp3_btn.classes(remove='tab-inactive', add='tab-active')
            self.mp4_btn.classes(remove='tab-active', add='tab-inactive')

    def handleQualityChanged(self, e: object) -> None:
        """
        Processes resolution or bitrate selection updates.

        Args:
            e (object): Select event containing the chosen quality.
        """
        new_val = getattr(e, 'value', '') or ''
        if not new_val:
            return

        if self.format_value == 'MP4':
            self.quality_value = str(new_val)
            if self.on_quality_change:
                self.on_quality_change(self.quality_value)
        else:
            self.bitrate_value = str(new_val)
            if self.on_quality_change:
                self.on_quality_change(self.bitrate_value)

    def setResolutions(self, resolutions_list: List[str]) -> None:
        """
        Updates available resolution options based on extracted video info.

        Args:
            resolutions_list (List[str]): List of available resolution labels (e.g., ['1080p', '720p']).
        """
        self.resolutions = resolutions_list if resolutions_list else list(self.DEFAULT_RESOLUTIONS)
        if self.quality_select and self.format_value == 'MP4':
            self.quality_select.options = self.resolutions
            self.quality_value = self.resolutions[0]
            self.quality_select.value = self.quality_value

    def setLoadingResolutions(self, is_loading: bool) -> None:
        """
        Toggles skeleton loading animation during resolution extraction.

        Args:
            is_loading (bool): True to display skeleton loader, False to restore dropdown.
        """
        self.is_loading_resolutions = is_loading

        if self.skeleton_container and self.select_container:
            if is_loading and self.format_value == 'MP4':
                self.skeleton_container.classes(remove='hidden')
                self.select_container.classes(add='hidden')
            else:
                self.skeleton_container.classes(add='hidden')
                self.select_container.classes(remove='hidden')

    def getFormat(self) -> str:
        """
        Retrieves the selected format ('MP4' or 'MP3').

        Returns:
            str: Format string.
        """
        return self.format_value

    def getQuality(self) -> str:
        """
        Retrieves the selected video quality setting or audio bitrate.

        Returns:
            str: Quality setting string.
        """
        if self.format_value == 'MP4':
            return self.quality_value
        return self.bitrate_value
