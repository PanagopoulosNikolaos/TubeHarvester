"""
Navigation tabs component for switching between Single and Batch download views.

Provides glass-styled tab switcher with active tab glow and view transition triggers.
"""

from typing import Callable, Optional
from nicegui import ui


class NavTabs:
    """
    Renders and manages the navigation tab selector between Single and Batch modes.
    """

    def __init__(
        self,
        active_tab: str = "single",
        on_change: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initializes the NavTabs component.

        Args:
            active_tab (str): Initially active tab identifier ('single' or 'batch').
            on_change (Optional[Callable[[str], None]], optional): Callback triggered on tab switch.
        """
        self.active_tab = active_tab
        self.on_change = on_change
        self.tabs_element: Optional[ui.tabs] = None

    def render(self) -> ui.tabs:
        """
        Renders the tab bar into the current UI context.

        Returns:
            ui.tabs: The instantiated NiceGUI tabs component.
        """
        with ui.tabs(value=self.active_tab, on_change=self.handleTabChange).classes('glass-tabs w-full') as tabs:
            ui.tab('single', label='Single Download').classes('glass-tab flex-1')
            ui.tab('batch', label='Batch Download').classes('glass-tab flex-1')

        self.tabs_element = tabs
        return tabs

    def handleTabChange(self, e: object) -> None:
        """
        Handles tab selection change events from the NiceGUI component.

        Args:
            e (object): The event object containing the new tab value.
        """
        new_val = getattr(e, 'value', str(e))
        self.active_tab = str(new_val)
        if self.on_change:
            self.on_change(self.active_tab)
