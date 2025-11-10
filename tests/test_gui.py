import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from src.GUI import SingleDownloadPanel, BatchDownloadPanel, YouTubeDownloaderGUI


class TestSingleDownloadPanel:
    """Test SingleDownloadPanel functionality."""

    def setup_method(self):
        """Initialize Tk root and panel instance."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window for testing
        self.panel = SingleDownloadPanel(self.root)

    def teardown_method(self):
        """Destroy Tk root window."""
        if self.root:
            self.root.destroy()

    @patch('tkinter.filedialog.askdirectory')
    def test_browse_path(self, mock_askdirectory):
        """Test browse path functionality."""
        mock_askdirectory.return_value = "/test/path"

        self.panel.browse_path()

        assert self.panel.path_display.get() == "/test/path"

    @patch('src.GUI.messagebox')
    @patch('src.GUI.YouTubeDownloader')
    def test_fetch_resolutions_no_formats(self, mock_downloader_class, mock_messagebox):
        """Test fetching resolutions when no video formats found."""
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.fetch_video_info.return_value = {'formats': []}

        # Set the last checked URL so the method will execute
        self.panel.last_checked_url = "https://youtube.com/watch?v=test"
        self.panel.fetch_resolutions()

        mock_messagebox.showinfo.assert_called_with("Info", "No video resolutions found.")

    @patch('src.GUI.messagebox')
    @patch('src.GUI.YouTubeDownloader')
    def test_fetch_resolutions_error(self, mock_downloader_class, mock_messagebox):
        """Test fetching resolutions with error."""
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader
        mock_downloader.fetch_video_info.side_effect = Exception("Network error")

        # Set the last checked URL so the method will execute
        self.panel.last_checked_url = "https://youtube.com/watch?v=test"
        self.panel.fetch_resolutions()

        mock_messagebox.showerror.assert_called_with("Error", "Failed to fetch resolutions: Network error")

    @patch('src.GUI.YouTubeDownloader')
    @patch('threading.Thread')
    def test_start_download_mp4(self, mock_thread_class, mock_downloader_class):
        """Test starting MP4 download."""
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        # Set up GUI fields
        self.panel.url_entry.insert(0, "https://youtube.com/watch?v=test")
        self.panel.path_display.insert(0, "/test/path")
        self.panel.resolution_var.set("720")

        self.panel.start_download()

        # Verify downloader was configured correctly
        mock_downloader.set_url.assert_called_with("https://youtube.com/watch?v=test")
        mock_downloader.set_path.assert_called_with("/test/path")
        assert mock_downloader.resolution == 720

        # Verify thread was started
        mock_thread.start.assert_called_once()

    @patch('src.GUI.MP3Downloader')
    @patch('threading.Thread')
    def test_start_download_mp3(self, mock_thread_class, mock_mp3_downloader_class):
        """Test starting MP3 download."""
        mock_downloader = Mock()
        mock_mp3_downloader_class.return_value = mock_downloader

        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        # Set up GUI fields
        self.panel.url_entry.insert(0, "https://youtube.com/watch?v=test")
        self.panel.path_display.insert(0, "/test/path")
        self.panel.format_var.set("MP3")

        self.panel.start_download()

        # Verify MP3 downloader was created with correct parameters
        mock_mp3_downloader_class.assert_called_with("https://youtube.com/watch?v=test", "/test/path", self.panel.update_progress, self.panel.log_message)

        # Verify thread was started
        mock_thread.start.assert_called_once()

    @patch('tkinter.messagebox.showerror')
    def test_start_download_mp4_no_resolution(self, mock_messagebox):
        """Test starting MP4 download without resolution."""
        self.panel.url_entry.insert(0, "https://youtube.com/watch?v=test")
        self.panel.format_var.set("MP4")
        self.panel.resolution_var.set("")  # No resolution set

        self.panel.start_download()

        mock_messagebox.assert_called_with("Error", "Please fetch and select a resolution.")

    def test_update_progress(self):
        """Test progress update."""
        self.panel.progress['value'] = 0
        self.panel.update_progress(50)

        assert self.panel.progress['value'] == 50

    def test_clear_progress_bar(self):
        """Test clearing progress bar."""
        self.panel.progress['value'] = 50
        self.panel.clear_progress_bar()

        assert self.panel.progress['value'] == 0

    def test_log_message(self):
        """Test logging message."""
        self.panel.log_message("Test message")

        # Check that message was inserted (text widget should contain the message)
        content = self.panel.message_screen.get("1.0", tk.END).strip()
        assert "Test message" in content

    def test_update_format_color_mp4(self):
        """Test format color update for MP4."""
        self.panel.format_var.set("MP4")
        self.panel.update_format_color()

        # Resolution menu should be enabled for MP4
        assert str(self.panel.resolution_menu['state']) == 'normal'

    def test_update_format_color_mp3(self):
        """Test format color update for MP3."""
        self.panel.format_var.set("MP3")
        self.panel.update_format_color()

        # Resolution menu should be disabled for MP3
        assert str(self.panel.resolution_menu['state']) == 'disabled'


class TestBatchDownloadPanel:
    """Test BatchDownloadPanel functionality."""

    def setup_method(self):
        """Initialize Tk root and panel instance."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window for testing
        self.panel = BatchDownloadPanel(self.root)

    def teardown_method(self):
        """Destroy Tk root window."""
        if self.root:
            self.root.destroy()

    @patch('tkinter.filedialog.askdirectory')
    def test_browse_path(self, mock_askdirectory):
        """Test browse path functionality."""
        mock_askdirectory.return_value = "/test/path"

        self.panel.browse_path()

        assert self.panel.path_display.get() == "/test/path"

    def test_update_max_videos_display_playlist(self):
        """Test max videos display update for playlist mode."""
        self.panel.mode_var.set("Playlist Download")
        self.panel.update_max_videos_display()

        assert self.panel.max_videos_var.get() == "200"

    def test_update_max_videos_display_profile(self):
        """Test max videos display update for profile scrape mode."""
        self.panel.mode_var.set("Profile Scrape")
        self.panel.update_max_videos_display()

        assert self.panel.max_videos_var.get() == "ALL"

    def test_start_batch_download_no_url(self):
        """Test starting batch download without URL."""
        self.panel.start_batch_download()

        # Check that the error message was logged
        content = self.panel.message_screen.get("1.0", tk.END).strip()
        assert "Error: Please enter a URL" in content

    @patch('src.PlaylistScraper.PlaylistScraper')
    @patch('src.BatchDownloader.BatchDownloader')
    @patch('threading.Thread')
    def test_start_batch_download_playlist_mode(self, mock_thread_class, mock_batch_downloader_class, mock_playlist_scraper_class):
        """Test starting batch download in playlist mode."""
        # Mock playlist scraper
        mock_scraper = Mock()
        mock_scraper_class = Mock()
        mock_scraper_class.return_value = mock_scraper
        mock_playlist_scraper_class.return_value = mock_scraper_class

        mock_scraper.scrape_playlist.return_value = [
            {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'duration': 300}
        ]
        mock_scraper.get_playlist_title.return_value = "Test Playlist"

        # Mock batch downloader
        mock_batch_downloader = Mock()
        mock_batch_downloader_class.return_value = mock_batch_downloader
        mock_batch_downloader.download_batch.return_value = {
            'successful': 1, 'failed': 0, 'errors': []
        }

        # Mock thread
        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        # Set up GUI fields
        self.panel.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        self.panel.path_display.insert(0, "/test/path")
        self.panel.mode_var.set("Playlist Download")

        self.panel.start_batch_download()

        # Verify thread was started
        mock_thread.start.assert_called_once()

        # Verify buttons were updated
        assert str(self.panel.download_button['state']) == 'disabled'
        assert str(self.panel.cancel_button['state']) == 'normal'

    @patch('src.ChannelScraper.ChannelScraper')
    @patch('src.BatchDownloader.BatchDownloader')
    @patch('threading.Thread')
    def test_start_batch_download_profile_mode(self, mock_thread_class, mock_batch_downloader_class, mock_channel_scraper_class):
        """Test starting batch download in profile scrape mode."""
        # Mock channel scraper
        mock_scraper = Mock()
        mock_scraper_class = Mock()
        mock_scraper_class.return_value = mock_scraper
        mock_channel_scraper_class.return_value = mock_scraper_class

        mock_scraper.scrape_channel.return_value = {
            'channel_name': 'Test Channel',
            'playlists': [],
            'standalone_videos': [
                {'url': 'https://youtube.com/watch?v=1', 'title': 'Video 1', 'duration': 300}
            ]
        }

        # Mock batch downloader
        mock_batch_downloader = Mock()
        mock_batch_downloader_class.return_value = mock_batch_downloader
        mock_batch_downloader.download_batch.return_value = {
            'successful': 1, 'failed': 0, 'errors': []
        }

        # Mock thread
        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        # Set up GUI fields
        self.panel.url_entry.insert(0, "https://youtube.com/channel/test")
        self.panel.path_display.insert(0, "/test/path")
        self.panel.mode_var.set("Profile Scrape")

        self.panel.start_batch_download()

        # Verify thread was started
        mock_thread.start.assert_called_once()

    def test_cancel_download(self):
        """Test cancelling download."""
        # Mock batch downloader
        mock_batch_downloader = Mock()
        self.panel.batch_downloader = mock_batch_downloader

        self.panel.cancel_download()

        # Verify cancel was called
        mock_batch_downloader.cancel_download.assert_called_once()

        # Verify buttons were updated
        assert str(self.panel.cancel_button['state']) == 'disabled'
        assert str(self.panel.download_button['state']) == 'normal'

    def test_cancel_download_no_downloader(self):
        """Test cancelling download when no downloader exists."""
        self.panel.batch_downloader = None

        # Should not raise an exception
        self.panel.cancel_download()

    def test_log_message(self):
        """Test logging message."""
        self.panel.log_message("Test message")

        # Check that message was inserted
        content = self.panel.message_screen.get("1.0", tk.END).strip()
        assert "Test message" in content


