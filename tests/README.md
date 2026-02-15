# Tests Directory

## Directory Summary

This directory contains comprehensive unit tests for the TubeHarvester YouTube downloader application. The test suite uses pytest and unittest.mock to validate functionality across all major modules including downloaders, scrapers, batch operations, cookie management, and the GUI. Tests ensure reliability through mocking external dependencies and validating edge cases.

## Documentation Index

- [`__init__.py`](../docs/tests_docs/init_doc.md) — Package initializer for the test suite
- [`test_batch_downloader.py`](../docs/tests_docs/test_batch_downloader_doc.md) — Tests for concurrent batch download operations
- [`test_batch_mp3_downloading.py`](../docs/tests_docs/test_batch_mp3_downloading_doc.md) — Integration tests for batch MP3 downloads
- [`test_channel_scraper.py`](../docs/tests_docs/test_channel_scraper_doc.md) — Tests for YouTube channel content scraping
- [`test_cookie_manager.py`](../docs/tests_docs/test_cookie_manager_doc.md) — Tests for browser cookie extraction functionality
- [`test_gui.py`](../docs/tests_docs/test_gui_doc.md) — Tests for graphical user interface components
- [`test_mp3_converter.py`](../docs/tests_docs/test_mp3_converter_doc.md) — Tests for MP3 download and conversion
- [`test_mp4_converter.py`](../docs/tests_docs/test_mp4_converter_doc.md) — Tests for MP4 download and conversion
- [`test_playlist_scraper.py`](../docs/tests_docs/test_playlist_scraper_doc.md) — Tests for YouTube playlist content scraping
- [`test_playlist_url_handling.py`](../docs/tests_docs/test_playlist_url_handling_doc.md) — Tests for playlist URL parsing and handling
- [`test_youtube_mix_playlists.py`](../docs/tests_docs/test_youtube_mix_playlists_doc.md) — Tests for YouTube Mix playlist handling
