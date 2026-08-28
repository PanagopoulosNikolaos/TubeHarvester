"""
Unit tests for NiceGUI UI components, theme utilities, and views.
"""

from unittest.mock import Mock, patch
import pytest

from src.ui.components.format_picker import FormatPicker
from src.ui.components.header import Header
from src.ui.components.log_console import LogConsole
from src.ui.components.nav_tabs import NavTabs
from src.ui.components.path_selector import PathSelector
from src.ui.components.progress import ProgressBar
from src.ui.components.url_input import UrlInput
from src.ui.theme import btnDanger, btnPrimary, btnSecondary, glassCard, injectTheme
from src.ui.views.batch_view import BatchView
from src.ui.views.single_view import SingleView


class TestTheme:
    """
    Test suite for theme helper functions and stylesheet injection.
    """

    @patch('src.ui.theme.ui.add_head_html')
    def testInjectTheme(self, mock_add_head: Mock) -> None:
        """
        Tests injecting CSS style block into NiceGUI page head.
        """
        injectTheme()
        mock_add_head.assert_called_once()
        call_arg = mock_add_head.call_args[0][0]
        assert "<style>" in call_arg
        assert "--bg-base:" in call_arg

    def testClassHelpers(self) -> None:
        """
        Tests CSS utility class helper strings.
        """
        assert glassCard() == "glass-card"
        assert btnPrimary() == "btn-primary"
        assert btnSecondary() == "btn-secondary"
        assert btnDanger() == "btn-danger"


class TestHeader:
    """
    Test suite for the Header component.
    """

    def testInit(self) -> None:
        """
        Tests Header initialization.
        """
        header = Header()
        assert header is not None


class TestNavTabs:
    """
    Test suite for the NavTabs navigation component.
    """

    def testInit(self) -> None:
        """
        Tests default active tab and callback setup.
        """
        callback = Mock()
        tabs = NavTabs(active_tab='batch', on_change=callback)
        assert tabs.active_tab == 'batch'
        assert tabs.on_change == callback

    def testHandleTabChange(self) -> None:
        """
        Tests tab change handler and callback dispatch.
        """
        callback = Mock()
        tabs = NavTabs(active_tab='single', on_change=callback)

        mock_event = Mock()
        mock_event.value = 'batch'
        tabs.handleTabChange(mock_event)

        assert tabs.active_tab == 'batch'
        callback.assert_called_with('batch')

    def testSelectTab(self) -> None:
        """
        Tests selectTab method directly.
        """
        callback = Mock()
        tabs = NavTabs(active_tab='single', on_change=callback)
        tabs.selectTab('batch')
        assert tabs.active_tab == 'batch'
        callback.assert_called_with('batch')


class TestUrlInput:
    """
    Test suite for URL input validation and error feedback.
    """

    def testInit(self) -> None:
        """
        Tests UrlInput initialization state.
        """
        url_input = UrlInput(placeholder="test_placeholder")
        assert url_input.placeholder == "test_placeholder"
        assert url_input.value == ""
        assert url_input.error_message is None

    def testValidationSingleSuccess(self) -> None:
        """
        Tests validation for single video URLs.
        """
        url_input = UrlInput()
        url_input.value = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert url_input.validate(is_batch=False) is True
        assert url_input.error_message is None

        url_input.value = "https://youtu.be/dQw4w9WgXcQ"
        assert url_input.validate(is_batch=False) is True

    def testValidationSingleFailure(self) -> None:
        """
        Tests error detection for invalid or empty single URLs.
        """
        url_input = UrlInput()
        url_input.value = ""
        assert url_input.validate(is_batch=False) is False
        assert "Please enter a URL" in url_input.error_message

        url_input.value = "https://vimeo.com/12345"
        assert url_input.validate(is_batch=False) is False
        assert "Please enter a valid YouTube URL" in url_input.error_message

    def testValidationBatchSuccess(self) -> None:
        """
        Tests validation for playlist and channel URLs.
        """
        url_input = UrlInput()
        url_input.value = "https://www.youtube.com/playlist?list=PL123"
        assert url_input.validate(is_batch=True) is True

        url_input.value = "https://www.youtube.com/@ChannelName"
        assert url_input.validate(is_batch=True) is True

    def testValidationBatchFailure(self) -> None:
        """
        Tests failure when a non-batch URL is supplied to batch validation.
        """
        url_input = UrlInput()
        url_input.value = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert url_input.validate(is_batch=True) is False
        assert "valid playlist or channel URL" in url_input.error_message

    def testSetGetError(self) -> None:
        """
        Tests manually setting and clearing errors.
        """
        url_input = UrlInput()
        url_input.setError("Custom error")
        assert url_input.error_message == "Custom error"

        url_input.clearError()
        assert url_input.error_message is None


