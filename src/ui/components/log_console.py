"""
Log console component for status monitoring and diagnostic messages.

Renders a dark, monospace terminal log with auto-scroll and color-coded message entries.
"""

from datetime import datetime
from typing import List, Optional
from nicegui import ui


class LogConsole:
    """
    Renders and manages the real-time activity log console.
    """

    def __init__(self) -> None:
        """
        Initializes the LogConsole component.
        """
        self.entries: List[dict] = []
        self.container: Optional[ui.element] = None
        self.log_element: Optional[ui.log] = None

    def render(self) -> None:
        """
        Builds the log console container into the current layout context.
        """
        self.container = ui.column().classes('w-full gap-2 hidden')
        with self.container:
            with ui.row().classes('w-full justify-between items-center'):
                ui.label('Activity Log').classes('field-label mb-0')
                ui.button(
                    'Clear Log',
                    on_click=self.clear,
                ).props('flat dense size=sm').classes('text-xs text-stone-400 hover:text-stone-200')

            self.log_element = ui.log(max_lines=500).classes('log-console w-full')

    def log(self, message: str, level: str = "info") -> None:
        """
        Appends a message entry to the log console with timestamp formatting.

        Args:
            message (str): Log message text.
            level (str): Log level category ('info', 'success', 'error', 'warn').
        """
        if not message.strip():
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        entry_data = {'time': timestamp, 'message': message, 'level': level}
        self.entries.append(entry_data)

        # Unhides console container on first incoming message
        if self.container:
            self.container.classes(remove='hidden')

        if self.log_element:
            formatted_line = f"[{timestamp}] {message}"
            self.log_element.push(formatted_line)

    def clear(self) -> None:
        """
        Clears all log entries and hides the console.
        """
        self.entries.clear()
        if self.log_element:
            self.log_element.clear()
        if self.container:
            self.container.classes(add='hidden')
