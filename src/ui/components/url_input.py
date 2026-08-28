"""
URL input component with debounced change notification, clipboard paste, and link type auto-detection.

Renders styled text input with inline error feedback, quick-paste action, and validation rules.
"""

import asyncio
from typing import Callable, Optional
from nicegui import ui


class UrlInput:
    """
    Renders and manages URL input with debouncing, quick-paste, and inline validation states.
    """

    def __init__(
        self,
        placeholder: str = "https://www.youtube.com/watch?v=...",
        label: str = "YouTube URL",
        on_change_debounced: Optional[Callable[[str], None]] = None,
        debounce_delay: float = 0.8,
    ) -> None:
        """
        Initializes the UrlInput component.

        Args:
            placeholder (str): Input placeholder text.
            label (str): Label above the input field.
            on_change_debounced (Optional[Callable[[str], None]], optional): Debounced callback on value changes.
            debounce_delay (float): Debounce interval in seconds (default: 0.8s).
        """
        self.placeholder = placeholder
        self.label = label
        self.on_change_debounced = on_change_debounced
        self.debounce_delay = debounce_delay
        self.value: str = ""
        self.error_message: Optional[str] = None

        self.input_element: Optional[ui.input] = None
        self.error_label: Optional[ui.label] = None
        self.debounce_timer: Optional[ui.timer] = None

    def render(self) -> None:
        """
        Builds the URL input container and attaches event handlers and quick-paste button.
        """
        with ui.column().classes('w-full gap-1'):
            ui.label(self.label).classes('field-label')

            with ui.row().classes('w-full items-center gap-2'):
                self.input_element = ui.input(
                    placeholder=self.placeholder,
                    value=self.value,
                    on_change=self.handleInputChanged,
                ).props('outlined dense clearable').classes('glass-input flex-1')

                # Attaches blur event for inline form validation.
                self.input_element.on('blur', self.handleBlur)

                # Quick-Paste button invoking browser clipboard API
                ui.button(
                    'Paste',
                    on_click=self.pasteFromClipboard,
                ).props('flat no-caps').classes('btn-secondary px-3')

            self.error_label = ui.label('').classes('input-error-msg hidden')

    async def pasteFromClipboard(self) -> None:
        """
        Reads plain text from the client clipboard and populates the input field.
        """
        try:
            pasted_text = await ui.run_javascript(
                'navigator.clipboard ? navigator.clipboard.readText() : ""'
            )
            if pasted_text and isinstance(pasted_text, str) and pasted_text.strip():
                clean_url = pasted_text.strip()
                self.setValue(clean_url)
                if self.on_change_debounced:
                    self.on_change_debounced(clean_url)
        except Exception:
            pass

    def handleInputChanged(self, e: object) -> None:
        """
        Handles raw input changes and coordinates debounced event dispatch.

        Args:
            e (object): Input event carrying the updated text value.
        """
        new_val = getattr(e, 'value', '') or ''
        self.value = str(new_val).strip()

        # Clears active validation errors as user types.
        if self.error_message:
            self.clearError()

        if self.on_change_debounced:
            if self.debounce_timer:
                self.debounce_timer.cancel()

            current_text = self.value

            def onTimeout() -> None:
                if self.on_change_debounced:
                    self.on_change_debounced(current_text)

            self.debounce_timer = ui.timer(self.debounce_delay, onTimeout, once=True)

    def handleBlur(self) -> None:
        """
        Validates URL formatting when the input field loses focus.
        """
        if self.value:
            self.validate()

    @staticmethod
    def detectUrlType(url: str) -> str:
        """
        Detects whether a URL represents a single video, playlist, or channel.

        Args:
            url (str): YouTube URL string.

        Returns:
            str: 'playlist', 'channel', 'single', or 'unknown'.
        """
        raw = url.strip().lower()
        if not raw:
            return 'unknown'

        if "list=" in raw:
            return 'playlist'

        channel_tokens = ["/channel/", "/user/", "/c/", "/@"]
        if any(token in raw for token in channel_tokens):
            return 'channel'

        if "youtube.com/watch" in raw or "youtu.be/" in raw or "youtube.com/shorts/" in raw:
            return 'single'

        return 'unknown'

    def validate(self, is_batch: bool = False) -> bool:
        """
        Validates the current URL against YouTube domain and mode criteria.

        Args:
            is_batch (bool): True if validating batch mode playlist/channel URLs.

        Returns:
            bool: True if input is valid, False otherwise.
        """
        raw = self.value.strip().lower()
        if not raw:
            self.setError("Please enter a URL.")
            return False

        if "youtube.com" not in raw and "youtu.be" not in raw:
            self.setError("Please enter a valid YouTube URL.")
            return False

        if is_batch:
            valid_batch_tokens = ["playlist", "list=", "/channel/", "/user/", "/c/", "/@"]
            if not any(token in raw for token in valid_batch_tokens):
                self.setError("Please enter a valid playlist or channel URL.")
                return False

        self.clearError()
        return True

    def setError(self, msg: str) -> None:
        """
        Displays an error message below the input field.

        Args:
            msg (str): Error message text to display.
        """
        self.error_message = msg
        if self.error_label:
            self.error_label.text = msg
            self.error_label.classes(remove='hidden')

    def clearError(self) -> None:
        """
        Hides and resets the inline error message.
        """
        self.error_message = None
        if self.error_label:
            self.error_label.text = ''
            self.error_label.classes(add='hidden')

    def getValue(self) -> str:
        """
        Retrieves the trimmed current text value.

        Returns:
            str: Current URL string.
        """
        return self.value

    def setValue(self, val: str) -> None:
        """
        Updates the input value programmatically.

        Args:
            val (str): New URL value string.
        """
        self.value = val
        if self.input_element:
            self.input_element.value = val
