"""
Cookie extraction and management module for YouTube authentication.

Locates local installed web browsers and leverages yt-dlp cookie extraction
capabilities to authenticate requests for age-restricted or protected media.
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Optional

logging.basicConfig(level=logging.INFO)


class CookieManager:
    """
    Manages the extraction and retrieval of YouTube cookies from local browsers.

    This class attempts to discover installed desktop browsers and extract
    authenticated session cookies into a local cookie file.
    """

    COOKIE_FILE = "yt_cookies.txt"
    BROWSERS = [
        ("brave-browser", "brave"),
        ("google-chrome", "chrome"),
        ("chromium", "chromium"),
        ("firefox", "firefox"),
        ("opera", "opera"),
        ("edge", "edge"),
    ]

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Initializes the CookieManager instance with optional logging callback.

        Args:
            log_callback (Callable[[str], None], optional): Callback function for log messages.
        """
        self.log_callback = log_callback

    def getCookieFile(self) -> Optional[str]:
        """
        Retrieves the path to the valid cookie file, extracting if absent.

        Returns:
            Optional[str]: Path string to the cookie file, or None if extraction fails.
        """
        cookie_path = Path(self.COOKIE_FILE)
        if cookie_path.exists():
            if self.log_callback:
                self.log_callback(f"Using existing cookie file: {self.COOKIE_FILE}")
            return str(cookie_path)

        if self.log_callback:
            self.log_callback("Cookie file not found. Attempting extraction from browsers.")

        # Attempts browser extraction if the cookie file does not exist locally.
        if self.extractCookies():
            return str(cookie_path)

        return None

    def extractCookies(self) -> bool:
        """
        Extracts YouTube session cookies from installed browsers via yt-dlp.

        Returns:
            bool: True if extraction succeeded and produced non-empty cookies, False otherwise.
        """
        if self.log_callback:
            self.log_callback("Attempting to extract YouTube cookies...")

        for binary_name, browser_key in self.BROWSERS:
            # Skips browsers that are not detected in the system PATH.
            if not shutil.which(binary_name):
                continue

            if self.log_callback:
                self.log_callback(f"Found {browser_key}, attempting extraction...")

            try:
                # Executes yt-dlp cookie extraction subprocess with a browser profile key.
                result = subprocess.run(
                    [
                        "yt-dlp",
                        "--cookies-from-browser", browser_key,
                        "--cookies", self.COOKIE_FILE,
                        "--user-agent", (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                        ),
                    ],
                    capture_output=True,
                    timeout=15,
                    text=True,
                )

                # Validates that the command exited cleanly and the created file has content.
                if result.returncode == 0 and Path(self.COOKIE_FILE).exists():
                    if Path(self.COOKIE_FILE).stat().st_size > 0:
                        if self.log_callback:
                            self.log_callback(f"Successfully extracted cookies from {browser_key}")
                        return True
                    else:
                        # Deletes empty files generated from failed extraction attempts.
                        Path(self.COOKIE_FILE).unlink()

            except Exception as exc:
                if self.log_callback:
                    self.log_callback(f"Error extracting from {browser_key}: {type(exc).__name__}")

        if self.log_callback:
            self.log_callback("Failed to extract cookies from any browser.")
        return False