class TestPathSelector:
    """
    Test suite for the PathSelector component.
    """

    def testInit(self) -> None:
        """
        Tests default directory assignment.
        """
        selector = PathSelector(default_path="/custom/path")
        assert selector.getValue() == "/custom/path"

    def testValidation(self) -> None:
        """
        Tests directory path validation.
        """
        selector = PathSelector()
        selector.setValue("/valid/path")
        assert selector.validate() is True

        selector.setValue("   ")
        assert selector.validate() is False
        assert "specify a download location" in selector.error_message


class TestFormatPicker:
    """
    Test suite for FormatPicker media format and quality toggling.
    """

    def testInit(self) -> None:
        """
        Tests FormatPicker initial format and resolutions.
        """
        picker = FormatPicker(default_format="MP4", default_quality="720p")
        assert picker.getFormat() == "MP4"
        assert picker.getQuality() == "720p"

    def testSetResolutions(self) -> None:
        """
        Tests updating resolution options dynamically.
        """
        picker = FormatPicker()
        picker.setResolutions(["2160p", "1440p", "1080p"])
        assert picker.resolutions == ["2160p", "1440p", "1080p"]

    def testSetFormat(self) -> None:
        """
        Tests switching format between MP4 and MP3.
        """
        callback = Mock()
        picker = FormatPicker(on_format_change=callback)
        picker.setFormat("MP3")
        assert picker.getFormat() == "MP3"
        callback.assert_called_with("MP3")


class TestProgressBar:
    """
    Test suite for the ProgressBar component.
    """

    def testInit(self) -> None:
        """
        Tests ProgressBar initial percentage and state.
        """
        progress = ProgressBar()
        assert progress.percentage == 0
        assert progress.is_visible is False

    def testSetProgress(self) -> None:
        """
        Tests setting progress values and clamping bounds.
        """
        progress = ProgressBar()
        progress.setProgress(75, "Downloading (75%)")
        assert progress.percentage == 75
        assert progress.status_text == "Downloading (75%)"
        assert progress.is_visible is True

        progress.setProgress(150)
        assert progress.percentage == 100

        progress.setProgress(-20)
        assert progress.percentage == 0

    def testReset(self) -> None:
        """
        Tests resetting progress to 0 and hiding indicator.
        """
        progress = ProgressBar()
        progress.setProgress(50)
        progress.reset()
        assert progress.percentage == 0
        assert progress.is_visible is False


class TestLogConsole:
    """
    Test suite for the LogConsole activity log component.
    """

    def testInit(self) -> None:
        """
        Tests LogConsole initialization.
        """
        console = LogConsole()
        assert len(console.entries) == 0

    def testLog(self) -> None:
        """
        Tests logging entries and timestamp formatting.
        """
        console = LogConsole()
        console.log("Download started", level="info")
        console.log("Download complete", level="success")
        console.log("Failed to connect", level="error")

        assert len(console.entries) == 3
        assert console.entries[0]['message'] == "Download started"
        assert console.entries[1]['level'] == "success"

    def testClear(self) -> None:
        """
        Tests clearing entries from the log.
        """
        console = LogConsole()
        console.log("Message 1")
        console.clear()
        assert len(console.entries) == 0


class TestViews:
    """
    Test suite for SingleView and BatchView components.
    """

    def testSingleViewInit(self) -> None:
        """
        Tests SingleView component initialization.
        """
        view = SingleView()
        assert view.is_downloading is False
        assert view.url_input is not None
        assert view.format_picker is not None

    def testBatchViewInit(self) -> None:
        """
        Tests BatchView component initialization.
        """
        view = BatchView()
        assert view.is_downloading is False
        assert view.mode_value == "playlist"
        assert view.max_videos_value == "200"

    def testBatchViewModeChange(self) -> None:
        """
        Tests mode toggle between playlist and channel in BatchView.
        """
        view = BatchView()

        mock_event = Mock()
        mock_event.value = "channel"
        view.handleModeChanged(mock_event)

        assert view.mode_value == "channel"
        assert view.max_videos_value == "ALL"
