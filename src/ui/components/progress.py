"""
Progress bar component with percentage indicator and operation status text.

Renders determinate progress tracking with smooth terracotta gradient fill.
"""

from typing import Optional
from nicegui import ui


class ProgressBar:
    """
    Renders and manages visual progress bars and status indicators.
    """

    def __init__(self) -> None:
        """
        Initializes the ProgressBar component.
        """
        self.percentage: int = 0
        self.status_text: str = ""
        self.is_visible: bool = False

        self.container: Optional[ui.element] = None
        self.progress_element: Optional[ui.linear_progress] = None
        self.percentage_label: Optional[ui.label] = None
        self.status_label: Optional[ui.label] = None

    def render(self) -> None:
        """
        Builds progress container, bar, and label elements.
        """
        self.container = ui.column().classes('w-full gap-2 hidden')
        with self.container:
            with ui.row().classes('w-full justify-between items-center text-xs'):
                self.status_label = ui.label('Ready').classes('font-medium text-stone-300')
                self.percentage_label = ui.label('0%').classes('font-mono font-semibold text-orange-400')

            self.progress_element = ui.linear_progress(value=0.0, show_value=False).classes('w-full rounded-full')

    def setProgress(self, percentage: int, status: Optional[str] = None) -> None:
        """
        Updates the progress percentage and optional status description.

        Args:
            percentage (int): Progress value between 0 and 100.
            status (Optional[str], optional): Descriptive label text.
        """
        self.percentage = max(0, min(100, percentage))
        self.setVisible(True)

        if self.progress_element:
            self.progress_element.value = self.percentage / 100.0

        if self.percentage_label:
            self.percentage_label.text = f"{self.percentage}%"

        if status:
            self.status_text = status
            if self.status_label:
                self.status_label.text = status

    def setVisible(self, is_visible: bool) -> None:
        """
        Toggles visibility of the progress indicator block.

        Args:
            is_visible (bool): True to display, False to hide.
        """
        self.is_visible = is_visible
        if self.container:
            if is_visible:
                self.container.classes(remove='hidden')
            else:
                self.container.classes(add='hidden')

    def reset(self) -> None:
        """
        Resets progress percentage to zero and hides the bar.
        """
        self.percentage = 0
        self.status_text = ""
        if self.progress_element:
            self.progress_element.value = 0.0
        if self.percentage_label:
            self.percentage_label.text = "0%"
        if self.status_label:
            self.status_label.text = "Ready"
        self.setVisible(False)
