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
├── LICENSE
├── main.py
├── README.md
├── requirements.txt
├── run_tests.py
├── src
│   ├── BatchDownloader.py
│   ├── ChannelScraper.py
│   ├── GUI.py
│   ├── __init__.py
│   ├── Mp3_Converter.py
│   ├── Mp4_Converter.py
│   ├── PlaylistScraper.py
└── tests
    ├── __init__.py
    ├── test_batch_downloader.py
    ├── test_batch_mp3_downloading.py
    ├── test_channel_scraper.py
    ├── test_gui.py
    ├── test_mp3_converter.py
    ├── test_mp4_converter.py
    ├── test_playlist_scraper.py
    ├── test_playlist_url_handling.py
    └── test_youtube_mix_playlists.py
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
