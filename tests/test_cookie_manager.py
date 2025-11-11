
import pytest
from unittest.mock import patch, Mock
from src.CookieManager import CookieManager
from pathlib import Path

class TestCookieManager:
    def setup_method(self):
        self.cookie_manager = CookieManager()

    @patch('pathlib.Path.exists')
    def test_get_cookie_file_exists(self, mock_exists):
        mock_exists.return_value = True
        cookie_file = self.cookie_manager.get_cookie_file()
        assert cookie_file == "yt_cookies.txt"

    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_get_cookie_file_extracts_successfully(self, mock_stat, mock_exists, mock_subprocess_run, mock_shutil_which):
        mock_exists.side_effect = [False, True] # First call in get_cookie_file, second in extract_cookies
        mock_shutil_which.return_value = True
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_stat.return_value = Mock(st_size=100) # Simulate non-empty file
        
        cookie_file = self.cookie_manager.get_cookie_file()
        assert cookie_file == "yt_cookies.txt"
        mock_subprocess_run.assert_called_once()

    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_get_cookie_file_extraction_fails(self, mock_exists, mock_subprocess_run, mock_shutil_which):
        mock_exists.return_value = False
        mock_shutil_which.return_value = True
        mock_subprocess_run.return_value = Mock(returncode=1, stderr="error")
        
        cookie_file = self.cookie_manager.get_cookie_file()
        assert cookie_file is None
        assert mock_subprocess_run.call_count == len(self.cookie_manager.BROWSERS)

    @patch('shutil.which', return_value=False)
    def test_extract_cookies_no_browsers_found(self, mock_shutil_which):
        assert self.cookie_manager.extract_cookies() is False

    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.unlink')
    def test_extract_cookies_empty_file(self, mock_unlink, mock_stat, mock_exists, mock_subprocess_run, mock_shutil_which):
        mock_shutil_which.return_value = True
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_stat.return_value = Mock(st_size=0) # Simulate empty file

        assert self.cookie_manager.extract_cookies() is False
        assert mock_unlink.called
