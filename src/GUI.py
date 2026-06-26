import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Text
import threading
from .Mp4_Converter import Mp4Downloader
from .Mp3_Converter import Mp3Downloader
from pathlib import Path
from .BatchDownloader import BatchDownloader
from .CookieManager import CookieManager
from .utils import sanitizeFilename


class SingleDownloadPanel(ttk.Frame):
    """
    Panel for individual video downloads.

    Provides a GUI for entering a YouTube URL, selecting format and resolution,
    and tracking the download progress.
    """

    def __init__(self, parent, colors):
        """
        Initializes the SingleDownloadPanel.

        Args:
            parent: The parent widget.
            colors (dict): Theme color palette.
        """
        super().__init__(parent)
        self.master = parent
        self.colors = colors
        self.downloader = None
        self.default_download_path = str(Path.home() / "Downloads")
        self.buildGui()

    def buildGui(self):
        """
        Constructs the GUI components for the single download panel.
        Refined soft layout with generous spacing.
        """
        # Main container
        main = ttk.Frame(self.master, padding="16 14 16 12")
        main.pack(expand=True, fill=tk.BOTH)

        # ---- URL Section ----
        ttk.Label(main, text="VIDEO URL", style="SectionHeader.TLabel").pack(anchor="w", padx=2)
        url_frame = ttk.Frame(main)
        url_frame.pack(fill=tk.X, pady=(0, 10))

        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(fill=tk.X, ipady=4)

        # ---- Path Section ----
        ttk.Label(main, text="DOWNLOAD LOCATION", style="SectionHeader.TLabel").pack(anchor="w", padx=2)
        path_frame = ttk.Frame(main)
        path_frame.pack(fill=tk.X, pady=(0, 12))

        self.path_display = ttk.Entry(path_frame)
        self.path_display.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self.path_display.insert(0, self.default_download_path)

        self.browse_button = ttk.Button(path_frame, text="Browse", command=self.browsePath, style="Ghost.TButton")
        self.browse_button.pack(side=tk.RIGHT, padx=(8, 0))

        # ---- Options Section ----
        ttk.Label(main, text="OPTIONS", style="SectionHeader.TLabel").pack(anchor="w", padx=2)
        opt_frame = ttk.Frame(main)
        opt_frame.pack(fill=tk.X, pady=(0, 14))

        # Format
        ttk.Label(opt_frame, text="Format").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=4)

        self.format_var = tk.StringVar(value="MP4")
        fmt_row = ttk.Frame(opt_frame)
        fmt_row.grid(row=0, column=1, sticky="w", pady=4)

        self.mp4_radio = ttk.Radiobutton(fmt_row, text="MP4  (video)", variable=self.format_var,
                                         value="MP4", command=self.updateFormatColor)
        self.mp4_radio.pack(side=tk.LEFT, padx=(0, 14))
        self.mp3_radio = ttk.Radiobutton(fmt_row, text="MP3  (audio)", variable=self.format_var,
                                         value="MP3", command=self.updateFormatColor)
        self.mp3_radio.pack(side=tk.LEFT)

        # Resolution / Quality
        ttk.Label(opt_frame, text="Quality").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=4)
        self.resolution_var = tk.StringVar(value="Highest")
        self.resolution_menu = ttk.OptionMenu(opt_frame, self.resolution_var, "Highest")
        self.resolution_menu.grid(row=1, column=1, sticky="w", pady=2)

        opt_frame.columnconfigure(1, weight=1)

        # ---- Primary Action ----
        controls = ttk.Frame(main)
        controls.pack(fill=tk.X, pady=(4, 10))

        self.download_button = ttk.Button(controls, text="⬇  Download", command=self.startDownload,
                                          style="Primary.TButton")
        self.download_button.pack(fill=tk.X, ipady=3)

        # ---- Progress + Status ----
        status_wrap = ttk.Frame(main)
        status_wrap.pack(expand=True, fill=tk.BOTH, pady=(4, 0))

        # Fetch progress (hidden by default)
        self.fetch_progress_frame = ttk.Frame(status_wrap)
        ttk.Label(self.fetch_progress_frame, text="Fetching metadata…", style="Muted.TLabel").pack(anchor="w")
        self.fetch_progress = ttk.Progressbar(self.fetch_progress_frame, mode='determinate', length=300)
        self.fetch_progress.pack(fill=tk.X, pady=(3, 2))
        self.fetch_status_label = ttk.Label(self.fetch_progress_frame, text="", style="Muted.TLabel")
        self.fetch_status_label.pack(anchor="w")
        self.fetch_progress_frame.pack_forget()

        # Download progress (hidden by default)
        self.download_progress_frame = ttk.Frame(status_wrap)
        self.download_label = ttk.Label(self.download_progress_frame, text="Downloading", style="Muted.TLabel")
        self.download_label.pack(anchor="w")
        self.progress = ttk.Progressbar(self.download_progress_frame, mode='determinate', length=300)
        self.progress.pack(fill=tk.X, pady=(3, 2))
        self.download_progress_frame.pack_forget()

        # Refined console log
        log_header = ttk.Label(status_wrap, text="STATUS LOG", style="SectionHeader.TLabel")
        log_header.pack(anchor="w", pady=(8, 2))

        self.message_screen = Text(
            status_wrap,
            height=11,
            font=('Menlo', 9) if self._is_macos() else ('Consolas', 9) if os.name == 'nt' else ('DejaVu Sans Mono', 9),
            bg=self.colors["BG_SECONDARY"],
            fg=self.colors["FG"],
            insertbackground=self.colors["ACCENT"],
            borderwidth=1,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["BORDER"],
            selectbackground=self.colors["ACCENT"],
            selectforeground="#1C1C20",
            padx=10,
            pady=8
        )
        self.message_screen.pack(expand=True, fill=tk.BOTH)
        self.message_screen.config(state=tk.DISABLED)

        # Setup text tags for colored output (snappier feedback)
        self._setup_log_tags()

        self.updateFormatColor()
        self.last_checked_url = ""
        self.master.after(900, self.autoFetchResolutions)

    def _is_macos(self):
        import platform
        return platform.system() == "Darwin"

    def autoFetchResolutions(self):
        """
        Periodically checks the URL field to trigger resolution fetching.
        """
        current_url = self.url_entry.get()
        if current_url and current_url != self.last_checked_url:
            self.last_checked_url = current_url
            threading.Thread(target=self.fetchResolutions, daemon=True).start()
        self.master.after(900, self.autoFetchResolutions)

    def browsePath(self):
        """
        Opens a directory selection dialog.
        """
        path = filedialog.askdirectory(initialdir=os.path.expanduser('~'))
        if path:
            self.path_display.delete(0, tk.END)
            self.path_display.insert(0, path)

    def fetchResolutions(self):
        """
        Fetches available resolutions for the current YouTube URL.
        Shows inline fetching state.
        """
        url = self.last_checked_url
        if not url:
            return

        self.fetch_progress_frame.pack(fill=tk.X, pady=(4, 6))
        self.fetch_progress['value'] = 15
        self.fetch_status_label.config(text="Contacting YouTube…")
        self.fetch_progress.update()

        try:
            downloader = Mp4Downloader(log_callback=self.logMessage)
            downloader.setUrl(url)
            
            opts = {
                'noplaylist': True, 
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'skip': ['translated_subs'],
                    }
                },
                'format': 'bestvideo+bestaudio/best',
            }
            cookie_file = downloader.cookie_manager.getCookieFile()
            if cookie_file:
                opts['cookiefile'] = cookie_file
            
            import yt_dlp
            self.fetch_progress['value'] = 45
            self.fetch_status_label.config(text="Parsing formats…")
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            formats = info.get('formats', [])
            
            video_formats = [f for f in formats if f.get('height') and f.get('vcodec') != 'none']
            resolutions = sorted(list(set([f['height'] for f in video_formats])), reverse=True)
            
            audio_formats = [f for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
            if audio_formats:
                resolutions.append('Audio Only')
            
            if not resolutions:
                self.logMessage("No video resolutions found.")
                self.fetch_progress_frame.pack_forget()
                return

            self.resolution_var.set(resolutions[0] if isinstance(resolutions[0], str) else f"{resolutions[0]}")
            menu = self.resolution_menu['menu']
            menu.delete(0, 'end')
            for res in resolutions:
                label = f"{res}" if res == 'Audio Only' else f"{res}p"
                val = res
                menu.add_command(label=label, command=lambda v=val: self.resolution_var.set(v))
            
            self.fetch_progress['value'] = 100
            self.fetch_status_label.config(text="Done")
            self.master.after(450, self.fetch_progress_frame.pack_forget)
            self.logMessage(f"Resolutions fetched: {', '.join(map(str, resolutions))}")

        except Exception as e:
            self.logMessage(f"Resolution fetch error: {e}")
            self.fetch_progress_frame.pack_forget()

    def startDownload(self):
        """
        Initializes and starts the download process in a separate thread.
        """
        self.progress['value'] = 0
        self.progress.update()
        self.download_progress_frame.pack(fill=tk.X, pady=(6, 2))

        url = self.url_entry.get()
        path = self.path_display.get() or self.default_download_path

        if self.format_var.get() == "MP4":
            resolution = self.resolution_var.get()
            if not resolution:
                messagebox.showerror("Error", "Please fetch and select a resolution.")
                self.download_progress_frame.pack_forget()
                return
            self.downloader = Mp4Downloader(self.updateProgress, self.logMessage)
            self.downloader.setUrl(url)
            self.downloader.setPath(path)
            try:
                self.downloader.resolution = int(resolution)
            except (ValueError, TypeError):
                self.downloader.resolution = 0  # let downloader pick best
            download_thread = threading.Thread(target=self.downloader.downloadVideo)
        elif self.format_var.get() == "MP3":
            self.downloader = Mp3Downloader(url, path, self.updateProgress, self.logMessage)
            download_thread = threading.Thread(target=self.downloader.downloadAsMp3)
        download_thread.start()

    def updateProgress(self, percentage):
        """
        Updates the progress bar UI.

        Args:
            percentage (int): Progress percentage (0-100).
        """
        self.progress['value'] = percentage
        self.progress.update()
        if percentage >= 100:
            self.master.after(2600, self.clearProgressBar)

    def clearProgressBar(self):
        """
        Resets the progress bar to zero and hides container.
        """
        self.progress['value'] = 0
        self.progress.update()
        self.download_progress_frame.pack_forget()

    def logMessage(self, message):
        """
        Appends a message to the status display area.
        Uses color tags when possible for better visual feedback.
        """
        self.message_screen.config(state=tk.NORMAL)

        tag = "info"
        lower = message.lower()
        if any(x in lower for x in ["error", "fail", "exception", "could not"]):
            tag = "error"
        elif any(x in lower for x in ["success", "complete", "downloaded", "finished", "100%"]):
            tag = "success"

        self.message_screen.insert(tk.END, message + "\n", tag)
        self.message_screen.see(tk.END)
        self.message_screen.config(state=tk.DISABLED)

    def _setup_log_tags(self):
        """Configure colored tags for the log Text widget."""
        c = self.colors
        self.message_screen.tag_config("info", foreground=c["FG"])
        self.message_screen.tag_config("success", foreground=c["SUCCESS"])
        self.message_screen.tag_config("error", foreground=c["ERROR"])

    def updateFormatColor(self):
        """
        Updates the UI state based on the selected download format.
        """
        is_mp4 = self.format_var.get() == "MP4"
        self.resolution_menu.config(state=tk.NORMAL if is_mp4 else tk.DISABLED)

class BatchDownloadPanel(ttk.Frame):
    """
    Panel for batch video downloads (playlists and channels).

    Allows users to scrape content from a playlist or channel and download
    all videos in the desired format and quality.
    """

    def __init__(self, parent, colors):
        """
        Initializes the BatchDownloadPanel.

        Args:
            parent: The parent widget.
            colors (dict): Theme color palette.
        """
        super().__init__(parent)
        self.master = parent
        self.colors = colors
        self.buildGui()
        self.displayStartupInfo()

    def buildGui(self):
        """
        Constructs the GUI components for the batch download panel.
        Cleaner layout, more breathing room, refined controls.
        """
        main = ttk.Frame(self, padding="16 14 16 12")
        main.pack(expand=True, fill=tk.BOTH)

        # URL
        ttk.Label(main, text="PLAYLIST OR CHANNEL URL", style="SectionHeader.TLabel").pack(anchor="w", padx=2)
        url_frame = ttk.Frame(main)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(fill=tk.X, ipady=4)

        # Base path
        ttk.Label(main, text="SAVE TO", style="SectionHeader.TLabel").pack(anchor="w", padx=2)
        path_frame = ttk.Frame(main)
        path_frame.pack(fill=tk.X, pady=(0, 12))
        self.path_display = ttk.Entry(path_frame)
        self.path_display.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self.path_display.insert(0, str(Path.home() / "Downloads"))
        self.browse_button = ttk.Button(path_frame, text="Browse", command=self.browsePath, style="Ghost.TButton")
        self.browse_button.pack(side=tk.RIGHT, padx=(8, 0))

        # Options
        ttk.Label(main, text="OPTIONS", style="SectionHeader.TLabel").pack(anchor="w", padx=2)
        opt = ttk.Frame(main)
        opt.pack(fill=tk.X, pady=(2, 10))

        # Row 0: Format
        ttk.Label(opt, text="Format").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=3)
        self.format_var = tk.StringVar(value="MP4")
        fr = ttk.Frame(opt)
        fr.grid(row=0, column=1, sticky="w")
        self.mp4_radio = ttk.Radiobutton(fr, text="MP4", variable=self.format_var, value="MP4", command=self.updateFormatColor)
        self.mp4_radio.pack(side=tk.LEFT, padx=(0, 10))
        self.mp3_radio = ttk.Radiobutton(fr, text="MP3", variable=self.format_var, value="MP3", command=self.updateFormatColor)
        self.mp3_radio.pack(side=tk.LEFT)

        # Quality
        ttk.Label(opt, text="Quality").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=3)
        self.quality_var = tk.StringVar(value="Highest")
        self.quality_menu = ttk.OptionMenu(opt, self.quality_var, "Highest")
        self.quality_menu.grid(row=1, column=1, sticky="w", pady=1)
        self.populateQualityMenu()

        # Max videos
        ttk.Label(opt, text="Max Videos").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=3)
        self.max_videos_var = tk.StringVar(value="200")
        self.max_videos_entry = ttk.Entry(opt, textvariable=self.max_videos_var, width=9)
        self.max_videos_entry.grid(row=2, column=1, sticky="w")

        # Mode
        ttk.Label(opt, text="Mode").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=3)
        mr = ttk.Frame(opt)
        mr.grid(row=3, column=1, sticky="w")
        self.mode_var = tk.StringVar(value="Playlist Download")
        ttk.Radiobutton(mr, text="Playlist Download", variable=self.mode_var, value="Playlist Download").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mr, text="Profile Scrape", variable=self.mode_var, value="Profile Scrape").pack(side=tk.LEFT)

        # Trace for mode
        self.mode_var.trace_add("write", self.updateMaxVideosDisplay)

        # Action buttons
        btn_row = ttk.Frame(main)
        btn_row.pack(fill=tk.X, pady=(6, 8))
        btn_row.columnconfigure(0, weight=3)
        btn_row.columnconfigure(1, weight=1)

        self.download_button = ttk.Button(btn_row, text="▶  Start Batch Download", command=self.startBatchDownload, style="Primary.TButton")
        self.download_button.grid(row=0, column=0, sticky="ew", padx=(0, 6), ipady=2)

        self.cancel_button = ttk.Button(btn_row, text="Cancel", command=self.cancelDownload, state=tk.DISABLED, style="Ghost.TButton")
        self.cancel_button.grid(row=0, column=1, sticky="ew")

        # Progress containers
        prog_wrap = ttk.Frame(main)
        prog_wrap.pack(fill=tk.X, pady=(2, 4))

        self.fetch_progress_frame = ttk.Frame(prog_wrap)
        ttk.Label(self.fetch_progress_frame, text="Fetching list…", style="Muted.TLabel").pack(anchor="w")
        self.fetch_progress = ttk.Progressbar(self.fetch_progress_frame, mode='determinate')
        self.fetch_progress.pack(fill=tk.X, pady=2)
        self.fetch_status_label = ttk.Label(self.fetch_progress_frame, text="", style="Muted.TLabel")
        self.fetch_status_label.pack(anchor="w")
        self.fetch_progress_frame.pack_forget()

        self.download_progress_frame = ttk.Frame(prog_wrap)
        ttk.Label(self.download_progress_frame, text="Batch progress", style="Muted.TLabel").pack(anchor="w")
        self.progress = ttk.Progressbar(self.download_progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=2)
        self.download_progress_frame.pack_forget()

        # Status log
        ttk.Label(main, text="STATUS LOG", style="SectionHeader.TLabel").pack(anchor="w", pady=(8, 2))
        self.message_screen = Text(
            main,
            height=11,
            font=('Menlo', 9) if self._is_macos() else ('Consolas', 9) if os.name == 'nt' else ('DejaVu Sans Mono', 9),
            bg=self.colors["BG_SECONDARY"],
            fg=self.colors["FG"],
            insertbackground=self.colors["ACCENT"],
            borderwidth=1,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["BORDER"],
            selectbackground=self.colors["ACCENT"],
            selectforeground="#1C1C20",
            padx=10,
            pady=8
        )
        self.message_screen.pack(expand=True, fill=tk.BOTH)
        self.message_screen.config(state=tk.DISABLED)

        self._setup_log_tags()

        self.updateFormatColor()
        self.last_checked_url = ""
        self.master.after(900, self.autoFetchResolutions)

    def _is_macos(self):
        import platform
        return platform.system() == "Darwin"

    def _setup_log_tags(self):
        """Configure colored tags for the log Text widget."""
        c = self.colors
        self.message_screen.tag_config("info", foreground=c["FG"])
        self.message_screen.tag_config("success", foreground=c["SUCCESS"])
        self.message_screen.tag_config("error", foreground=c["ERROR"])

    def autoFetchResolutions(self):
        """
        Periodically checks the URL field to trigger resolution fetching.
        """
        current_url = self.url_entry.get()
        if current_url and current_url != self.last_checked_url:
            self.last_checked_url = current_url
            threading.Thread(target=self.fetchResolutions, daemon=True).start()
        self.master.after(900, self.autoFetchResolutions)

    def browsePath(self):
        """
        Opens a directory selection dialog.
        """
        path = filedialog.askdirectory(initialdir=os.path.expanduser('~'))
        if path:
            self.path_display.delete(0, tk.END)
            self.path_display.insert(0, path)

    def fetchResolutions(self):
        """
        Fetches available resolutions from the first video in playlist/channel.
        """
        url = self.last_checked_url
        if not url:
            return

        self.fetch_progress_frame.pack(fill=tk.X, pady=(2, 4))
        self.fetch_progress['value'] = 20
        self.fetch_status_label.config(text="Scanning source…")
        self.fetch_progress.update()

        try:
            from .Mp4_Converter import Mp4Downloader
            import yt_dlp
            
            downloader = Mp4Downloader(log_callback=self.logMessage)
            
            opts = {
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'skip': ['translated_subs'],
                    }
                },
            }
            cookie_file = downloader.cookie_manager.getCookieFile()
            if cookie_file:
                opts['cookiefile'] = cookie_file
            
            fetch_url = url
            if 'list=' in url:
                with yt_dlp.YoutubeDL({'extract_flat': True, 'quiet': True}) as ydl:
                    playlist_info = ydl.extract_info(url, download=False)
                    if playlist_info and 'entries' in playlist_info and playlist_info['entries']:
                        first_entry = playlist_info['entries'][0]
                        if first_entry:
                            fetch_url = f"https://www.youtube.com/watch?v={first_entry.get('id', '')}"
            
            self.fetch_progress['value'] = 55
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(fetch_url, download=False)
            
            formats = info.get('formats', [])
            video_formats = [f for f in formats if f.get('height') and f.get('vcodec') != 'none']
            resolutions = sorted(list(set([f['height'] for f in video_formats])), reverse=True)
            
            if not resolutions:
                self.logMessage("No resolutions detected. Using defaults.")
                self.fetch_progress_frame.pack_forget()
                return

            menu = self.quality_menu["menu"]
            menu.delete(0, "end")
            menu.add_command(label="Highest", command=lambda: self.quality_var.set("Highest"))
            for res in resolutions:
                menu.add_command(label=f"{res}p", command=lambda v=f"{res}p": self.quality_var.set(v))
            
            self.fetch_progress['value'] = 100
            self.fetch_status_label.config(text="Updated")
            self.master.after(420, self.fetch_progress_frame.pack_forget)
            self.logMessage(f"Resolutions: {', '.join([f'{r}p' for r in resolutions])}")

        except Exception as e:
            self.logMessage(f"Could not fetch resolutions: {e}")
            self.fetch_progress_frame.pack_forget()

    def updateFormatColor(self):
        """
        Updates the UI state based on the selected download format.
        """
        is_mp4 = self.format_var.get() == "MP4"
        self.quality_menu.config(state=tk.NORMAL if is_mp4 else tk.DISABLED)

    def populateQualityMenu(self):
        """
        Populates the quality dropdown with common resolution choices.
        """
        quality_options = [
            "Highest",
            "2160p",
            "1440p",
            "1080p",
            "720p",
            "480p",
            "360p",
            "240p",
            "144p",
        ]
        menu = self.quality_menu["menu"]
        menu.delete(0, "end")
        for option in quality_options:
            menu.add_command(label=option, command=lambda value=option: self.quality_var.set(value))

    def updateMaxVideosDisplay(self, *args):
        """
        Updates the Max Videos field based on the selected mode.
        """
        if self.mode_var.get() == "Profile Scrape":
            self.max_videos_var.set("ALL")
        else:
            self.max_videos_var.set("200")

    def startBatchDownload(self):
        """
        Starts the batch download process in a separate thread.
        """
        url = self.url_entry.get().strip()
        base_path = self.path_display.get().strip() or os.path.expanduser('~')
        format_type = self.format_var.get()
        quality = self.quality_var.get()
        max_videos_str = self.max_videos_var.get()
        mode = self.mode_var.get()

        if max_videos_str == "ALL":
            max_videos = 10000
        else:
            max_videos = int(max_videos_str)

        if not url:
            self.logMessage("Error: Please enter a URL")
            return

        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.download_progress_frame.pack(fill=tk.X, pady=(2, 4))

        download_thread = threading.Thread(
            target=self.executeBatchDownload,
            args=(url, base_path, format_type, quality, max_videos, mode),
            daemon=True
        )
        download_thread.start()

    def cancelDownload(self):
        """
        Cancels the ongoing batch download.
        """
        if hasattr(self, 'batch_downloader') and self.batch_downloader:
            self.batch_downloader.cancelDownload()
            self.cancel_button.config(state=tk.DISABLED)
            self.download_button.config(state=tk.NORMAL)

    def executeBatchDownload(self, url, base_path, format_type, quality, max_videos, mode):
        """
        Coordinates the scraping and downloading process for a batch.

        Args:
            url (str): Target YouTube URL.
            base_path (str): Base directory for files.
            format_type (str): 'MP4' or 'MP3'.
            quality (str): Quality preference.
            max_videos (int): Video limit.
            mode (str): Download mode.
        """
        try:
            self.batch_downloader = None
            self.fetch_progress_frame.pack(fill=tk.X, pady=(2, 4))
            self.fetch_progress['value'] = 0
            self.fetch_status_label.config(text="")

            if mode == "Playlist Download":
                self.logMessage(f"Scraping playlist: {url}")
                from .PlaylistScraper import PlaylistScraper
                scraper = PlaylistScraper(timeout=2.0)
                
                def fetchProgressCallback(current, total, percentage):
                    self.updateFetchProgress(current, total, percentage)
                
                videos = scraper.scrapePlaylist(url, max_videos, fetchProgressCallback)

                if not videos:
                    self.logMessage("No videos found in playlist")
                    return

                self.logMessage(f"Found {len(videos)} videos in playlist")

                video_list = []
                playlist_title = sanitizeFilename(scraper.getPlaylistTitle(url))
                for video in videos:
                    video_list.append({
                        'url': video['url'],
                        'title': sanitizeFilename(video['title']),
                        'folder': f"Playlists/{playlist_title}"
                    })

            elif mode == "Profile Scrape":
                self.logMessage(f"Scraping channel: {url}")
                from .ChannelScraper import ChannelScraper
                scraper = ChannelScraper(timeout=2.0)
                
                def fetchProgressCallback(current, total, percentage):
                    self.updateFetchProgress(current, total, percentage)
                
                channel_info = scraper.scrapeChannel(url, 1000, fetchProgressCallback)

                if not channel_info['playlists'] and not channel_info['standalone_videos']:
                    self.logMessage("No content found in channel")
                    return

                self.logMessage(f"Found {len(channel_info['playlists'])} playlists and {len(channel_info['standalone_videos'])} standalone videos")

                video_list = []
                channel_name = sanitizeFilename(channel_info['channel_name'])

                for playlist in channel_info['playlists']:
                    for video in playlist['videos']:
                        video_list.append({
                            'url': video['url'],
                            'title': sanitizeFilename(video['title']),
                            'folder': f"{channel_name}/{sanitizeFilename(playlist['title'])}"
                        })

                for video in channel_info['standalone_videos']:
                    video_list.append({
                        'url': video['url'],
                        'title': sanitizeFilename(video['title']),
                        'folder': f"{channel_name}/Random"
                    })

            self.fetch_progress_frame.pack_forget()
            self.download_progress_frame.pack(fill=tk.X, pady=(2, 4))
            self.logMessage("Data fetching complete. Starting downloads...")

            self.batch_downloader = BatchDownloader(
                max_workers=3,
                progress_callback=self.updateProgress,
                log_callback=self.logMessage
            )

            results = self.batch_downloader.downloadBatch(
                video_list, format_type, base_path, quality
            )

            self.logMessage(f"Batch download completed: {results['successful']} successful, {results['failed']} failed")
            if results['errors']:
                self.logMessage("Errors encountered:")
                for error in results['errors'][:5]:
                    self.logMessage(f"  - {error}")
                if len(results['errors']) > 5:
                    self.logMessage(f"  ... and {len(results['errors']) - 5} more errors")

        except Exception as e:
            self.logMessage(f"Error during batch download: {str(e)}")

        finally:
            self.fetch_progress_frame.pack_forget()
            self.download_progress_frame.pack_forget()
            self.download_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.batch_downloader = None

    def updateFetchProgress(self, current, total, percentage):
        """
        Updates the UI for data fetching progress.
        """
        self.fetch_progress['value'] = max(0, min(100, percentage))
        self.fetch_status_label.config(text=f"{current} / {total}  •  {percentage}%")
        self.fetch_progress.update()
        self.fetch_status_label.update()

    def updateProgress(self, percentage):
        """
        Updates the UI for download progress.

        Args:
            percentage (int): Percentage complete.
        """
        self.progress['value'] = percentage
        self.progress.update()
        if percentage >= 100:
            self.master.after(1800, lambda: self.download_progress_frame.pack_forget())

    def logMessage(self, message):
        """
        Logs a message to the status display with colored tags.
        """
        self.message_screen.config(state=tk.NORMAL)

        tag = "info"
        lower = message.lower()
        if any(x in lower for x in ["error", "fail", "exception", "could not"]):
            tag = "error"
        elif any(x in lower for x in ["success", "complete", "downloaded", "finished", "100%", "done"]):
            tag = "success"

        self.message_screen.insert(tk.END, message + "\n", tag)
        self.message_screen.see(tk.END)
        self.message_screen.config(state=tk.DISABLED)

    def displayStartupInfo(self):
        """
        Displays system and default configuration information at startup.
        """
        import platform
        home_dir = os.path.expanduser('~')
        
        info_lines = [
            "— TubeHarvester Batch —",
            f"System: {platform.system()} {platform.release()}",
            f"Defaults → {self.format_var.get()} • {self.quality_var.get()} • max {self.max_videos_var.get()} • {self.mode_var.get()}",
            "Ready. Paste a playlist or channel URL above.",
            ""
        ]
        
        for line in info_lines:
            self.logMessage(line)

