
import subprocess
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

class CookieManager:
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
        Initialize the CookieManager with an optional log callback.

        Args:
            log_callback (callable): Function to call with log messages
        """
        self.log_callback = log_callback

    def get_cookie_file(self):
        """
        Get the path to the cookie file, creating it if it doesn't exist.

        Returns:
            str or None: Path to the cookie file if it exists or can be created, None otherwise
        """
        cookie_path = Path(self.COOKIE_FILE)
        if cookie_path.exists():
            if self.log_callback:
                self.log_callback(f"Using existing cookie file: {self.COOKIE_FILE}")
            return str(cookie_path)
        
        if self.log_callback:
            self.log_callback("Cookie file not found. Attempting to extract cookies from browsers.")
        if self.extract_cookies():
            return str(cookie_path)
        
        return None

    def extract_cookies(self):
        """
        Extract YouTube cookies from installed browsers.

        Returns:
            bool: True if cookies were successfully extracted, False otherwise
        """
        if self.log_callback:
            self.log_callback("Attempting to extract YouTube cookies...")

        for binary, name in self.BROWSERS:
            if not shutil.which(binary):
                if self.log_callback:
                    self.log_callback(f"Browser '{name}' not found. Skipping.")
                continue

            if self.log_callback:
                self.log_callback(f"Found {name}, attempting extraction...")

            try:
                # no URL specification, yt-dlp will extract all cookies
                result = subprocess.run(
                    ["yt-dlp", "--cookies-from-browser", name, "--cookies", self.COOKIE_FILE],
                    capture_output=True,
                    timeout=15,
                    text=True
                )

                if result.returncode == 0 and Path(self.COOKIE_FILE).exists():
                    # check if the cookie file is not empty
                    if Path(self.COOKIE_FILE).stat().st_size > 0:
                        if self.log_callback:
                            self.log_callback(f"Successfully extracted cookies from {name} to {self.COOKIE_FILE}")
                        return True
                    else:
                        if self.log_callback:
                            self.log_callback(f"Extracted an empty cookie file from {name}. Trying next browser.")
                        Path(self.COOKIE_FILE).unlink() # remove empty file to avoid using it
                else:
                    if self.log_callback:
                        error_message = result.stderr.strip() if result.stderr else "Unknown error"
                        self.log_callback(f"Failed to extract from {name}: {error_message}")

            except (subprocess.TimeoutExpired, Exception) as e:
                if self.log_callback:
                    self.log_callback(f"Error with {name}: {type(e).__name__}")

        if self.log_callback:
            self.log_callback("Failed to extract cookies from any browser.")
        return False
