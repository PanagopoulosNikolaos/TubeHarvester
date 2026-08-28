"""
Header component for the TubeHarvester application.

Renders the top hero banner with logo container, application title, and descriptive tagline.
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
                    # Renders download/cloud arrow icon.
                    ui.icon('download', size='28px').classes('text-white')

                ui.label('TubeHarvester').classes('hero-app-title')

            ui.label('Fast and elegant YouTube media harvester').classes('hero-app-tagline')
