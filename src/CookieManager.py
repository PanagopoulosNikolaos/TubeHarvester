import subprocess
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

class CookieManager:
    """
    Manages the extraction and retrieval of YouTube cookies from local browsers.

    This class attempts to find installed browsers and use yt-dlp's built-in
    cookie extraction to create a cookie file for authenticated requests.
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

    def __init__(self, log_callback=None):
        """
        Initializes the CookieManager.

        Args:
            log_callback (callable, optional): Called with log messages.
        """
        self.log_callback = log_callback

    def getCookieFile(self):
        """
        Gets the path to the cookie file, extracting if necessary.

        Returns:
            str: Path to the cookie file or None if extraction fails.
        """
        cookie_path = Path(self.COOKIE_FILE)
        if cookie_path.exists():
            if self.log_callback:
                self.log_callback(f"Using existing cookie file: {self.COOKIE_FILE}")
            return str(cookie_path)
        
        if self.log_callback:
            self.log_callback("Cookie file not found. Attempting extraction from browsers.")
        
        if self.extractCookies():
            return str(cookie_path)
        
        return None

    def extractCookies(self):
        """
        Extracts YouTube cookies from installed browsers using yt-dlp.

        Returns:
            bool: True if extraction was successful, False otherwise.
        """
        if self.log_callback:
            self.log_callback("Attempting to extract YouTube cookies...")

        for binary, name in self.BROWSERS:
            if not shutil.which(binary):
                continue

            if self.log_callback:
                self.log_callback(f"Found {name}, attempting extraction...")

            try:
                # Use --user-agent for consistency with downloader options
                result = subprocess.run(
                    [
                        "yt-dlp",
                        "--cookies-from-browser", name,
                        "--cookies", self.COOKIE_FILE,
                        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    ],
                    capture_output=True,
                    timeout=15,
                    text=True
                )

                if result.returncode == 0 and Path(self.COOKIE_FILE).exists():
                    if Path(self.COOKIE_FILE).stat().st_size > 0:
                        if self.log_callback:
                            self.log_callback(f"Successfully extracted cookies from {name}")
                        return True
                    else:
                        Path(self.COOKIE_FILE).unlink()

            except Exception as e:
                if self.log_callback:
                    self.log_callback(f"Error extracting from {name}: {type(e).__name__}")

        if self.log_callback:
            self.log_callback("Failed to extract cookies from any browser.")
        return False
