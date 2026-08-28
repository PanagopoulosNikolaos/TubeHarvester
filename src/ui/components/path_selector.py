"""
Path selector component for destination folder configuration.

Provides an editable path display, directory picker modal with full-width presets,
and custom path input capabilities.
"""

import os
from typing import Callable, Optional
from nicegui import ui


class PathSelector:
    """
    Renders and manages the destination download folder selector.
    """

    def __init__(
        self,
        default_path: Optional[str] = None,
        on_change: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initializes the PathSelector component.

        Args:
            default_path (Optional[str], optional): Starting directory path. Defaults to system Downloads.
            on_change (Optional[Callable[[str], None]], optional): Callback triggered on path update.
        """
        home_dir = os.path.expanduser('~')
        self.default_path = default_path or os.path.join(home_dir, 'Downloads')
        self.value: str = self.default_path
        self.on_change = on_change
        self.error_message: Optional[str] = None

        self.is_custom: bool = False
        self.input_element: Optional[ui.input] = None
        self.error_label: Optional[ui.label] = None
        self.browse_dialog: Optional[ui.dialog] = None

    def render(self) -> None:
        """
        Builds the destination path selector UI.
        """
        with ui.column().classes('w-full gap-1'):
            ui.label('Download Location').classes('field-label')

            with ui.row().classes('w-full items-center gap-2'):
                self.input_element = ui.input(
                    value=self.value,
                    on_change=self.handleInputChanged,
                ).props('outlined dense').classes('glass-input flex-1')

                self.input_element.on('blur', self.handleBlur)

                ui.button(
                    'Browse',
                    on_click=self.openBrowseDialog,
                ).props('flat no-caps').classes('btn-secondary px-4')

            self.error_label = ui.label('').classes('input-error-msg hidden')

    def handleInputChanged(self, e: object) -> None:
        """
        Handles manual path edits from the input field.

        Args:
            e (object): Input event carrying the updated path.
        """
        new_val = getattr(e, 'value', '') or ''
        self.value = str(new_val).strip()
        self.is_custom = not self.isStandardPreset(self.value)

        if self.error_message:
            self.clearError()

        if self.on_change:
            self.on_change(self.value)

    def handleBlur(self) -> None:
        """
        Validates path validity when focus leaves the input field.
        """
        if self.value:
            self.validate()

    def validate(self) -> bool:
        """
        Checks whether the specified folder path string is non-empty.

        Returns:
            bool: True if path is valid, False otherwise.
        """
        if not self.value.strip():
            self.setError("Please specify a download location.")
            return False

        self.clearError()
        return True

    def isStandardPreset(self, path_str: str) -> bool:
        """
        Checks whether the given path string corresponds to a standard preset directory.

        Args:
            path_str (str): Target directory path.

        Returns:
            bool: True if path matches a known standard preset, False otherwise.
        """
        home_dir = os.path.expanduser('~')
        standard_paths = {
            os.path.normpath(os.path.join(home_dir, "Downloads")),
            os.path.normpath(os.path.join(home_dir, "Videos")),
            os.path.normpath(os.path.join(home_dir, "Music")),
            os.path.normpath(os.path.join(home_dir, "Desktop")),
            os.path.normpath(os.path.join(home_dir, "Documents")),
        }
        return os.path.normpath(path_str.strip()) in standard_paths

    def isCustom(self) -> bool:
        """
        Determines whether the currently selected path is a custom user directory.

        Returns:
            bool: True if custom path, False if standard preset.
        """
        if self.is_custom:
            return True
        return not self.isStandardPreset(self.value)

    def selectPreset(self, path: str, dialog: ui.dialog) -> None:
        """
        Selects a standard destination preset and closes the modal.

        Args:
            path (str): Selected directory path.
            dialog (ui.dialog): Parent directory picker modal.
        """
        self.is_custom = False
        self.setValue(path)
        dialog.close()

    def openBrowseDialog(self) -> None:
        """
        Opens a directory picker modal dialog with full-width clickable preset buttons and custom path entry.
        """
        home_dir = os.path.expanduser('~')
        presets = [
            ("Downloads", os.path.join(home_dir, "Downloads")),
            ("Videos", os.path.join(home_dir, "Videos")),
            ("Music", os.path.join(home_dir, "Music")),
            ("Desktop", os.path.join(home_dir, "Desktop")),
            ("Documents", os.path.join(home_dir, "Documents")),
        ]

        with ui.dialog() as dialog, ui.card().classes('glass-card min-w-[340px] max-w-[460px] p-6'):
            ui.label('Select Download Directory').classes('text-lg font-bold text-white mb-1')
            ui.label('Choose a standard destination folder or enter a custom path:').classes('text-xs text-stone-300 mb-3')

            # Presets list with fully clickable row buttons
            with ui.column().classes('w-full gap-2 mb-4'):
                for name, path in presets:
                    preset_row = ui.element('div').classes('preset-row')
                    preset_row.on('click', lambda _, p=path: self.selectPreset(p, dialog))
                    with preset_row:
                        with ui.column().classes('gap-0'):
                            ui.label(name).classes('text-sm font-semibold text-white')
                            ui.label(path).classes('text-xs text-stone-400')

            # Custom path input section
            ui.label('Custom Directory Path:').classes('text-xs font-semibold text-stone-300 mb-1')
            custom_input = ui.input(
                placeholder=home_dir,
                value=self.value,
            ).props('outlined dense').classes('glass-input w-full mb-4')

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Close', on_click=dialog.close).props('flat no-caps').classes('btn-secondary px-4')

                def applyCustom() -> None:
                    target_val = custom_input.value.strip()
                    if target_val:
                        self.is_custom = True
                        self.setValue(target_val)
                    dialog.close()

                ui.button('Apply Path', on_click=applyCustom).props('flat no-caps').classes('btn-primary px-4')

        dialog.open()

    def setError(self, msg: str) -> None:
        """
        Renders error text below the path selector.

        Args:
            msg (str): Error message string.
        """
        self.error_message = msg
        if self.error_label:
            self.error_label.text = msg
            self.error_label.classes(remove='hidden')

    def clearError(self) -> None:
        """
        Hides the path error message.
        """
        self.error_message = None
        if self.error_label:
            self.error_label.text = ''
            self.error_label.classes(add='hidden')

    def getValue(self) -> str:
        """
        Retrieves current download path.

        Returns:
            str: Destination path string.
        """
        return self.value

    def setValue(self, val: str) -> None:
        """
        Updates the path value and syncs the input element.

        Args:
            val (str): New directory path.
        """
        self.value = val
        if self.input_element:
            self.input_element.value = val
        if self.on_change:
            self.on_change(val)
