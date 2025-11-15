import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Text
import threading
from .Mp4_Converter import YouTubeDownloader
from .Mp3_Converter import MP3Downloader
from pathlib import Path
from .BatchDownloader import BatchDownloader
from .CookieManager import CookieManager

class SingleDownloadPanel(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.master = parent
        self.colors = colors
        self.downloader = None
        self.default_download_path = str(Path.home() / "Downloads")
        self.build_gui()

    def build_gui(self):
        # main frame for the single download panel
        main_frame = ttk.Frame(self.master, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # url and path frame - contains input fields for URL and download path
        url_path_frame = ttk.LabelFrame(main_frame, text="Input", padding="10 10 10 10")
        url_path_frame.pack(fill=tk.X, pady=5)
        
        # url input field configuration
        ttk.Label(url_path_frame, text="YouTube URL:").grid(row=0, column=0, sticky="w", pady=2)
        self.url_entry = ttk.Entry(url_path_frame, width=60)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)

        # download path input field with browse button
        ttk.Label(url_path_frame, text="Download Path:").grid(row=1, column=0, sticky="w", pady=2)
        self.path_display = ttk.Entry(url_path_frame, width=50)
        self.path_display.grid(row=1, column=1, sticky="ew", pady=2)
        self.browse_button = ttk.Button(url_path_frame, text="Browse", command=self.browse_path)
        self.browse_button.grid(row=1, column=2, sticky="e", padx=5, pady=2)
        
        url_path_frame.columnconfigure(1, weight=1)

        # options frame - contains format and resolution selection
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10 10 10 10")
        options_frame.pack(fill=tk.X, pady=5)

        # format selection radio buttons (MP4/MP3)
        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky="w")
        self.format_var = tk.StringVar(value="MP4")
        self.mp4_radio = ttk.Radiobutton(options_frame, text="MP4", variable=self.format_var, value="MP4", command=self.update_format_color)
        self.mp4_radio.grid(row=0, column=1, sticky='w', padx=5)
        self.mp3_radio = ttk.Radiobutton(options_frame, text="MP3", variable=self.format_var, value="MP3", command=self.update_format_color)
        self.mp3_radio.grid(row=0, column=2, sticky='w', padx=5)

        # resolution selection dropdown menu
        ttk.Label(options_frame, text="Resolution:").grid(row=1, column=0, sticky="w")
        self.resolution_var = tk.StringVar(self.master)
        self.resolution_menu = ttk.OptionMenu(options_frame, self.resolution_var, "Highest")
        self.resolution_menu.grid(row=1, column=1, columnspan=2, sticky="w", pady=5)

        # controls frame - contains the main action button
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        # download button configuration
        self.download_button = ttk.Button(controls_frame, text="Download", command=self.start_download)
        self.download_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # removed close button as it's redundant with the window's X button

        # progress and log frame - contains progress bars and status messages
        progress_log_frame = ttk.LabelFrame(main_frame, text="Status", padding="10 10 10 10")
        progress_log_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        # fetching data progress bar - shows progress when fetching video data
        self.fetch_progress_frame = ttk.Frame(progress_log_frame)
        self.fetch_progress_frame.pack(fill=tk.X, pady=5)
        
        self.fetch_label = ttk.Label(self.fetch_progress_frame, text="Fetching Data:", font=('Courier', 9, 'bold'))
        self.fetch_label.pack(anchor='w')
        
        self.fetch_progress = ttk.Progressbar(self.fetch_progress_frame, orient='horizontal', length=400, mode='determinate')
        self.fetch_progress.pack(fill=tk.X, pady=2)
        
        self.fetch_status_label = ttk.Label(self.fetch_progress_frame, text="", font=('Courier', 9))
        self.fetch_status_label.pack(anchor='w')
        
        # hide fetch progress initially
        self.fetch_progress_frame.pack_forget()

        # download progress bar - shows progress during the actual download
        self.download_progress_frame = ttk.Frame(progress_log_frame)
        self.download_progress_frame.pack(fill=tk.X, pady=5)
        
        self.download_label = ttk.Label(self.download_progress_frame, text="Download Progress:", font=('Courier', 9, 'bold'))
        self.download_label.pack(anchor='w')
        
        self.progress = ttk.Progressbar(self.download_progress_frame, orient='horizontal', length=40, mode='determinate')
        self.progress.pack(fill=tk.X, pady=2)
        
        # hide download progress initially
        self.download_progress_frame.pack_forget()

        # message log display area - shows status messages and errors
        self.message_screen = Text(progress_log_frame, height=10, width=75, font=('Courier', 9), 
                                   fg=self.colors["FOREGROUND_COLOR"], bg=self.colors["SECONDARY_BACKGROUND_COLOR"], insertbackground=self.colors["ACCENT_COLOR"],
                                   borderwidth=0, highlightthickness=1, highlightbackground=self.colors["ACCENT_COLOR"],
                                   selectbackground=self.colors["ACCENT_COLOR_DARK"], selectforeground=self.colors["FOREGROUND_COLOR"])
        self.message_screen.pack(expand=True, fill=tk.BOTH, pady=5)
        self.message_screen.config(state=tk.DISABLED)

        self.update_format_color()
        self.last_checked_url = ""
        self.master.after(1000, self.auto_fetch_resolutions)

    def auto_fetch_resolutions(self):
        current_url = self.url_entry.get()
        if current_url and current_url != self.last_checked_url:
            self.last_checked_url = current_url
            # run fetching in a separate thread to not block the GUI
            threading.Thread(target=self.fetch_resolutions, daemon=True).start()
        self.master.after(1000, self.auto_fetch_resolutions) # check again in 1 second

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_display.delete(0, tk.END)
            self.path_display.insert(0, path)

    def fetch_resolutions(self):
        url = self.last_checked_url # use the last checked URL
        if not url:
            return # silently return if no URL

        try:
            downloader = YouTubeDownloader(log_callback=self.log_message)
            downloader.set_url(url)
            info = downloader.fetch_video_info()
            formats = info.get('formats', [])
            resolutions = sorted(list(set([f['height'] for f in formats if f.get('height') and f.get('vcodec') != 'none'])), reverse=True)
            
            if not resolutions:
                messagebox.showinfo("Info", "No video resolutions found.")
                return

            self.resolution_var.set(resolutions[0]) # default to highest
            menu = self.resolution_menu['menu']
            menu.delete(0, 'end')
            for res in resolutions:
                menu.add_command(label=f"{res}p", command=lambda value=res: self.resolution_var.set(value))
            
            self.log_message("Resolutions fetched successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch resolutions: {e}")

    def start_download(self):
        self.progress['value'] = 0
        self.progress.update()

        url = self.url_entry.get()
        path = self.path_display.get() or self.default_download_path

        if self.format_var.get() == "MP4":
            resolution = self.resolution_var.get()
            if not resolution:
                messagebox.showerror("Error", "Please fetch and select a resolution.")
                return
            self.downloader = YouTubeDownloader(self.update_progress, self.log_message)
            self.downloader.set_url(url)
            self.downloader.set_path(path)
            self.downloader.resolution = int(resolution)
            download_thread = threading.Thread(target=self.downloader.download_video)
        elif self.format_var.get() == "MP3":
            self.downloader = MP3Downloader(url, path, self.update_progress, self.log_message)
            download_thread = threading.Thread(target=self.downloader.download_as_mp3)
        download_thread.start()

    def update_progress(self, percentage):
        self.progress['value'] = percentage
        self.progress.update()
        if percentage == 100:
            self.master.after(3000, self.clear_progress_bar)

    def clear_progress_bar(self):
        self.progress['value'] = 0
        self.progress.update()

    def log_message(self, message):
        self.message_screen.config(state=tk.NORMAL)
        self.message_screen.insert(tk.END, message + "\n")
        self.message_screen.see(tk.END)
        self.message_screen.config(state=tk.DISABLED)

    def update_format_color(self):
        # this can be expanded to disable/enable the resolution dropdown
        is_mp4 = self.format_var.get() == "MP4"
        self.resolution_menu.config(state=tk.NORMAL if is_mp4 else tk.DISABLED)

