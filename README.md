# TubeHarvester

A modern NiceGUI web application for downloading YouTube videos, audio, playlists, and channels.

## Features

- Modern, responsive web interface built with NiceGUI and styled with the Orange and Dark Soft design system
- Download individual YouTube videos with dynamic resolution selection (4K, 1080p, 720p, 480p, 360p)
- Convert and extract audio to MP3 format
- Batch download entire YouTube playlists and channel uploads in parallel
- Support for YouTube mix playlists and various channel URL formats
- Automatic browser cookie discovery for authenticated requests
- Real-time download progress bars and live activity console logging
- Decoupled backend architecture in `src/extraction/` with clean callback contracts

## Project Structure

```
TubeHarvester/
├── LICENSE
├── main.py
├── pyproject.toml
├── README.md
├── requirements.txt
├── run_tests.py
├── src/
│   ├── __init__.py
│   ├── extraction/
│   │   ├── __init__.py
│   │   ├── batch_downloader.py
│   │   ├── channel_scraper.py
│   │   ├── cookie_manager.py
│   │   ├── mp3_downloader.py
│   │   ├── mp4_downloader.py
│   │   ├── playlist_scraper.py
│   │   └── utils.py
│   └── ui/
│       ├── __init__.py
│       ├── app.py
│       ├── theme.py
│       ├── components/
│       │   ├── __init__.py
│       │   ├── format_picker.py
│       │   ├── header.py
│       │   ├── log_console.py
│       │   ├── nav_tabs.py
│       │   ├── path_selector.py
│       │   ├── progress.py
│       │   └── url_input.py
│       └── views/
│           ├── __init__.py
│           ├── batch_view.py
│           └── single_view.py
└── tests/
    ├── __init__.py
    ├── test_batch_downloader.py
    ├── test_batch_mp3_downloading.py
    ├── test_channel_scraper.py
    ├── test_cookie_manager.py
    ├── test_mp3_converter.py
    ├── test_mp4_converter.py
    ├── test_playlist_scraper.py
    ├── test_playlist_url_handling.py
    ├── test_ui_components.py
    └── test_youtube_mix_playlists.py
```

## Installation

### Prerequisites
- Python 3.9+
- FFmpeg

### Install FFmpeg
```bash
sudo apt install ffmpeg  # Debian/Ubuntu
```

### Install with pip / pipx

Install the package directly in editable mode:

```bash
pip install -e .
```

For development dependencies:

```bash
pip install -e ".[dev]"
```

### Setup Python Environment (Alternative)
```bash
pip install -r requirements.txt
```

Or with conda:
```bash
conda activate py14
pip install -r requirements.txt
```

### Run the Application

Launch the NiceGUI web app:

```bash
python3 main.py
```

Or when installed as a package:

```bash
tubeharvester
```

The web interface will be accessible at `http://127.0.0.1:8080`.

## Running Tests

Run the full pytest suite:

```bash
python run_tests.py
```

Or directly with pytest:

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
