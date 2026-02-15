# test_playlist_url_handling.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [testPlaylistScraping](#testplaylistscraping) | Function | Tests scraping logic for various YouTube playlist URL formats. |

## Overview
This file contains a test script designed to verify the robust handling of different YouTube playlist URL formats. It ensures that the `PlaylistScraper` can correctly identify and process both direct playlist links and video links that contain a playlist parameter (`&list=...`).

## testPlaylistScraping

**Primary Library:** `src.PlaylistScraper`  
**Purpose:** Validates that playlist scraping works across multiple URL representation formats.

#### Overview
This function performs an integration test by scraping a live YouTube playlist using two different URL formats. It validates that the scraper is able to resolve both formats to the same playlist metadata, retrieving the title and a snippet of the video list.

#### Signature
```python
def testPlaylistScraping() -> None
```

#### Returns
| Type | Description |
|------|-------------|
| None | Function returns None but prints results and exceptions. |

#### Dependencies
* **Internal Modules:** `PlaylistScraper.getPlaylistTitle` (Extracts title), `PlaylistScraper.scrapePlaylist` (Extracts video list).

#### Workflow (Executable Logic Only)

**Phase 1: Video URL with Parameter**
Tests the extraction from a URL of a specific video within a playlist.
* **Line 36:** Fetches the playlist title using the video URL.
* **Line 41:** Scrapes the first 5 videos.
* **Line 43-48:** Validates that videos were found and prints their metadata.

**Phase 2: Direct Playlist URL**
Tests the extraction from a standard dedicated playlist page URL.
* **Line 65:** Fetches the playlist title using the direct link.
* **Line 70:** Scrapes the first 5 videos.
* **Line 72-77:** Validates that the same metadata (implicitly) is found via this direct path.

#### Source Code
```python
def testPlaylistScraping():
    """Test playlist scraping with both URL formats."""
    
    # Video URL with playlist parameter
    video_url_with_playlist = "https://www.youtube.com/watch?v=zk3T2qtK2B0&list=PLrxcNWZXdQ2l9Jnr8-thveoeoQlBUSFOw"
    
    # Direct playlist URL format
    direct_playlist_url = "https://www.youtube.com/playlist?list=PLrxcNWZXdQ2l9Jnr8-thveoeoQlBUSFOw"
    
    print("=" * 80)
    print("Testing Playlist Scraping Fix")
    print("=" * 80)
    
    scraper = PlaylistScraper(timeout=0.5)  # Shorter timeout for testing
    
    # Test 1: Video URL with playlist parameter
    print("\n[TEST 1] Testing with video URL containing playlist parameter:")
    print(f"URL: {video_url_with_playlist}")
    print("-" * 80)
    
    try:
        # Get playlist title
        title = scraper.getPlaylistTitle(video_url_with_playlist)
        print(f"Playlist Title: {title}")
        
        # Scrape first 5 videos as a test
        print("\nScraping first 5 videos...")
        videos = scraper.scrapePlaylist(video_url_with_playlist, max_videos=5)
        
        if videos:
            print(f"\n✓ SUCCESS! Found {len(videos)} videos:")
            for i, video in enumerate(videos, 1):
                print(f"  {i}. {video['title']}")
                print(f"     URL: {video['url']}")
                print(f"     Duration: {video['duration']} seconds")
        else:
            print("\n✗ FAILED! No videos found.")
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Direct playlist URL
    print("\n" + "=" * 80)
    print("[TEST 2] Testing with direct playlist URL:")
    print(f"URL: {direct_playlist_url}")
    print("-" * 80)
    
    try:
        # Get playlist title
        title = scraper.getPlaylistTitle(direct_playlist_url)
        print(f"Playlist Title: {title}")
        
        # Scrape first 5 videos as a test
        print("\nScraping first 5 videos...")
        videos = scraper.scrapePlaylist(direct_playlist_url, max_videos=5)
        
        if videos:
            print(f"\n✓ SUCCESS! Found {len(videos)} videos:")
            for i, video in enumerate(videos, 1):
                print(f"  {i}. {video['title']}")
                print(f"     URL: {video['url']}")
                print(f"     Duration: {video['duration']} seconds")
        else:
            print("\n✗ FAILED! No videos found.")
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
```