class BatchDownloadPanel(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.master = parent
        self.colors = colors
        self.build_gui()
        self._display_startup_info()

    def build_gui(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # URL and Path Frame
        url_path_frame = ttk.LabelFrame(main_frame, text="Input", padding="10 10 10 10")
        url_path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(url_path_frame, text="Playlist/Channel URL:").grid(row=0, column=0, sticky="w", pady=2)
        self.url_entry = ttk.Entry(url_path_frame, width=60)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)

        ttk.Label(url_path_frame, text="Base Path:").grid(row=1, column=0, sticky="w", pady=2)
        self.path_display = ttk.Entry(url_path_frame, width=50)
        self.path_display.grid(row=1, column=1, sticky="ew", pady=2)
        self.browse_button = ttk.Button(url_path_frame, text="Browse", command=self.browse_path)
        self.browse_button.grid(row=1, column=2, sticky="e", padx=5, pady=2)

        url_path_frame.columnconfigure(1, weight=1)

        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10 10 10 10")
        options_frame.pack(fill=tk.X, pady=5)

        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky="w")
        self.format_var = tk.StringVar(value="MP4")
        self.mp4_radio = ttk.Radiobutton(options_frame, text="MP4", variable=self.format_var, value="MP4", command=self.update_format_color)
        self.mp4_radio.grid(row=0, column=1, sticky='w', padx=5)
        self.mp3_radio = ttk.Radiobutton(options_frame, text="MP3", variable=self.format_var, value="MP3", command=self.update_format_color)
        self.mp3_radio.grid(row=0, column=2, sticky='w', padx=5)

        ttk.Label(options_frame, text="Quality:").grid(row=1, column=0, sticky="w")
        self.quality_var = tk.StringVar(value="Highest")
        self.quality_menu = ttk.OptionMenu(options_frame, self.quality_var, "Highest")
        self.quality_menu.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(options_frame, text="Max Videos:").grid(row=2, column=0, sticky="w")
        self.max_videos_var = tk.StringVar(value="200")
        self.max_videos_entry = ttk.Entry(options_frame, textvariable=self.max_videos_var, width=10)
        self.max_videos_entry.grid(row=2, column=1, sticky="w", pady=5)

        ttk.Label(options_frame, text="Mode:").grid(row=3, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="Playlist Download")
        self.playlist_radio = ttk.Radiobutton(options_frame, text="Playlist Download", variable=self.mode_var, value="Playlist Download")
        self.playlist_radio.grid(row=3, column=1, sticky='w', padx=5)
        self.profile_radio = ttk.Radiobutton(options_frame, text="Profile Scrape", variable=self.mode_var, value="Profile Scrape")
        self.profile_radio.grid(row=3, column=2, sticky='w', padx=5)

        # Add trace to update Max Videos field when mode changes
        self.mode_var.trace_add("write", self.update_max_videos_display)

        # Controls Frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        self.download_button = ttk.Button(controls_frame, text="Start Batch Download", command=self.start_batch_download)
        self.download_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.cancel_button = ttk.Button(controls_frame, text="Cancel", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Progress and Log Frame
        progress_log_frame = ttk.LabelFrame(main_frame, text="Status", padding="10 10 10 10")
        progress_log_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        # Fetching Data Progress Bar
        self.fetch_progress_frame = ttk.Frame(progress_log_frame)
        self.fetch_progress_frame.pack(fill=tk.X, pady=5)
        
        self.fetch_label = ttk.Label(self.fetch_progress_frame, text="Fetching Data:", font=('Courier', 9, 'bold'))
        self.fetch_label.pack(anchor='w')
        
        self.fetch_progress = ttk.Progressbar(self.fetch_progress_frame, orient='horizontal', length=400, mode='determinate')
        self.fetch_progress.pack(fill=tk.X, pady=2)
        
        self.fetch_status_label = ttk.Label(self.fetch_progress_frame, text="", font=('Courier', 9))
        self.fetch_status_label.pack(anchor='w')
        
        # Hide fetch progress initially
        self.fetch_progress_frame.pack_forget()

        # Download Progress Bar
        self.download_progress_frame = ttk.Frame(progress_log_frame)
        self.download_progress_frame.pack(fill=tk.X, pady=5)
        
        self.download_label = ttk.Label(self.download_progress_frame, text="Download Progress:", font=('Courier', 9, 'bold'))
        self.download_label.pack(anchor='w')
        
        self.progress = ttk.Progressbar(self.download_progress_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(fill=tk.X, pady=2)
        
        # Hide download progress initially
        self.download_progress_frame.pack_forget()

        self.message_screen = Text(progress_log_frame, height=10, width=75, font=('Courier', 9), 
                                   fg=self.colors["FOREGROUND_COLOR"], bg=self.colors["SECONDARY_BACKGROUND_COLOR"], insertbackground=self.colors["ACCENT_COLOR"],
                                   borderwidth=0, highlightthickness=1, highlightbackground=self.colors["ACCENT_COLOR"],
                                   selectbackground=self.colors["ACCENT_COLOR_DARK"], selectforeground=self.colors["FOREGROUND_COLOR"])
        self.message_screen.pack(expand=True, fill=tk.BOTH, pady=5)
        self.message_screen.config(state=tk.DISABLED)

        self.update_format_color()

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_display.delete(0, tk.END)
            self.path_display.insert(0, path)

    def update_format_color(self):
        # this can be expanded to disable/enable the quality dropdown
        pass

    def update_max_videos_display(self, *args):
        """Update the Max Videos field based on selected mode."""
        if self.mode_var.get() == "Profile Scrape":
            self.max_videos_var.set("ALL")
        else:
            # reset to default value when switching back to Playlist Download
            self.max_videos_var.set("200")

    def start_batch_download(self):
        """Start batch download based on selected mode."""
        url = self.url_entry.get().strip()
        base_path = self.path_display.get().strip() or os.path.expanduser('~')
        format_type = self.format_var.get()
        quality = self.quality_var.get()
        max_videos_str = self.max_videos_var.get()
        mode = self.mode_var.get()

        # handle "ALL" value for Profile Scrape mode
        if max_videos_str == "ALL":
            max_videos = 10000  # use high limit for unlimited
        else:
            max_videos = int(max_videos_str)

        if not url:
            self.log_message("Error: Please enter a URL")
            return

        # disable start button and enable cancel button
        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

        # clear previous progress
        self.progress['value'] = 0

        # start download in separate thread
        download_thread = threading.Thread(
            target=self._execute_batch_download,
            args=(url, base_path, format_type, quality, max_videos, mode),
            daemon=True
        )
        download_thread.start()

    def cancel_download(self):
        """Cancel the ongoing batch download."""
        if hasattr(self, 'batch_downloader') and self.batch_downloader:
            self.batch_downloader.cancel_download()
            self.cancel_button.config(state=tk.DISABLED)
            self.download_button.config(state=tk.NORMAL)

    def _execute_batch_download(self, url, base_path, format_type, quality, max_videos, mode):
        """Execute the batch download process."""
        try:
            self.batch_downloader = None

            # show fetch progress bar
            self.fetch_progress_frame.pack(fill=tk.X, pady=5)
            self.fetch_progress['value'] = 0
            self.fetch_status_label.config(text="")

            if mode == "Playlist Download":
                # scrape playlist
                self.log_message(f"Scraping playlist: {url}")
                from .PlaylistScraper import PlaylistScraper
                scraper = PlaylistScraper(timeout=2.0)
                
                # create progress callback for fetching
                def fetch_progress_callback(current, total, percentage):
                    self._update_fetch_progress(current, total, percentage)
                
                videos = scraper.scrape_playlist(url, max_videos, fetch_progress_callback)

                if not videos:
                    self.log_message("No videos found in playlist")
                    return

                self.log_message(f"Found {len(videos)} videos in playlist")

                # prepare video list for batch download
                video_list = []
                playlist_title = scraper.get_playlist_title(url)
                for video in videos:
                    video_list.append({
                        'url': video['url'],
                        'title': video['title'],
                        'folder': f"Playlists/{playlist_title}"  # generic folder for playlist downloads
                    })

            elif mode == "Profile Scrape":
                # scrape channel - no limit for profile scraping (get all videos)
                self.log_message(f"Scraping channel: {url} (unlimited videos)")
                from .ChannelScraper import ChannelScraper
                scraper = ChannelScraper(timeout=2.0)
                
                # create progress callback for fetching
                def fetch_progress_callback(current, total, percentage):
                    self._update_fetch_progress(current, total, percentage)
                
                # use a very high limit for profile scraping to get all videos
                channel_info = scraper.scrape_channel(url, 1000, fetch_progress_callback)  # 10k should be enough for most channels

                if not channel_info['playlists'] and not channel_info['standalone_videos']:
                    self.log_message("No content found in channel")
                    return

                self.log_message(f"Found {len(channel_info['playlists'])} playlists and {len(channel_info['standalone_videos'])} standalone videos")

                # prepare video list for batch download
                video_list = []
                channel_name = channel_info['channel_name']

                # add videos from playlists
                for playlist in channel_info['playlists']:
                    for video in playlist['videos']:
                        video_list.append({
                            'url': video['url'],
                            'title': video['title'],
                            'folder': f"{channel_name}/{playlist['title']}"
                        })

                # add standalone videos
                for video in channel_info['standalone_videos']:
                    video_list.append({
                        'url': video['url'],
                        'title': video['title'],
                        'folder': f"{channel_name}/Random"
                    })

            # hide fetch progress bar and show download progress bar
            self.fetch_progress_frame.pack_forget()
            self.download_progress_frame.pack(fill=tk.X, pady=5)
            self.log_message("Data fetching complete. Starting downloads...")

            # start batch download
            self.batch_downloader = BatchDownloader(
                max_workers=3,
                progress_callback=self._update_progress,
                log_callback=self.log_message
            )

            results = self.batch_downloader.download_batch(
                video_list, format_type, base_path, quality
            )

            # show final results
            self.log_message(f"Batch download completed: {results['successful']} successful, {results['failed']} failed")
            if results['errors']:
                self.log_message("Errors encountered:")
                for error in results['errors'][:5]:  # show first 5 errors
                    self.log_message(f"  - {error}")
                if len(results['errors']) > 5:
                    self.log_message(f"  ... and {len(results['errors']) - 5} more errors")

        except Exception as e:
            self.log_message(f"Error during batch download: {str(e)}")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}")

        finally:
            # hide both progress bars
            self.fetch_progress_frame.pack_forget()
            self.download_progress_frame.pack_forget()
            
            # re-enable buttons
            self.download_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.batch_downloader = None

    def _update_fetch_progress(self, current, total, percentage):
        """Update the fetch progress bar with ASCII-style visual."""
        # update progress bar
        self.fetch_progress['value'] = percentage
        
        # create ASCII-style progress bar
        bar_width = 20
        filled = int((percentage / 100) * bar_width)
        bar = '=' * filled + '>' + ' ' * (bar_width - filled - 1)
        
        # update status label with ASCII bar and stats
        status_text = f"[{bar}] {percentage}% ({current}/{total} items)"
        self.fetch_status_label.config(text=status_text)
        
        # force GUI update
        self.fetch_progress.update()
        self.fetch_status_label.update()

    def _update_progress(self, percentage):
        """Update the download progress bar."""
        self.progress['value'] = percentage
        self.progress.update()

    def log_message(self, message):
        self.message_screen.config(state=tk.NORMAL)
        self.message_screen.insert(tk.END, message + "\n")
        self.message_screen.see(tk.END)
        self.message_screen.config(state=tk.DISABLED)

    def _display_startup_info(self):
        """Display startup configuration information."""
        import platform
        home_dir = os.path.expanduser('~')
        
        info_lines = [
            "=" * 60,
            "TubeHarvester - Batch Download Configuration",
            "=" * 60,
            f"System: {platform.system()} {platform.release()}",
            f"Home Directory: {home_dir}",
            f"Default Base Path: {home_dir}",
            "",
            "Default Settings:",
            f"  Format: {self.format_var.get()}",
            f" Quality: {self.quality_var.get()}",
            f"  Max Videos: {self.max_videos_var.get()}",
            f" Mode: {self.mode_var.get()}",
            "",
            "Output Structure:",
            " MP3: ~/Music/<Source>/<Playlist or Random>/",
            "  MP4: ~/Videos/<Source>/<Playlist or Random>/",
            "",
            "Ready to download. Enter a playlist or channel URL to begin.",
            "=" * 60,
            ""
        ]
        
        for line in info_lines:
            self.log_message(line)

class YouTubeDownloaderGUI:
    def __init__(self, master):
        self.master = master
        self.master.title('TubeHarvester - YouTube Downloader')
        self.master.geometry("750x750")
        self.master.resizable(True, True)

        # GitHub Dark Dimmed color palette
        self.colors = {
            "BACKGROUND_COLOR": "#22272e",
            "SECONDARY_BACKGROUND_COLOR": "#2d333b",
            "TERTIARY_BACKGROUND_COLOR": "#323842",
            "FOREGROUND_COLOR": "#adbac7",
            "TEXT_SECONDARY_COLOR": "#768390",
            "ACCENT_COLOR": "#58a6ff",
            "ACCENT_COLOR_DARK": "#4883c8",
            "BORDER_COLOR": "#444c56",
            "TEXT_INACTIVE_COLOR": "#768390",
        }

        # Set dark background for root window
        self.master.configure(bg=self.colors["BACKGROUND_COLOR"])

        # Style configuration
        style = ttk.Style(self.master)
        style.theme_use('clam')

        # Configure Notebook (tabs)
        style.configure("TNotebook",
                        background=self.colors["BACKGROUND_COLOR"],
                        borderwidth=0,
                        tabmargins=[0, 0, 0, 0])

        # Tab styling
        style.configure("TNotebook.Tab",
                        background=self.colors["SECONDARY_BACKGROUND_COLOR"],
                        foreground=self.colors["TEXT_INACTIVE_COLOR"],
                        borderwidth=0,
                        padding=[30, 12],
                        font=('Helvetica', 10, 'normal'))

        style.map("TNotebook.Tab",
                  background=[("selected", self.colors["TERTIARY_BACKGROUND_COLOR"]), ("!selected", self.colors["SECONDARY_BACKGROUND_COLOR"])],
                  foreground=[("selected", self.colors["ACCENT_COLOR"]), ("!selected", self.colors["TEXT_INACTIVE_COLOR"])],
                  expand=[("selected", [0, 0, 0, 0])],
                  padding=[("selected", [30, 12]), ("!selected", [30, 12])])

        # Frame styling
        style.configure("TFrame", background=self.colors["BACKGROUND_COLOR"], borderwidth=0)

        # LabelFrame styling
        style.configure("TLabelframe",
                        background=self.colors["BACKGROUND_COLOR"],
                        bordercolor=self.colors["ACCENT_COLOR"],
                        borderwidth=1,
                        relief='solid')
        style.configure("TLabelframe.Label",
                        background=self.colors["BACKGROUND_COLOR"],
                        foreground=self.colors["ACCENT_COLOR"],
                        font=('Helvetica', 10, 'bold'))

        # Label styling
        style.configure("TLabel",
                        background=self.colors["BACKGROUND_COLOR"],
                        foreground=self.colors["FOREGROUND_COLOR"],
                        padding=6,
                        font=('Helvetica', 10))

        # Entry styling
        style.configure("TEntry",
                        fieldbackground=self.colors["SECONDARY_BACKGROUND_COLOR"],
                        foreground=self.colors["FOREGROUND_COLOR"],
                        bordercolor=self.colors["BORDER_COLOR"],
                        lightcolor=self.colors["BORDER_COLOR"],
                        darkcolor=self.colors["BORDER_COLOR"],
                        borderwidth=1,
                        insertcolor=self.colors["ACCENT_COLOR"])
        style.map("TEntry",
                  fieldbackground=[("focus", self.colors["TERTIARY_BACKGROUND_COLOR"])],
                  bordercolor=[("focus", self.colors["ACCENT_COLOR"])])

        # Button styling
        style.configure("TButton",
                        background=self.colors["SECONDARY_BACKGROUND_COLOR"],
                        foreground=self.colors["FOREGROUND_COLOR"],
                        bordercolor=self.colors["ACCENT_COLOR"],
                        lightcolor=self.colors["ACCENT_COLOR"],
                        darkcolor=self.colors["ACCENT_COLOR"],
                        borderwidth=1,
                        padding=6,
                        font=('Helvetica', 10))
        style.map("TButton",
                  background=[("active", self.colors["TERTIARY_BACKGROUND_COLOR"]), ("pressed", self.colors["ACCENT_COLOR_DARK"])],
                  foreground=[("active", self.colors["ACCENT_COLOR"])],
                  bordercolor=[("focus", self.colors["ACCENT_COLOR"])])

        # Radiobutton styling
        style.configure("TRadiobutton",
                        background=self.colors["BACKGROUND_COLOR"],
                        foreground=self.colors["FOREGROUND_COLOR"],
                        bordercolor=self.colors["BORDER_COLOR"],
                        font=('Helvetica', 10))
        style.map("TRadiobutton",
                  background=[("active", self.colors["BACKGROUND_COLOR"])],
                  foreground=[("active", self.colors["ACCENT_COLOR"])])

        # Menubutton (OptionMenu) styling
        style.configure("TMenubutton",
                        background=self.colors["SECONDARY_BACKGROUND_COLOR"],
                        foreground=self.colors["FOREGROUND_COLOR"],
                        bordercolor=self.colors["ACCENT_COLOR"],
                        borderwidth=1,
                        padding=6,
                        font=('Helvetica', 10))
        style.map("TMenubutton",
                  background=[("active", self.colors["TERTIARY_BACKGROUND_COLOR"])],
                  foreground=[("active", self.colors["ACCENT_COLOR"])])

        # Progressbar styling
        style.configure("TProgressbar",
                        troughcolor=self.colors["SECONDARY_BACKGROUND_COLOR"],
                        background=self.colors["ACCENT_COLOR"],
                        bordercolor=self.colors["ACCENT_COLOR"],
                        lightcolor=self.colors["ACCENT_COLOR"],
                        darkcolor=self.colors["ACCENT_COLOR"],
                        borderwidth=1)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Single download tab
        self.single_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.single_tab, text="Single Download")

        # Single download panel
        self.single_panel = SingleDownloadPanel(self.single_tab, colors=self.colors)
        self.single_panel.pack(expand=True, fill=tk.BOTH)

        # Batch download tab
        self.batch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_tab, text="Batch Download")

        # Batch download panel
        self.batch_panel = BatchDownloadPanel(self.batch_tab, colors=self.colors)
        self.batch_panel.pack(expand=True, fill=tk.BOTH)

def run_gui():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
