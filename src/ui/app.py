"""
Main NiceGUI web application bootstrap for TubeHarvester.

Constructs application layout, injects global styles, orchestrates view transitions,
coordinates URL auto-detection mode switching, and exposes the entry point runner.
"""

from pathlib import Path
from nicegui import app, ui

from .components.header import Header
from .components.nav_tabs import NavTabs
from .theme import injectTheme
from .views.batch_view import BatchView
from .views.single_view import SingleView

# Root static images directory path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGES_DIR = PROJECT_ROOT / "images"
CRAWLER_ICON = IMAGES_DIR / "icons" / "crawler.png"

# Registers static file route for icon and media assets
app.add_static_files('/images', str(IMAGES_DIR))


def buildLayout() -> None:
    """
    Constructs the application shell, header, tab navigation, and dynamic view containers.
    """
    injectTheme()

    # Outer centered viewport wrapper with fluid scaling
    with ui.element('div').classes('app-wrapper'):
        with ui.element('div').classes('app-container'):
            header = Header()
            header.render()

            # Container placeholders for tab swapping
            single_container = ui.column().classes('w-full')
            batch_container = ui.column().classes('w-full hidden')

            nav_tabs: NavTabs

            def switchView(selected_tab: str) -> None:
                """
                Toggles visibility between Single and Batch download views.

                Args:
                    selected_tab (str): Active tab identifier ('single' or 'batch').
                """
                if selected_tab == 'single':
                    single_container.classes(remove='hidden')
                    batch_container.classes(add='hidden')
                else:
                    single_container.classes(add='hidden')
                    batch_container.classes(remove='hidden')

            def handleAutoModeSwitch(target_mode: str, url: str) -> None:
                """
                Coordinates cross-view mode switching when URL auto-detection triggers.

                Args:
                    target_mode (str): Destination mode ('single' or 'batch').
                    url (str): Detected YouTube URL.
                """
                nav_tabs.setActiveTab(target_mode)
                switchView(target_mode)
                if target_mode == 'single':
                    single_view.setUrl(url)
                else:
                    batch_view.setUrl(url)

            # Instantiates dynamic view controllers with auto-switch callbacks
            single_view = SingleView(on_mode_switch=handleAutoModeSwitch)
            batch_view = BatchView(on_mode_switch=handleAutoModeSwitch)

            # Render navigation tabs above the cards for seamless top-level mode switching
            nav_tabs = NavTabs(active_tab='single', on_change=switchView)
            nav_tabs.render()

            with single_container:
                single_view.render()

            with batch_container:
                batch_view.render()


@ui.page('/')
def mainPage() -> None:
    """
    Root route handler serving the TubeHarvester web application.
    """
    buildLayout()


def createApp(
    host: str = "127.0.0.1",
    port: int = 8080,
    show: bool = False,
    reload: bool = False,
) -> None:
    """
    Initializes and starts the NiceGUI web server.

    Args:
        host (str): Bind address (default: '127.0.0.1').
        port (int): Port number (default: 8080).
        show (bool): Automatically open browser window (default: False).
        reload (bool): Enable live auto-reload (default: False).
    """
    ui.run(
        title="TubeHarvester",
        favicon=str(CRAWLER_ICON),
        dark=True,
        host=host,
        port=port,
        show=show,
        reload=reload,
    )