class YouTubeDownloaderGUI:
    """
    Main application window for TubeHarvester.

    Orchestrates the single and batch download panels, manages themes,
    and initializes the GUI environment.
    """

    def __init__(self, master):
        """
        Initializes the YouTubeDownloaderGUI.

        Args:
            master (tk.Tk): The root Tkinter window.
        """
        self.master = master
        self.master.title('TubeHarvester - YouTube Downloader')
        self.master.geometry("820x820")
        self.master.minsize(720, 680)
        self.master.resizable(True, True)

        # Claude-inspired soft dark theme with warm orange accents
        self.colors = {
            "BG": "#1C1C20",
            "BG_SECONDARY": "#252529",
            "BG_TERTIARY": "#2F2F34",
            "BG_INPUT": "#2D2D31",
            "FG": "#EDEDEF",
            "FG_SECONDARY": "#A1A1A7",
            "FG_MUTED": "#6E6E75",
            "ACCENT": "#FF7A3D",
            "ACCENT_HOVER": "#FF955F",
            "ACCENT_PRESSED": "#E86A2F",
            "BORDER": "#3A3A3F",
            "SUCCESS": "#22C55E",
            "ERROR": "#F87171",
        }

        # Set dark background for root window
        self.master.configure(bg=self.colors["BG"])

        # Style configuration - soft dark Claude-inspired + orange
        style = ttk.Style(self.master)
        style.theme_use('clam')

        # Root / general
        style.configure(".",
                        background=self.colors["BG"],
                        foreground=self.colors["FG"],
                        font=('Helvetica', 10))

        # Notebook / Tabs - clean modern look
        style.configure("TNotebook",
                        background=self.colors["BG"],
                        borderwidth=0,
                        tabmargins=[0, 0, 0, 0])

        style.configure("TNotebook.Tab",
                        background=self.colors["BG_SECONDARY"],
                        foreground=self.colors["FG_MUTED"],
                        borderwidth=0,
                        padding=[28, 11],
                        font=('Helvetica', 10))

        style.map("TNotebook.Tab",
                  background=[
                      ("selected", self.colors["BG_TERTIARY"]),
                      ("!selected", self.colors["BG_SECONDARY"])
                  ],
                  foreground=[
                      ("selected", self.colors["ACCENT"]),
                      ("!selected", self.colors["FG_MUTED"])
                  ],
                  padding=[("selected", [28, 11]), ("!selected", [28, 11])])

        # Frames
        style.configure("TFrame", background=self.colors["BG"], borderwidth=0)

        # Section header labels (used instead of heavy LabelFrames for refinement)
        style.configure("SectionHeader.TLabel",
                        background=self.colors["BG"],
                        foreground=self.colors["ACCENT"],
                        font=('Helvetica', 10, 'bold'),
                        padding=(0, 6, 0, 4))

        # Regular labels
        style.configure("TLabel",
                        background=self.colors["BG"],
                        foreground=self.colors["FG"],
                        padding=4,
                        font=('Helvetica', 10))

        style.configure("Muted.TLabel",
                        background=self.colors["BG"],
                        foreground=self.colors["FG_MUTED"],
                        font=('Helvetica', 9))

        # Entry fields - soft and focused with orange ring
        style.configure("TEntry",
                        fieldbackground=self.colors["BG_INPUT"],
                        foreground=self.colors["FG"],
                        bordercolor=self.colors["BORDER"],
                        lightcolor=self.colors["BORDER"],
                        darkcolor=self.colors["BORDER"],
                        borderwidth=1,
                        insertcolor=self.colors["ACCENT"],
                        padding=8,
                        font=('Helvetica', 10))
        style.map("TEntry",
                  fieldbackground=[("focus", self.colors["BG_TERTIARY"])],
                  bordercolor=[("focus", self.colors["ACCENT"])])

        # Buttons - secondary by default
        style.configure("TButton",
                        background=self.colors["BG_SECONDARY"],
                        foreground=self.colors["FG"],
                        bordercolor=self.colors["BORDER"],
                        borderwidth=1,
                        padding=(14, 8),
                        font=('Helvetica', 10))
        style.map("TButton",
                  background=[
                      ("active", self.colors["BG_TERTIARY"]),
                      ("pressed", self.colors["BG_TERTIARY"])
                  ],
                  foreground=[("active", self.colors["ACCENT"])])

        # Primary / Accent action button (warm orange)
        style.configure("Primary.TButton",
                        background=self.colors["ACCENT"],
                        foreground="#1C1C20",
                        bordercolor=self.colors["ACCENT"],
                        borderwidth=0,
                        padding=(18, 10),
                        font=('Helvetica', 10, 'bold'))
        style.map("Primary.TButton",
                  background=[
                      ("active", self.colors["ACCENT_HOVER"]),
                      ("pressed", self.colors["ACCENT_PRESSED"])
                  ],
                  foreground=[("active", "#1C1C20"), ("pressed", "#1C1C20")])

        # Subtle / ghost button for secondary actions (Browse, Cancel)
        style.configure("Ghost.TButton",
                        background=self.colors["BG_SECONDARY"],
                        foreground=self.colors["FG_SECONDARY"],
                        bordercolor=self.colors["BORDER"],
                        borderwidth=1,
                        padding=(12, 7),
                        font=('Helvetica', 9))
        style.map("Ghost.TButton",
                  background=[("active", self.colors["BG_TERTIARY"])],
                  foreground=[("active", self.colors["FG"])])

        # Radiobuttons - clean
        style.configure("TRadiobutton",
                        background=self.colors["BG"],
                        foreground=self.colors["FG"],
                        font=('Helvetica', 10),
                        padding=3)
        style.map("TRadiobutton",
                  foreground=[("active", self.colors["ACCENT"])])

        # OptionMenu / Menubutton
        style.configure("TMenubutton",
                        background=self.colors["BG_INPUT"],
                        foreground=self.colors["FG"],
                        bordercolor=self.colors["BORDER"],
                        borderwidth=1,
                        padding=(10, 6),
                        font=('Helvetica', 10))
        style.map("TMenubutton",
                  background=[("active", self.colors["BG_TERTIARY"])],
                  foreground=[("active", self.colors["ACCENT"])])

        # Progressbar - orange accent
        style.configure("TProgressbar",
                        troughcolor=self.colors["BG_SECONDARY"],
                        background=self.colors["ACCENT"],
                        bordercolor=self.colors["ACCENT"],
                        lightcolor=self.colors["ACCENT"],
                        darkcolor=self.colors["ACCENT"],
                        borderwidth=0,
                        thickness=8)

        # LabelFrame (used sparingly now) - very subtle
        style.configure("TLabelframe",
                        background=self.colors["BG"],
                        bordercolor=self.colors["BORDER"],
                        borderwidth=1)
        style.configure("TLabelframe.Label",
                        background=self.colors["BG"],
                        foreground=self.colors["ACCENT"],
                        font=('Helvetica', 9, 'bold'))

        # === Refined header ===
        header = ttk.Frame(self.master)
        header.pack(fill=tk.X, padx=18, pady=(16, 8))

        # Title with subtle orange accent
        title = ttk.Label(header, text="TubeHarvester", font=('Helvetica', 18, 'bold'),
                          foreground=self.colors["FG"])
        title.pack(side=tk.LEFT)

        accent_dot = ttk.Label(header, text="  ●", font=('Helvetica', 16),
                               foreground=self.colors["ACCENT"])
        accent_dot.pack(side=tk.LEFT, padx=(2, 0))

        subtitle = ttk.Label(header, text="YouTube Downloader", font=('Helvetica', 11),
                             foreground=self.colors["FG_MUTED"])
        subtitle.pack(side=tk.LEFT, padx=(10, 0))

        # Subtle divider line
        divider = ttk.Frame(self.master, height=1, style="TFrame")
        divider.pack(fill=tk.X, padx=18, pady=(0, 6))
        # We'll style the actual visual separator below via a colored frame
        sep = tk.Frame(self.master, height=1, bg=self.colors["BORDER"])
        sep.pack(fill=tk.X, padx=18, pady=(0, 4))

        # Notebook tabs
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=12, pady=(4, 12))

        # Single download tab
        self.single_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.single_tab, text="  Single Download  ")

        # Single download panel
        self.single_panel = SingleDownloadPanel(self.single_tab, colors=self.colors)
        self.single_panel.pack(expand=True, fill=tk.BOTH)

        # Batch download tab
        self.batch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_tab, text="  Batch Download  ")

        # Batch download panel
        self.batch_panel = BatchDownloadPanel(self.batch_tab, colors=self.colors)
        self.batch_panel.pack(expand=True, fill=tk.BOTH)

def runGui():
    """
    Initializes and runs the TubeHarvester GUI application.
    """
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    runGui()
