import os
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
from .Mp4_Converter import YouTubeDownloader
from .Mp3_Converter import MP3Downloader

class BatchDownloader:
    def __init__(self, max_workers=3, progress_callback=None, log_callback=None):
        """
        Initialize the BatchDownloader.

        Parameters
        ----------
        max_workers : int
            Maximum number of concurrent downloads (default: 3)
        progress_callback : callable
            Function to call with overall progress percentage
        log_callback : callable
            Function to call with log messages
        """
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_event = threading.Event()
        self.total_videos = 0
        self.completed_videos = 0
        self.lock = threading.Lock()

    def download_batch(self, video_list, format_type, base_path, quality="highest"):
        """
        Download a batch of videos.

        Parameters
        ----------
        video_list : list
            List of video info dictionaries: [{'url': str, 'title': str, 'folder': str}, ...]
        format_type : str
            'MP4' or 'MP3'
        base_path : str
            Base directory for downloads
        quality : str
            Quality setting ('highest', 'best', etc.)

        Returns
        -------
        dict
            Results summary: {'successful': int, 'failed': int, 'errors': [str, ...]}
        """
        self.total_videos = len(video_list)
        self.completed_videos = 0
        self.cancel_event.clear()

        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        if not video_list:
            if self.log_callback:
                self.log_callback("No videos to download")
            return results

        if self.log_callback:
            self.log_callback(f"Starting batch download of {self.total_videos} videos in {format_type} format")

        # Create organized folder structure
        organized_paths = self._create_folder_structure(video_list, base_path, format_type)

        # Download videos concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_video = {}
            for video_info in video_list:
                if self.cancel_event.is_set():
                    break

                folder_path = organized_paths.get(video_info.get('folder', ''), base_path)
                future = executor.submit(
                    self._download_single_video,
                    video_info,
                    format_type,
                    folder_path,
                    quality
                )
                future_to_video[future] = video_info

            # Process completed downloads
            for future in as_completed(future_to_video):
                if self.cancel_event.is_set():
                    break

                video_info = future_to_video[future]
                try:
                    success, error_msg = future.result()
                    with self.lock:
                        self.completed_videos += 1
                        if success:
                            results['successful'] += 1
                            if self.log_callback:
                                self.log_callback(f"✓ Completed: {video_info['title']}")
                        else:
                            results['failed'] += 1
                            results['errors'].append(f"{video_info['title']}: {error_msg}")
                            if self.log_callback:
                                self.log_callback(f"✗ Failed: {video_info['title']} - {error_msg}")

                        # Update overall progress
                        overall_progress = (self.completed_videos / self.total_videos) * 100
                        if self.progress_callback:
                            self.progress_callback(int(overall_progress))

                except Exception as e:
                    with self.lock:
                        self.completed_videos += 1
                        results['failed'] += 1
                        results['errors'].append(f"{video_info['title']}: {str(e)}")
                        if self.log_callback:
                            self.log_callback(f"✗ Error: {video_info['title']} - {str(e)}")

        if self.cancel_event.is_set():
            if self.log_callback:
                self.log_callback("Batch download cancelled")
        else:
            if self.log_callback:
                self.log_callback(f"Batch download completed: {results['successful']} successful, {results['failed']} failed")

        return results

    def cancel_download(self):
        """Cancel the current batch download."""
        self.cancel_event.set()
        if self.log_callback:
            self.log_callback("Cancelling batch download...")

    def _download_single_video(self, video_info, format_type, folder_path, quality):
        """
        Download a single video.

        Parameters
        ----------
        video_info : dict
            Video information: {'url': str, 'title': str}
        format_type : str
            'MP4' or 'MP3'
        folder_path : str
            Path to save the video
        quality : str
            Quality setting

        Returns
        -------
        tuple
            (success: bool, error_message: str)
        """
        try:
            if format_type.upper() == 'MP4':
                downloader = YouTubeDownloader()

                downloader.set_url(video_info['url'])
                downloader.set_path(folder_path)

                # Set resolution based on quality
                if quality.lower() == 'highest':
                    # Will use the highest available resolution
                    pass  # Default behavior
                else:
                    # Could implement quality parsing here
                    pass

                downloader.download_video()

            elif format_type.upper() == 'MP3':
                downloader = MP3Downloader()

                downloader.set_url(video_info['url'])
                downloader.set_path(folder_path)
                downloader.download_as_mp3()

            else:
                raise ValueError(f"Unsupported format: {format_type}")

            return True, ""

        except Exception as e:
            return False, str(e)

    def _create_folder_structure(self, video_list, base_path, format_type):
        """
        Create organized folder structure for downloads following the plan:
        ~/Music (MP3) or ~/Videos (MP4)/ChannelName/PlaylistName/ or Random/

        Parameters
        ----------
        video_list : list
            List of video info dictionaries with 'folder' key containing 'ChannelName/PlaylistName' or 'ChannelName/Random'
        base_path : str
            Base directory path
        format_type : str
            'MP4' or 'MP3'

        Returns
        -------
        dict
            Mapping of folder identifiers to full paths
        """
        organized_paths = {}

        # Determine root folder based on format
        if format_type.upper() == 'MP3':
            root_folder = os.path.join(base_path, "Music")
        else:  # MP4
            root_folder = os.path.join(base_path, "Videos")

        # Create unique folder paths for each group of videos
        folder_groups = {}
        for video in video_list:
            folder_path = video.get('folder', '')
            if folder_path not in folder_groups:
                folder_groups[folder_path] = []
            folder_groups[folder_path].append(video)

        for folder_path, videos in folder_groups.items():
            if folder_path:
                # folder_path should be in format "ChannelName/PlaylistName" or "ChannelName/Random"
                full_path = os.path.join(root_folder, folder_path)
            else:
                # Fallback for videos without specific folder
                full_path = root_folder

            # Create directory structure if it doesn't exist
            os.makedirs(full_path, exist_ok=True)
            organized_paths[folder_path] = full_path

        return organized_paths
