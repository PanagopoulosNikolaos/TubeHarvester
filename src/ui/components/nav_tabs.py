"""
Navigation tabs component for switching between Single and Batch download views.

Provides styled tab switcher with custom image icons and brown-8 selection state.
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
        self.single_btn: Optional[ui.button] = None
        self.batch_btn: Optional[ui.button] = None

    def render(self) -> None:
        """
        Renders the tab bar into the current UI context with custom PNG icons.
        """
        with ui.element('div').classes('glass-tabs w-full flex flex-row items-center gap-2'):
            self.single_btn = ui.button(
                'Single Download',
                icon='img:/images/icons/YouTube-download.png',
                on_click=lambda: self.selectTab('single'),
            ).props('flat no-caps').classes('nav-tab-btn flex-1')

            self.batch_btn = ui.button(
                'Batch Download',
                icon='img:/images/icons/piled-batchfiles.png',
                on_click=lambda: self.selectTab('batch'),
            ).props('flat no-caps').classes('nav-tab-btn flex-1')

        self.updateTabStyles()

    def selectTab(self, tab_id: str) -> None:
        """
        Selects the specified tab and triggers the on_change callback.

        Args:
            tab_id (str): Tab identifier ('single' or 'batch').
        """
        self.active_tab = tab_id
        self.updateTabStyles()
        if self.on_change:
            self.on_change(self.active_tab)

    def setActiveTab(self, tab_id: str) -> None:
        """
        Updates the active tab state and styling without invoking the on_change callback.

        Args:
            tab_id (str): Tab identifier ('single' or 'batch').
        """
        self.active_tab = tab_id
        self.updateTabStyles()

    def handleTabChange(self, e: object) -> None:
        """
        Compatibility handler for event objects.

        Args:
            e (object): Event containing tab value.
        """
        new_val = getattr(e, 'value', str(e))
        self.selectTab(str(new_val))

    def updateTabStyles(self) -> None:
        """
        Updates button visual styles, applying brown-8 background to the selected tab.
        """
        if not self.single_btn or not self.batch_btn:
            return

        if self.active_tab == 'single':
            self.single_btn.classes(remove='tab-inactive', add='tab-active')
            self.batch_btn.classes(remove='tab-active', add='tab-inactive')
        else:
            self.batch_btn.classes(remove='tab-inactive', add='tab-active')
            self.single_btn.classes(remove='tab-active', add='tab-inactive')
