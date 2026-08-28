"""
Format and quality selector component for choosing between MP4 video and MP3 audio.

Provides format radio buttons, dynamic resolution dropdown with skeleton loading states,
and automatic disabling of resolution selection when MP3 format is active.
"""

from typing import Callable, List, Optional
from nicegui import ui


class FormatPicker:
    """
    Renders and manages media format and quality resolution selection.
    """

    DEFAULT_RESOLUTIONS = ["1080p", "720p", "480p", "360p"]

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
        self.resolutions = list(self.DEFAULT_RESOLUTIONS)
        self.is_loading_resolutions = False

        self.on_format_change = on_format_change
        self.on_quality_change = on_quality_change

        self.format_toggle: Optional[ui.toggle] = None
        self.quality_select: Optional[ui.select] = None
        self.skeleton_container: Optional[ui.element] = None
        self.select_container: Optional[ui.element] = None

    def render(self) -> None:
        """
        Builds format radio buttons and quality dropdown elements.
        """
        with ui.row().classes('w-full items-start gap-4 flex-wrap sm:flex-nowrap'):
            # Format selection column
            with ui.column().classes('flex-1 min-w-[140px] gap-1'):
                ui.label('Media Format').classes('field-label')

                self.format_toggle = ui.toggle(
                    options={'MP4': 'MP4 Video', 'MP3': 'MP3 Audio'},
                    value=self.format_value,
                    on_change=self.handleFormatChanged,
                ).props('no-caps spread rounded unelevated toggle-color=brown-8 color=transparent text-color=grey-5').classes('w-full q-btn-toggle')

            # Quality selection column
            with ui.column().classes('flex-1 min-w-[140px] gap-1'):
                ui.label('Quality / Resolution').classes('field-label')

                self.skeleton_container = ui.element('div').classes('skeleton-shimmer hidden')

                self.select_container = ui.column().classes('w-full')
                with self.select_container:
                    self.quality_select = ui.select(
                        options=self.resolutions,
                        value=self.quality_value if self.format_value == 'MP4' else 'N/A',
                        on_change=self.handleQualityChanged,
                    ).props('outlined dense options-dense').classes('glass-input w-full')

                    # Syncs initial disabled state if starting in MP3 mode.
                    if self.format_value == 'MP3':
                        self.quality_select.props('disable')
                        self.quality_select.value = 'N/A'

    def handleFormatChanged(self, e: object) -> None:
        """
        Processes media format toggle updates and adjusts quality selector availability.

        Args:
            e (object): Toggle event containing the selected format string.
        """
        new_val = getattr(e, 'value', '') or 'MP4'
        self.format_value = str(new_val)

        if self.quality_select:
            if self.format_value == 'MP3':
                # Disables quality selector since MP3 downloads audio without video resolutions.
                self.quality_select.props('disable')
                self.quality_select.value = 'N/A'
            else:
                self.quality_select.props(remove='disable')
                if self.resolutions:
                    self.quality_value = self.resolutions[0]
                    self.quality_select.value = self.quality_value

        if self.on_format_change:
            self.on_format_change(self.format_value)

    def handleQualityChanged(self, e: object) -> None:
        """
        Processes resolution selection updates.

        Args:
            e (object): Select event containing the chosen resolution.
        """
        new_val = getattr(e, 'value', '') or ''
        if self.format_value == 'MP4' and new_val != 'N/A':
            self.quality_value = str(new_val)
            if self.on_quality_change:
                self.on_quality_change(self.quality_value)

    def setResolutions(self, resolutions_list: List[str]) -> None:
        """
        Updates available resolution options based on extracted video info.

        Args:
            resolutions_list (List[str]): List of available resolution labels (e.g., ['1080p', '720p']).
        """
        self.resolutions = resolutions_list if resolutions_list else list(self.DEFAULT_RESOLUTIONS)
        if self.quality_select:
            self.quality_select.options = self.resolutions
            if self.format_value == 'MP4':
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
        Retrieves the selected video quality setting.

        Returns:
            str: Quality setting string.
        """
        return self.quality_value
