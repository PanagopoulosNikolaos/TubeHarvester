"""
Unit tests for CookieManager module.
"""

from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from src.extraction.cookie_manager import CookieManager


class TestCookieManager:
    """
    Test suite verifying cookie file retrieval and browser extraction behaviors.
    """

    def setup_method(self) -> None:
        """
        Initializes the CookieManager test subject.
        """
        self.cookie_manager = CookieManager()

    @patch('pathlib.Path.exists')
    def testGetCookieFileExists(self, mock_exists: Mock) -> None:
        """
        Tests retrieving existing cookie file without triggering browser extraction.
        """
        mock_exists.return_value = True
        cookie_file = self.cookie_manager.getCookieFile()
        assert cookie_file == "yt_cookies.txt"

    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def testGetCookieFileExtractsSuccessfully(
        self,
        mock_stat: Mock,
        mock_exists: Mock,
        mock_subprocess_run: Mock,
        mock_shutil_which: Mock,
    ) -> None:
        """
        Tests extracting cookies when cookie file is initially missing.
        """
        mock_exists.side_effect = [False, True]
        mock_shutil_which.return_value = True
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_stat.return_value = Mock(st_size=100)

        cookie_file = self.cookie_manager.getCookieFile()
        assert cookie_file == "yt_cookies.txt"
        mock_subprocess_run.assert_called_once()

    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def testGetCookieFileExtractionFails(
        self,
        mock_exists: Mock,
        mock_subprocess_run: Mock,
        mock_shutil_which: Mock,
    ) -> None:
        """
        Tests return value when browser extraction fails across all browsers.
        """
        mock_exists.return_value = False
        mock_shutil_which.return_value = True
        mock_subprocess_run.return_value = Mock(returncode=1, stderr="error")

        cookie_file = self.cookie_manager.getCookieFile()
        assert cookie_file is None
        assert mock_subprocess_run.call_count == len(self.cookie_manager.BROWSERS)

    @patch('shutil.which', return_value=False)
    def testExtractCookiesNoBrowsersFound(self, mock_shutil_which: Mock) -> None:
        """
        Tests failure when no supported browser binaries exist on system.
        """
        assert self.cookie_manager.extractCookies() is False

    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.unlink')
    def testExtractCookiesEmptyFile(
        self,
        mock_unlink: Mock,
        mock_stat: Mock,
        mock_exists: Mock,
        mock_subprocess_run: Mock,
        mock_shutil_which: Mock,
    ) -> None:
        """
        Tests that empty extracted cookie files are removed and return False.
        """
        mock_shutil_which.return_value = True
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_stat.return_value = Mock(st_size=0)

        assert self.cookie_manager.extractCookies() is False
        assert mock_unlink.called
