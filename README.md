# TubeHarvester

A Python application for downloading YouTube videos, audio, playlists, and channels.

## Features

- Download individual YouTube videos
- Convert videos to MP3 or MP4 formats
- Batch download multiple videos
- Scrape and download entire YouTube playlists
- Scrape and download all videos from a YouTube channel
- Simple graphical user interface (GUI)

## Project Structure

```
TubeHarvester/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── LICENSE                # License information
├── run_tests.py           # Test runner
├── .gitignore             # Git ignore rules
├── src/                   # Source code directory
│   ├── __init__.py        # Package initialization
│   ├── BatchDownloader.py # Batch download functionality
│   ├── ChannelScraper.py  # YouTube channel scraping
│   ├── GUI.py            # Graphical user interface
│   ├── Mp3_Converter.py  # MP3 conversion functionality
│   ├── Mp4_Converter.py  # MP4 conversion functionality
│   └── PlaylistScraper.py # YouTube playlist scraping
└── tests/                 # Test files directory
    ├── __init__.py        # Package initialization
    ├── test_batch_downloader.py
    ├── test_channel_scraper.py
    ├── test_gui.py
    ├── test_mp3_converter.py
    ├── test_mp4_converter.py
    └── test_playlist_scraper.py
```

## Installation

### Prerequisites
- Python 3.x
- FFmpeg

### Install FFmpeg
```bash
sudo apt install ffmpeg  # Debian/Ubuntu
```

### Setup Python Environment
```bash
pip install -r requirements.txt
```

Or with conda:
```bash
conda activate base_env
pip install -r requirements.txt
```

### Run the Application
```bash
python3 main.py
```

Or with conda:
```bash
conda activate base_env && python main.py
```

## Usage

The GUI will launch, allowing to enter YouTube URLs and select download options.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