class TestYouTubeDownloaderGUI:
    """Test YouTubeDownloaderGUI functionality."""

    def setup_method(self):
        """Initialize Tk root instance."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window for testing

    def teardown_method(self):
        """Destroy Tk root window."""
        if self.root:
            self.root.destroy()

    def test_gui_initialization(self):
        """Test GUI initialization."""
        # Create a new root for this specific test to avoid conflicts
        test_root = tk.Tk()
        test_root.withdraw()  # Hide the window
        
        gui = YouTubeDownloaderGUI(test_root)

        # Verify notebook (tabs) was created
        assert gui.notebook is not None

        # Verify tabs were created
        assert gui.single_tab is not None
        assert gui.batch_tab is not None

        # Verify panels were created
        assert gui.single_panel is not None
        assert gui.batch_panel is not None

        # Clean up
        test_root.destroy()

    @patch('tkinter.Tk')
    def test_run_gui(self, mock_tk_class):
        """Test running the GUI."""
        mock_root = Mock()
        mock_tk_class.return_value = mock_root

        # Import and call run_gui (this would normally start the event loop)
        from src.GUI import run_gui

        # We can't actually run the GUI in tests, but we can verify it creates a Tk instance
        # and calls mainloop on it
        with patch('src.GUI.YouTubeDownloaderGUI') as mock_gui_class:
            mock_gui = Mock()
            mock_gui_class.return_value = mock_gui

            # This would normally block, but we'll mock it
            with patch.object(mock_root, 'mainloop') as mock_mainloop:
                run_gui()

            mock_tk_class.assert_called_once()
            mock_gui_class.assert_called_once_with(mock_root)
            mock_mainloop.assert_called_once()
