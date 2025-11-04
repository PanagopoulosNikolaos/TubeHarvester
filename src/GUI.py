import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Text
import threading
from .Mp4_Converter import YouTubeDownloader
from .Mp3_Converter import MP3Downloader
from pathlib import Path
from .BatchDownloader import BatchDownloader

class SingleDownloadPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent
        self.downloader = None
        self.default_download_path = str(Path.home() / "Downloads")
        self.build_gui()

    def build_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # URL and Path Frame
        url_path_frame = ttk.LabelFrame(main_frame, text="Input", padding="10 10 10 10")
        url_path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_path_frame, text="YouTube URL:").grid(row=0, column=0, sticky="w", pady=2)
        self.url_entry = ttk.Entry(url_path_frame, width=60)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)

        ttk.Label(url_path_frame, text="Download Path:").grid(row=1, column=0, sticky="w", pady=2)
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

        ttk.Label(options_frame, text="Resolution:").grid(row=1, column=0, sticky="w")
        self.resolution_var = tk.StringVar(self.master)
        self.resolution_menu = ttk.OptionMenu(options_frame, self.resolution_var, "Highest")
        self.resolution_menu.grid(row=1, column=1, columnspan=2, sticky="w", pady=5)

        # Controls Frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        self.download_button = ttk.Button(controls_frame, text="Download", command=self.start_download)
        self.download_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.close_button = ttk.Button(controls_frame, text="Close", command=self.master.destroy)
        self.close_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Progress and Log Frame
        progress_log_frame = ttk.LabelFrame(main_frame, text="Status", padding="10 10 10 10")
        progress_log_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        self.progress = ttk.Progressbar(progress_log_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        self.message_screen = Text(progress_log_frame, height=10, width=75, font=('Courier', 9), 
                                   fg='#c9d1d9', bg='#161b22', insertbackground='#ffd700',
                                   borderwidth=0, highlightthickness=1, highlightbackground='#ffd700',
                                   selectbackground='#daa520', selectforeground='#ffffff')
        self.message_screen.pack(expand=True, fill=tk.BOTH, pady=5)
        self.message_screen.config(state=tk.DISABLED)

        self.update_format_color()
        self.last_checked_url = ""
        self.master.after(1000, self.auto_fetch_resolutions)

    def auto_fetch_resolutions(self):
        current_url = self.url_entry.get()
        if current_url and current_url != self.last_checked_url:
            self.last_checked_url = current_url
            # Run fetching in a separate thread to not block the GUI
            threading.Thread(target=self.fetch_resolutions, daemon=True).start()
        self.master.after(1000, self.auto_fetch_resolutions) # Check again in 1 second

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_display.delete(0, tk.END)
            self.path_display.insert(0, path)

    def fetch_resolutions(self):
        url = self.last_checked_url # Use the last checked URL
        if not url:
            return # Silently return if no URL

        try:
            downloader = YouTubeDownloader()
            downloader.set_url(url)
            info = downloader.fetch_video_info()
            formats = info.get('formats', [])
            resolutions = sorted(list(set([f['height'] for f in formats if f.get('height') and f.get('vcodec') != 'none'])), reverse=True)
            
            if not resolutions:
                messagebox.showinfo("Info", "No video resolutions found.")
                return

            self.resolution_var.set(resolutions[0]) # Default to highest
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
        # This can be expanded to disable/enable the resolution dropdown
        is_mp4 = self.format_var.get() == "MP4"
        self.resolution_menu.config(state=tk.NORMAL if is_mp4 else tk.DISABLED)

class BatchDownloadPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent
        self.build_gui()

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

        self.progress = ttk.Progressbar(progress_log_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        self.message_screen = Text(progress_log_frame, height=10, width=75, font=('Courier', 9), 
                                   fg='#c9d1d9', bg='#161b22', insertbackground='#ffd700',
                                   borderwidth=0, highlightthickness=1, highlightbackground='#ffd700',
                                   selectbackground='#daa520', selectforeground='#ffffff')
        self.message_screen.pack(expand=True, fill=tk.BOTH, pady=5)
        self.message_screen.config(state=tk.DISABLED)

        self.update_format_color()

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_display.delete(0, tk.END)
            self.path_display.insert(0, path)

    def update_format_color(self):
        # This can be expanded to disable/enable the quality dropdown
        pass

    def update_max_videos_display(self, *args):
        """Update the Max Videos field based on selected mode."""
        if self.mode_var.get() == "Profile Scrape":
            self.max_videos_var.set("ALL")
        else:
            # Reset to default value when switching back to Playlist Download
            self.max_videos_var.set("200")

    def start_batch_download(self):
        """Start batch download based on selected mode."""
        url = self.url_entry.get().strip()
        base_path = self.path_display.get().strip() or os.path.expanduser('~')
        format_type = self.format_var.get()
        quality = self.quality_var.get()
        max_videos_str = self.max_videos_var.get()
        mode = self.mode_var.get()

        # Handle "ALL" value for Profile Scrape mode
        if max_videos_str == "ALL":
            max_videos = 10000  # Use high limit for unlimited
        else:
            max_videos = int(max_videos_str)

        if not url:
            self.log_message("Error: Please enter a URL")
            return

        # Disable start button and enable cancel button
        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

        # Clear previous progress
        self.progress['value'] = 0

        # Start download in separate thread
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

            if mode == "Playlist Download":
                # Scrape playlist
                self.log_message(f"Scraping playlist: {url}")
                from .PlaylistScraper import PlaylistScraper
                scraper = PlaylistScraper(timeout=2.0)
                videos = scraper.scrape_playlist(url, max_videos)

                if not videos:
                    self.log_message("No videos found in playlist")
                    return

                self.log_message(f"Found {len(videos)} videos in playlist")

                # Prepare video list for batch download
                video_list = []
                playlist_title = scraper.get_playlist_title(url)
                for video in videos:
                    video_list.append({
                        'url': video['url'],
                        'title': video['title'],
                        'folder': f"Playlists/{playlist_title}"  # Generic folder for playlist downloads
                    })

            elif mode == "Profile Scrape":
                # Scrape channel - no limit for profile scraping (get all videos)
                self.log_message(f"Scraping channel: {url} (unlimited videos)")
                from .ChannelScraper import ChannelScraper
                scraper = ChannelScraper(timeout=2.0)
                # Use a very high limit for profile scraping to get all videos
                channel_info = scraper.scrape_channel(url, 10000)  # 10k should be enough for most channels

                if not channel_info['playlists'] and not channel_info['standalone_videos']:
                    self.log_message("No content found in channel")
                    return

                self.log_message(f"Found {len(channel_info['playlists'])} playlists and {len(channel_info['standalone_videos'])} standalone videos")

                # Prepare video list for batch download
                video_list = []
                channel_name = channel_info['channel_name']

                # Add videos from playlists
                for playlist in channel_info['playlists']:
                    for video in playlist['videos']:
                        video_list.append({
                            'url': video['url'],
                            'title': video['title'],
                            'folder': f"{channel_name}/{playlist['title']}"
                        })

                # Add standalone videos
                for video in channel_info['standalone_videos']:
                    video_list.append({
                        'url': video['url'],
                        'title': video['title'],
                        'folder': f"{channel_name}/Random"
                    })

            # Start batch download
            self.batch_downloader = BatchDownloader(
                max_workers=3,
                progress_callback=self._update_progress,
                log_callback=self.log_message
            )

            results = self.batch_downloader.download_batch(
                video_list, format_type, base_path, quality
            )

            # Show final results
            self.log_message(f"Batch download completed: {results['successful']} successful, {results['failed']} failed")
            if results['errors']:
                self.log_message("Errors encountered:")
                for error in results['errors'][:5]:  # Show first 5 errors
                    self.log_message(f"  - {error}")
                if len(results['errors']) > 5:
                    self.log_message(f"  ... and {len(results['errors']) - 5} more errors")

        except Exception as e:
            self.log_message(f"Error during batch download: {str(e)}")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}")

        finally:
            # Re-enable buttons
            self.download_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.batch_downloader = None

    def _update_progress(self, percentage):
        """Update the progress bar."""
        self.progress['value'] = percentage
        self.progress.update()

    def log_message(self, message):
        self.message_screen.config(state=tk.NORMAL)
        self.message_screen.insert(tk.END, message + "\n")
        self.message_screen.see(tk.END)
        self.message_screen.config(state=tk.DISABLED)

class YouTubeDownloaderGUI:
    def __init__(self, master):
        self.master = master
        self.master.title('TubeHarvester - YouTube Downloader')
        self.master.geometry("750x650")
        self.master.resizable(True, True)
        
        # Set dark background for root window
        self.master.configure(bg='#0d1117')

        # Style configuration - GitHub Dark Theme
        style = ttk.Style(self.master)
        style.theme_use('clam')
        
        # GitHub Dark color palette with Gold accents
        bg_dark = '#0d1117'          # Main background
        bg_secondary = '#161b22'      # Secondary background
        bg_tertiary = '#21262d'       # Tertiary background (hover)
        border_color = '#30363d'      # Border color
        text_color = '#c9d1d9'        # Main text
        text_secondary = '#8b949e'    # Secondary text
        accent_gold = '#ffd700'       # Gold accent
        accent_gold_dark = '#daa520'  # Darker gold for hover
        text_inactive = '#a0a0a0'     # Inactive tab text
        
        # Configure Notebook (tabs) - uniform size
        style.configure("TNotebook", 
                       background=bg_dark, 
                       borderwidth=0,
                       tabmargins=[0, 0, 0, 0])
        
        # Tab styling - FIXED WIDTH AND HEIGHT for consistency
        style.configure("TNotebook.Tab", 
                       background=bg_secondary,
                       foreground=text_inactive,
                       borderwidth=0,
                       padding=[30, 12],  # Fixed padding for uniform size
                       font=('Helvetica', 10, 'normal'))
        
        # Tab state styling - gold for active, gray for inactive
        style.map("TNotebook.Tab",
                 background=[("selected", bg_tertiary), ("!selected", bg_secondary)],
                 foreground=[("selected", accent_gold), ("!selected", text_inactive)],
                 expand=[("selected", [0, 0, 0, 0])],  # No expansion on selection
                 padding=[("selected", [30, 12]), ("!selected", [30, 12])])  # Same padding always
        
        # Frame styling
        style.configure("TFrame", background=bg_dark, borderwidth=0)
        
        # LabelFrame styling - gold borders and labels
        style.configure("TLabelframe", 
                       background=bg_dark,
                       bordercolor=accent_gold,
                       borderwidth=1,
                       relief='solid')
        style.configure("TLabelframe.Label", 
                       background=bg_dark,
                       foreground=accent_gold,
                       font=('Helvetica', 10, 'bold'))
        
        # Label styling
        style.configure("TLabel", 
                       background=bg_dark,
                       foreground=text_color,
                       padding=6,
                       font=('Helvetica', 10))
        
        # Entry styling
        style.configure("TEntry", 
                       fieldbackground=bg_secondary,
                       foreground=text_color,
                       bordercolor=border_color,
                       lightcolor=border_color,
                       darkcolor=border_color,
                       borderwidth=1,
                       insertcolor=accent_gold)
        style.map("TEntry",
                 fieldbackground=[("focus", bg_tertiary)],
                 bordercolor=[("focus", accent_gold)])
        
        # Button styling
        style.configure("TButton",
                       background=bg_secondary,
                       foreground=text_color,
                       bordercolor=accent_gold,
                       lightcolor=accent_gold,
                       darkcolor=accent_gold,
                       borderwidth=1,
                       padding=6,
                       font=('Helvetica', 10))
        style.map("TButton",
                 background=[("active", bg_tertiary), ("pressed", accent_gold_dark)],
                 foreground=[("active", accent_gold)],
                 bordercolor=[("focus", accent_gold)])
        
        # Radiobutton styling
        style.configure("TRadiobutton",
                       background=bg_dark,
                       foreground=text_color,
                       bordercolor=border_color,
                       font=('Helvetica', 10))
        style.map("TRadiobutton",
                 background=[("active", bg_dark)],
                 foreground=[("active", accent_gold)])
        
        # Menubutton (OptionMenu) styling
        style.configure("TMenubutton",
                       background=bg_secondary,
                       foreground=text_color,
                       bordercolor=accent_gold,
                       borderwidth=1,
                       padding=6,
                       font=('Helvetica', 10))
        style.map("TMenubutton",
                 background=[("active", bg_tertiary)],
                 foreground=[("active", accent_gold)])
        
        # Progressbar styling
        style.configure("TProgressbar",
                       troughcolor=bg_secondary,
                       background=accent_gold,
                       bordercolor=accent_gold,
                       lightcolor=accent_gold,
                       darkcolor=accent_gold,
                       borderwidth=1)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Single download tab
        self.single_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.single_tab, text="📹 Single Download")

        # Single download panel
        self.single_panel = SingleDownloadPanel(self.single_tab)
        self.single_panel.pack(expand=True, fill=tk.BOTH)

        # Batch download tab
        self.batch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_tab, text="📂 Batch Download")

        # Batch download panel
        self.batch_panel = BatchDownloadPanel(self.batch_tab)
        self.batch_panel.pack(expand=True, fill=tk.BOTH)

def run_gui():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
