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
        """
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
        self.browse_button = ttk.Button(url_path_frame, text="Browse", command=self.browsePath)
        self.browse_button.grid(row=1, column=2, sticky="e", padx=5, pady=2)
        
        url_path_frame.columnconfigure(1, weight=1)

        # options frame - contains format and resolution selection
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10 10 10 10")
        options_frame.pack(fill=tk.X, pady=5)

        # format selection radio buttons (MP4/MP3)
        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky="w")
        self.format_var = tk.StringVar(value="MP4")
        self.mp4_radio = ttk.Radiobutton(options_frame, text="MP4", variable=self.format_var, value="MP4", command=self.updateFormatColor)
        self.mp4_radio.grid(row=0, column=1, sticky='w', padx=5)
        self.mp3_radio = ttk.Radiobutton(options_frame, text="MP3", variable=self.format_var, value="MP3", command=self.updateFormatColor)
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
        self.download_button = ttk.Button(controls_frame, text="Download", command=self.startDownload)
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

        self.updateFormatColor()
        self.last_checked_url = ""
        self.master.after(1000, self.autoFetchResolutions)

    def autoFetchResolutions(self):
        """
        Periodically checks the URL field to trigger resolution fetching.
        """
        current_url = self.url_entry.get()
        if current_url and current_url != self.last_checked_url:
            self.last_checked_url = current_url
            threading.Thread(target=self.fetchResolutions, daemon=True).start()
        self.master.after(1000, self.autoFetchResolutions)

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
        """
        url = self.last_checked_url
        if not url:
            return

        try:
            downloader = Mp4Downloader(log_callback=self.logMessage)
            downloader.setUrl(url)
            
            # Use the same options as the actual download to get all available formats
            opts = {
                'noplaylist': True, 
                'cookiefile': downloader.cookie_manager.getCookieFile(),
                'javascript_executor': '/home/ice/.deno/bin/deno',
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'hl': 'en-US',
                        'gl': 'US',
                    }
                },
                'youtube_include_dash_manifest': True,
                'youtube_include_hls_manifest': True,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',  # Get all available formats for resolution selection
            }
            
            import yt_dlp
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            formats = info.get('formats', [])
            
            # Get all available resolutions from video formats
            video_formats = [f for f in formats if f.get('height') and f.get('vcodec') != 'none']
            resolutions = sorted(list(set([f['height'] for f in video_formats])), reverse=True)
            
            # Also include audio-only formats if available
            audio_formats = [f for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
            if audio_formats:
                resolutions.append('Audio Only')
            
            if not resolutions:
                messagebox.showinfo("Info", "No video resolutions found.")
                return

            self.resolution_var.set(resolutions[0])
            menu = self.resolution_menu['menu']
            menu.delete(0, 'end')
            for res in resolutions:
                if res == 'Audio Only':
                    menu.add_command(label=f"{res}", command=lambda value=res: self.resolution_var.set(value))
                else:
                    menu.add_command(label=f"{res}p", command=lambda value=res: self.resolution_var.set(value))
            
            self.logMessage(f"Resolutions fetched successfully: {', '.join(map(str, resolutions))}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch resolutions: {e}")

    def startDownload(self):
        """
        Initializes and starts the download process in a separate thread.
        """
        self.progress['value'] = 0
        self.progress.update()

        url = self.url_entry.get()
        path = self.path_display.get() or self.default_download_path

        if self.format_var.get() == "MP4":
            resolution = self.resolution_var.get()
            if not resolution:
                messagebox.showerror("Error", "Please fetch and select a resolution.")
                return
            self.downloader = Mp4Downloader(self.updateProgress, self.logMessage)
            self.downloader.setUrl(url)
            self.downloader.setPath(path)
            self.downloader.resolution = int(resolution)
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
        if percentage == 100:
            self.master.after(3000, self.clearProgressBar)

    def clearProgressBar(self):
        """
        Resets the progress bar to zero.
        """
        self.progress['value'] = 0
        self.progress.update()

    def logMessage(self, message):
        """
        Appends a message to the status display area.

        Args:
            message (str): The message to log.
        """
        self.message_screen.config(state=tk.NORMAL)
        self.message_screen.insert(tk.END, message + "\n")
        self.message_screen.see(tk.END)
        self.message_screen.config(state=tk.DISABLED)

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
        """
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
        self.browse_button = ttk.Button(url_path_frame, text="Browse", command=self.browsePath)
        self.browse_button.grid(row=1, column=2, sticky="e", padx=5, pady=2)

        url_path_frame.columnconfigure(1, weight=1)

        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10 10 10 10")
        options_frame.pack(fill=tk.X, pady=5)

        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky="w")
        self.format_var = tk.StringVar(value="MP4")
        self.mp4_radio = ttk.Radiobutton(options_frame, text="MP4", variable=self.format_var, value="MP4", command=self.updateFormatColor)
        self.mp4_radio.grid(row=0, column=1, sticky='w', padx=5)
        self.mp3_radio = ttk.Radiobutton(options_frame, text="MP3", variable=self.format_var, value="MP3", command=self.updateFormatColor)
        self.mp3_radio.grid(row=0, column=2, sticky='w', padx=5)

        ttk.Label(options_frame, text="Quality:").grid(row=1, column=0, sticky="w")
        self.quality_var = tk.StringVar(value="Highest")
        self.quality_menu = ttk.OptionMenu(options_frame, self.quality_var, "Highest")
        self.quality_menu.grid(row=1, column=1, sticky="w", pady=5)
        self.populateQualityMenu()

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
        self.mode_var.trace_add("write", self.updateMaxVideosDisplay)

        # Controls Frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        self.download_button = ttk.Button(controls_frame, text="Start Batch Download", command=self.startBatchDownload)
        self.download_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.cancel_button = ttk.Button(controls_frame, text="Cancel", command=self.cancelDownload, state=tk.DISABLED)
        self.cancel_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Fetching Data Progress Bar
        self.fetch_progress_frame = ttk.Frame(controls_frame)
        self.fetch_progress_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.fetch_label = ttk.Label(self.fetch_progress_frame, text="Fetching Data:", font=('Courier', 9, 'bold'))
        self.fetch_label.pack(anchor='w')
        
        self.fetch_progress = ttk.Progressbar(self.fetch_progress_frame, orient='horizontal', length=400, mode='determinate')
        self.fetch_progress.pack(fill=tk.X, pady=2)
        
        self.fetch_status_label = ttk.Label(self.fetch_progress_frame, text="", font=('Courier', 9))
        self.fetch_status_label.pack(anchor='w')
        
        # Hide fetch progress initially
        self.fetch_progress_frame.grid_remove()

        # Download Progress Bar
        self.download_progress_frame = ttk.Frame(controls_frame) # Change parent to controls_frame
        self.download_progress_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5) # Use grid for placement
        
        self.download_label = ttk.Label(self.download_progress_frame, text="Download Progress:", font=('Courier', 9, 'bold'))
        self.download_label.pack(anchor='w')
        
        self.progress = ttk.Progressbar(self.download_progress_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(fill=tk.X, pady=2)
        
        # Hide download progress initially
        self.download_progress_frame.grid_remove() # Use grid_remove instead of pack_forget

        # Progress and Log Frame (now only contains message_screen)
        progress_log_frame = ttk.LabelFrame(main_frame, text="Status", padding="10 10 10 10")
        progress_log_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        self.message_screen = Text(progress_log_frame, height=10, width=75, font=('Courier', 9), 
                                   fg=self.colors["FOREGROUND_COLOR"], bg=self.colors["SECONDARY_BACKGROUND_COLOR"], insertbackground=self.colors["ACCENT_COLOR"],
                                   borderwidth=0, highlightthickness=1, highlightbackground=self.colors["ACCENT_COLOR"],
                                   selectbackground=self.colors["ACCENT_COLOR_DARK"], selectforeground=self.colors["FOREGROUND_COLOR"])
        self.message_screen.pack(expand=True, fill=tk.BOTH, pady=5)
        self.message_screen.config(state=tk.DISABLED)

        self.message_screen.config(state=tk.DISABLED)

        self.updateFormatColor()
        self.last_checked_url = ""
        self.master.after(1000, self.autoFetchResolutions)

    def autoFetchResolutions(self):
        """
        Periodically checks the URL field to trigger resolution fetching.
        """
        current_url = self.url_entry.get()
        if current_url and current_url != self.last_checked_url:
            self.last_checked_url = current_url
            threading.Thread(target=self.fetchResolutions, daemon=True).start()
        self.master.after(1000, self.autoFetchResolutions)

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

        try:
            from .Mp4_Converter import Mp4Downloader
            import yt_dlp
            
            downloader = Mp4Downloader(log_callback=self.logMessage)
            
            opts = {
                'noplaylist': True,
                'cookiefile': downloader.cookie_manager.getCookieFile(),
                'javascript_executor': '/home/ice/.deno/bin/deno',
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'hl': 'en-US',
                        'gl': 'US',
                    }
                },
                'youtube_include_dash_manifest': True,
                'youtube_include_hls_manifest': True,
            }
            
            # For playlists, get first video URL to check formats
            fetch_url = url
            if 'list=' in url:
                with yt_dlp.YoutubeDL({'extract_flat': True, 'quiet': True}) as ydl:
                    playlist_info = ydl.extract_info(url, download=False)
                    if playlist_info and 'entries' in playlist_info and playlist_info['entries']:
                        first_entry = playlist_info['entries'][0]
                        if first_entry:
                            fetch_url = f"https://www.youtube.com/watch?v={first_entry.get('id', '')}"
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(fetch_url, download=False)
            
            formats = info.get('formats', [])
            video_formats = [f for f in formats if f.get('height') and f.get('vcodec') != 'none']
            resolutions = sorted(list(set([f['height'] for f in video_formats])), reverse=True)
            
            if not resolutions:
                self.logMessage("No video resolutions found. Using preset values.")
                return

            # Update quality menu with actual resolutions
            menu = self.quality_menu["menu"]
            menu.delete(0, "end")
            menu.add_command(label="Highest", command=lambda: self.quality_var.set("Highest"))
            for res in resolutions:
                menu.add_command(label=f"{res}p", command=lambda value=f"{res}p": self.quality_var.set(value))
            
            self.logMessage(f"Resolutions fetched: {', '.join([f'{r}p' for r in resolutions])}")

        except Exception as e:
            self.logMessage(f"Could not fetch resolutions: {e}")

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
            self.fetch_progress_frame.grid()
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

            self.fetch_progress_frame.grid_remove()
            self.download_progress_frame.grid()
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
            self.fetch_progress_frame.grid_remove()
            self.download_progress_frame.grid_remove()
            self.download_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.batch_downloader = None

    def updateFetchProgress(self, current, total, percentage):
        """
        Updates the UI for data fetching progress.

        Args:
            current (int): Current item index.
            total (int): Total items.
            percentage (int): Percentage complete.
        """
        self.fetch_progress['value'] = percentage
        bar_width = 20
        filled = int((percentage / 100) * bar_width)
        bar = '=' * filled + '>' + ' ' * (bar_width - filled - 1)
        status_text = f"[{bar}] {percentage}% ({current}/{total} items)"
        self.fetch_status_label.config(text=status_text)
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

    def logMessage(self, message):
        """
        Logs a message to the status display.

        Args:
            message (str): The message to log.
        """
        self.message_screen.config(state=tk.NORMAL)
        self.message_screen.insert(tk.END, message + "\n")
        self.message_screen.see(tk.END)
        self.message_screen.config(state=tk.DISABLED)

    def displayStartupInfo(self):
        """
        Displays system and default configuration information at startup.
        """
        import platform
        home_dir = os.path.expanduser('~')
        
        info_lines = [
            "=" * 60,
            "TubeHarvester - Batch Download Configuration",
            "=" * 60,
            f"System: {platform.system()} {platform.release()}",
            f"Home Directory: {home_dir}",
            "",
            "Default Settings:",
            f"  Format: {self.format_var.get()}",
            f"  Quality: {self.quality_var.get()}",
            f"  Max Videos: {self.max_videos_var.get()}",
            f"  Mode: {self.mode_var.get()}",
            "",
            "Output Structure:",
            "  MP3: ~/Music/<Source>/<Playlist or Random>/",
            "  MP4: ~/Videos/<Source>/<Playlist or Random>/",
            "",
            "Ready for download.",
            "=" * 60,
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

def runGui():
    """
    Initializes and runs the TubeHarvester GUI application.
    """
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    runGui()
