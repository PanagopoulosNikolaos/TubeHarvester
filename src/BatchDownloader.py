import os
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .Mp4_Converter import Mp4Downloader
from .Mp3_Converter import Mp3Downloader
from .utils import sanitizeFilename

class BatchDownloader:
    """
    Manages concurrent downloads of multiple YouTube videos.

    This class uses a ThreadPoolExecutor to handle multiple downloads in parallel,
    tracking overall progress and allowing for cancellation.
    """

    def __init__(self, max_workers=3, progress_callback=None, log_callback=None):
        """
        Initializes the BatchDownloader with thread management.

        Args:
            max_workers (int): Maximum number of concurrent downloads (default: 3).
            progress_callback (callable, optional): Called with overall progress percentage.
            log_callback (callable, optional): Called with log messages.
        """
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_event = threading.Event()
        self.total_videos = 0
        self.completed_videos = 0
        self.lock = threading.Lock()
        self.last_progress_update = 0

    def downloadBatch(self, video_list, format_type, base_path, quality="highest"):
        """
        Downloads a batch of videos concurrently.

        Args:
            video_list (list): List of dicts: [{'url': str, 'title': str, 'folder': str}, ...].
            format_type (str): 'MP4' or 'MP3'.
            base_path (str): Base directory for downloads.
            quality (str): Quality setting (e.g., 'highest').

        Returns:
            dict: Results summary: {'successful': int, 'failed': int, 'errors': [str, ...]}.
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

        organized_paths = self.createFolderStructure(video_list, base_path, format_type)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_video = {}
            for video_info in video_list:
                if self.cancel_event.is_set():
                    break

                folder_path = organized_paths.get(video_info.get('folder', ''), base_path)
                future = executor.submit(
                    self.downloadSingleVideo,
                    video_info,
                    format_type,
                    folder_path,
                    quality
                )
                future_to_video[future] = video_info

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
                        else:
                            results['failed'] += 1
                            results['errors'].append(f"{video_info['title']}: {error_msg}")
                            if self.log_callback:
                                self.log_callback(f"Failed: {video_info['title']} - {error_msg}")

                        overall_progress = (self.completed_videos / self.total_videos) * 100
                        if self.progress_callback:
                            self.progress_callback(int(overall_progress))

                        progress_percent = int(overall_progress)
                        if progress_percent > self.last_progress_update and (progress_percent % 5 == 0 or progress_percent == 100):
                            self.last_progress_update = progress_percent
                            if self.log_callback:
                                bar_length = 20
                                filled_length = int(bar_length * self.completed_videos // self.total_videos)
                                bar = '[' + '=' * filled_length + '>' + ' ' * (bar_length - filled_length - 1) + ']'
                                self.log_callback(f"Download progress: {bar} {progress_percent}% ({self.completed_videos}/{self.total_videos} videos)")

                except Exception as e:
                    with self.lock:
                        self.completed_videos += 1
                        results['failed'] += 1
                        results['errors'].append(f"{video_info['title']}: {str(e)}")
                        if self.log_callback:
                            self.log_callback(f"Error: {video_info['title']} - {str(e)}")

                        overall_progress = (self.completed_videos / self.total_videos) * 100
                        if self.progress_callback:
                            self.progress_callback(int(overall_progress))

        if self.cancel_event.is_set():
            if self.log_callback:
                self.log_callback("Batch download cancelled")
        else:
            if self.log_callback:
                self.log_callback(f"Batch download completed: {results['successful']} successful, {results['failed']} failed")

        return results

    def cancelDownload(self):
        """
        Cancels the current batch download operation.
        """
        self.cancel_event.set()
        if self.log_callback:
            self.log_callback("Cancelling batch download...")

    def downloadSingleVideo(self, video_info, format_type, folder_path, quality):
        """
        Downloads a single video using the appropriate converter.

        Args:
            video_info (dict): Video information: {'url': str, 'title': str}.
            format_type (str): 'MP4' or 'MP3'.
            folder_path (str): Path to save the file.
            quality (str): Quality setting.

        Returns:
            tuple: (success: bool, error_message: str).
        """
        try:
            sanitized_title = sanitizeFilename(video_info['title'])
            
            if format_type.upper() == 'MP4':
                downloader = Mp4Downloader()
                downloader.setUrl(video_info['url'])
                downloader.setPath(folder_path)
                # Resolution mapping could be improved here
                # Pass the quality parameter to set the resolution
                if quality and quality.lower() != "highest":
                    try:
                        # Extract numeric value from quality (e.g., "720p" -> 720)
                        resolution = ''.join(filter(str.isdigit, quality))
                        if resolution:
                            downloader.resolution = resolution
                    except:
                        pass  # Use default resolution if parsing fails
                downloader.downloadVideo(custom_title=sanitized_title)

            elif format_type.upper() == 'MP3':
                downloader = Mp3Downloader()
                downloader.setUrl(video_info['url'])
                downloader.setPath(folder_path)
                downloader.downloadAsMp3(custom_title=sanitized_title)

            else:
                raise ValueError(f"Unsupported format: {format_type}")

            return True, ""

        except Exception as e:
            return False, str(e)

    def createFolderStructure(self, video_list, base_path, format_type):
        """
        Creates the folder structure for organized downloads.

        Args:
            video_list (list): List of video items.
            base_path (str): Root path.
            format_type (str): 'MP4' or 'MP3'.

        Returns:
            dict: Map of folder identifiers to absolute paths.
        """
        organized_paths = {}

        if format_type.upper() == 'MP3':
            root_folder = os.path.join(base_path, "Music")
        else:
            root_folder = os.path.join(base_path, "Videos")

        folder_groups = {}
        for video in video_list:
            item_folder = video.get('folder', '')
            if item_folder not in folder_groups:
                folder_groups[item_folder] = []
            folder_groups[item_folder].append(video)

        for item_folder, videos_in_group in folder_groups.items():
            if item_folder:
                full_path = os.path.join(root_folder, item_folder)
            else:
                full_path = root_folder

            os.makedirs(full_path, exist_ok=True)
            organized_paths[item_folder] = full_path

        return organized_paths
