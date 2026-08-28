"""
Header component for the TubeHarvester application.

Renders the top hero banner with crawler logo icon, application title, and descriptive tagline.
"""

from nicegui import ui


class Header:
    """
    Renders and manages the application hero branding header.
    """

    def __init__(self) -> None:
        """
        Initializes the Header component.
        """
        pass

    def render(self) -> None:
        """
        Builds the visual hero banner elements inside the active layout context.
        """
        with ui.element('div').classes('hero-banner'):
            with ui.element('div').classes('hero-brand'):
                with ui.element('div').classes('hero-logo-box'):
                    # Uses the crawler logo icon as the primary application face.
                    ui.image('/images/icons/crawler.png').classes('app-icon-hero')

                ui.label('TubeHarvester').classes('hero-app-title')

            ui.label('Fast and elegant YouTube media harvester').classes('hero-app-tagline')
