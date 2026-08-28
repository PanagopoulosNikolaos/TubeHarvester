"""
URL input component with debounced change notification and validation.

Renders styled text input with inline error feedback, clear button, and validation rules.
"""

import asyncio
from typing import Callable, Optional
from nicegui import ui


class UrlInput:
    """
    Renders and manages URL input with debouncing and inline validation states.
    """

    def __init__(
        self,
        placeholder: str = "https://www.youtube.com/watch?v=...",
        label: str = "YouTube URL",
        on_change_debounced: Optional[Callable[[str], None]] = None,
        debounce_delay: float = 0.9,
    ) -> None:
        """
        Initializes the UrlInput component.

        Args:
            placeholder (str): Input placeholder text.
            label (str): Label above the input field.
            on_change_debounced (Optional[Callable[[str], None]], optional): Debounced callback on value changes.
            debounce_delay (float): Debounce interval in seconds (default: 0.9s).
        """
        self.placeholder = placeholder
        self.label = label
        self.on_change_debounced = on_change_debounced
        self.debounce_delay = debounce_delay
        self.value: str = ""
        self.error_message: Optional[str] = None

        self.input_element: Optional[ui.input] = None
        self.error_label: Optional[ui.label] = None
        self.debounce_task: Optional[asyncio.Task] = None

    def render(self) -> None:
        """
        Builds the URL input container and attaches event handlers.
        """
        with ui.column().classes('w-full gap-1'):
            ui.label(self.label).classes('field-label')

            with ui.row().classes('w-full items-center relative'):
                self.input_element = ui.input(
                    placeholder=self.placeholder,
                    value=self.value,
                    on_change=self.handleInputChanged,
                ).props('outlined dense clearable').classes('glass-input w-full')

                # Attaches blur event for inline form validation.
                self.input_element.on('blur', self.handleBlur)

            self.error_label = ui.label('').classes('input-error-msg hidden')

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
            if self.debounce_task and not self.debounce_task.done():
                self.debounce_task.cancel()

            self.debounce_task = asyncio.create_task(self.triggerDebouncedChange(self.value))

    async def triggerDebouncedChange(self, text_val: str) -> None:
        """
        Waits for debounce delay before notifying subscribers.

        Args:
            text_val (str): The current text value.
        """
        try:
            await asyncio.sleep(self.debounce_delay)
            if self.on_change_debounced:
                self.on_change_debounced(text_val)
        except asyncio.CancelledError:
            pass

    def handleBlur(self) -> None:
        """
        Validates URL formatting when the input field loses focus.
        """
        if self.value:
            self.validate()

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
            valid_batch_tokens = ["playlist", "/channel/", "/user/", "/c/", "/@"]
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
