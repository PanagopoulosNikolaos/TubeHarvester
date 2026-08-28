"""
Concurrent batch downloader module for processing multi-video queues.

Coordinates parallel download tasks via ThreadPoolExecutor with progress tracking,
error reporting, and thread-safe cancellation support.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import os
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

from .mp3_downloader import Mp3Downloader
from .mp4_downloader import Mp4Downloader
from .utils import sanitizeFilename


class BatchDownloader:
    """
    Manages concurrent downloads of multiple YouTube videos.

    Uses a ThreadPoolExecutor to handle multiple downloads in parallel,
    tracking overall progress and supporting clean cancellation.
    """

    def __init__(
        self,
        max_workers: int = 3,
        progress_callback: Optional[Callable[[int], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initializes the BatchDownloader with thread pool configuration.

        Args:
            max_workers (int): Maximum number of concurrent downloads (default: 3).
            progress_callback (Optional[Callable[[int], None]], optional): Progress callback.
            log_callback (Optional[Callable[[str], None]], optional): Status message callback.
        """
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_event = threading.Event()
        self.total_videos = 0
        self.completed_videos = 0
        self.lock = threading.Lock()
        self.last_progress_update = 0

    def downloadBatch(
        self,
        video_list: List[Dict[str, Any]],
        format_type: str,
        base_path: str,
        quality: str = "highest",
    ) -> Dict[str, Any]:
        """
        Downloads a list of videos concurrently using worker threads.

        Args:
            video_list (List[Dict[str, Any]]): List of dicts: [{'url': str, 'title': str, 'folder': str}, ...].
            format_type (str): Output format ('MP4' or 'MP3').
            base_path (str): Root destination directory.
            quality (str): Video quality setting (default: 'highest').

        Returns:
            Dict[str, Any]: Summary dictionary: {'successful': int, 'failed': int, 'errors': list}.
        """
        self.total_videos = len(video_list)
        self.completed_videos = 0
        self.cancel_event.clear()

        results: Dict[str, Any] = {
            'successful': 0,
            'failed': 0,
            'errors': [],
        }

        if not video_list:
            if self.log_callback:
                self.log_callback("No videos to download")
            return results

        if self.log_callback:
            self.log_callback(f"Starting batch download of {self.total_videos} videos in {format_type} format")

        organized_paths = self.createFolderStructure(video_list, base_path, format_type)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_video: Dict[Any, Dict[str, Any]] = {}
            for video_info in video_list:
                # Checks if cancellation was requested before scheduling next worker.
                if self.cancel_event.is_set():
                    break

                folder_path = organized_paths.get(video_info.get('folder', ''), base_path)
                future = executor.submit(
                    self.downloadSingleVideo,
                    video_info,
                    format_type,
                    folder_path,
                    quality,
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
                                self.log_callback(
                                    f"Download progress: {bar} {progress_percent}% "
                                    f"({self.completed_videos}/{self.total_videos} videos)"
                                )

                except Exception as exc:
                    with self.lock:
                        self.completed_videos += 1
                        results['failed'] += 1
                        results['errors'].append(f"{video_info['title']}: {str(exc)}")
                        if self.log_callback:
                            self.log_callback(f"Error: {video_info['title']} - {str(exc)}")

                        overall_progress = (self.completed_videos / self.total_videos) * 100
                        if self.progress_callback:
                            self.progress_callback(int(overall_progress))

        if self.cancel_event.is_set():
            if self.log_callback:
                self.log_callback("Batch download cancelled")
        else:
            if self.log_callback:
                self.log_callback(
                    f"Batch download completed: {results['successful']} successful, "
                    f"{results['failed']} failed"
                )

        return results

    def cancelDownload(self) -> None:
        """
        Signals cancellation to terminate pending batch download jobs.
        """
        self.cancel_event.set()
        if self.log_callback:
            self.log_callback("Cancelling batch download...")

    def downloadSingleVideo(
        self,
        video_info: Dict[str, Any],
        format_type: str,
        folder_path: str,
        quality: str,
    ) -> Tuple[bool, str]:
        """
        Downloads an individual video item according to format and quality configuration.

        Args:
            video_info (Dict[str, Any]): Video item dictionary containing url and title.
            format_type (str): Target format ('MP4' or 'MP3').
            folder_path (str): Target directory path.
            quality (str): Quality string.

        Returns:
            Tuple[bool, str]: Tuple of (success_status, error_message).
        """
        try:
            sanitized_title = sanitizeFilename(video_info['title'])

            if format_type.upper() == 'MP4':
                downloader = Mp4Downloader()
                downloader.setUrl(video_info['url'])
                downloader.setPath(folder_path)

                if quality and quality.lower() != "highest":
                    try:
                        # Parses numerical resolution height (e.g., '720p' -> 720).
                        resolution_digits = ''.join(filter(str.isdigit, quality))
                        if resolution_digits:
                            downloader.resolution = resolution_digits
                    except Exception:
                        pass
                downloader.downloadVideo(custom_title=sanitized_title)

            elif format_type.upper() == 'MP3':
                downloader = Mp3Downloader()
                downloader.setUrl(video_info['url'])
                downloader.setPath(folder_path)
                downloader.downloadAsMp3(custom_title=sanitized_title)

            else:
                raise ValueError(f"Unsupported format: {format_type}")

            return True, ""

        except Exception as exc:
            return False, str(exc)

    def createFolderStructure(
        self,
        video_list: List[Dict[str, Any]],
        base_path: str,
        format_type: str,
    ) -> Dict[str, str]:
        """
        Creates subdirectories on disk organized by folder keys and format.

        Args:
            video_list (List[Dict[str, Any]]): List of video metadata items.
            base_path (str): Root destination directory.
            format_type (str): Selected format ('MP4' or 'MP3').

        Returns:
            Dict[str, str]: Mapping from folder identifiers to absolute directory paths.
        """
        organized_paths: Dict[str, str] = {}

        if format_type.upper() == 'MP3':
            root_folder = os.path.join(base_path, "Music")
        else:
            root_folder = os.path.join(base_path, "Videos")

        folder_groups: Dict[str, List[Dict[str, Any]]] = {}
        for video in video_list:
            item_folder = video.get('folder', '')
            if item_folder not in folder_groups:
                folder_groups[item_folder] = []
            folder_groups[item_folder].append(video)

        for item_folder in folder_groups:
            if item_folder:
                full_path = os.path.join(root_folder, item_folder)
            else:
                full_path = root_folder

            os.makedirs(full_path, exist_ok=True)
            organized_paths[item_folder] = full_path

        return organized_paths
