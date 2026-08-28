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
        self.log_box: Optional[ui.column] = None

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
                    icon='cleaning_services',
                    on_click=self.clear,
                ).props('flat dense size=sm').classes('text-xs text-stone-400 hover:text-stone-200')

            self.log_box = ui.column().classes('log-console w-full')

    def log(self, message: str, level: str = "info") -> None:
        """
        Appends a message entry to the log console with timestamp and color styling.

        Args:
            message (str): Log message text.
            level (str): Log level category ('info', 'success', 'error', 'warn').
        """
        if not message.strip():
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        entry_data = {'time': timestamp, 'message': message, 'level': level}
        self.entries.append(entry_data)

        # Unhides console on first incoming log message.
        if self.container:
            self.container.classes(remove='hidden')

        if self.log_box:
            with self.log_box:
                color_class = "log-info"
                if level == "success" or "complete" in message.lower() or "success" in message.lower():
                    color_class = "log-success"
                elif level == "error" or "error" in message.lower() or "failed" in message.lower():
                    color_class = "log-error"

                with ui.row().classes('log-entry w-full items-start gap-2'):
                    ui.label(f"[{timestamp}]").classes('text-stone-500 font-mono text-xs select-none shrink-0')
                    ui.label(message).classes(f'{color_class} text-xs font-mono flex-1')

            # Auto-scrolls console to the bottom of message list.
            ui.run_javascript(f"""
                const el = document.querySelector('.log-console');
                if (el) {{ el.scrollTop = el.scrollHeight; }}
            """)

    def clear(self) -> None:
        """
        Clears all log entries and hides the console.
        """
        self.entries.clear()
        if self.log_box:
            self.log_box.clear()
        if self.container:
            self.container.classes(add='hidden')
