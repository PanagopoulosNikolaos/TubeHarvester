"""
Main NiceGUI web application bootstrap for TubeHarvester.

Constructs application layout, injects global styles, orchestrates view transitions,
and exposes the entry point runner.
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

            # Dynamic view instances
            single_view = SingleView()
            batch_view = BatchView()

            # Container placeholders for tab swapping
            single_container = ui.column().classes('w-full')
            batch_container = ui.column().classes('w-full hidden')

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
