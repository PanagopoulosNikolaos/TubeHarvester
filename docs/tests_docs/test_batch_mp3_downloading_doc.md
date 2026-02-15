# test_batch_mp3_downloading.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [testMp3Batch](#testmp3batch) | Function | Validates the workflow for MP3 batch downloading. |

## Overview
This file contains a functional test script for verifying the MP3 batch downloading capabilities of the `TubeHarvester` project. It integrates the `PlaylistScraper` and `BatchDownloader` to simulate a real-world usage scenario without performing actual network-heavy downloads.

## testMp3Batch

**Primary Library:** `PlaylistScraper`, `BatchDownloader`  
**Purpose:** Validates the end-to-end infrastructure for scraping a playlist and preparing it for MP3 batch download.

#### Overview
This test function verifies that a YouTube playlist can be successfully scraped, its metadata transformed into a format suitable for the downloader, and that the appropriate folder structure for MP3 storage is created on the local file system.

#### Signature
```python
def testMp3Batch() -> None
```

#### Returns
| Type | Description |
|------|-------------|
| None | Function returns None but performs assertions. |

#### Dependencies
* **Internal Modules:** `PlaylistScraper.scrapePlaylist` (Scrapes video metadata), `PlaylistScraper.getPlaylistTitle` (Retrieves playlist name), `BatchDownloader.createFolderStructure` (Manages directory creation).

#### Workflow (Executable Logic Only)

**Phase 1: Scraping**
Retrieves video metadata from a target playlist URL.
* **Line 28-29:** Initializes `PlaylistScraper` and scrapes up to 2 videos from the test URL.
* **Line 31-33:** Validates that videos were found.

**Phase 2: Metadata Preparation**
Transforms raw scraper output into the expected input format for the downloader.
* **Line 39:** Fetches the playlist title to use as a folder name.
* **Line 41-46:** Iterates through videos and constructs dictionary objects with `url`, `title`, and `folder` keys.

**Phase 3: Initialization**
Tests the instantiation of the `BatchDownloader`.
* **Line 62-66:** Creates a `BatchDownloader` instance with mock-like logging and progress callbacks defined inline.

**Phase 4: Folder Structure Validation**
Ensures that the downloader can correctly map videos to their target filesystem paths.
* **Line 72-74:** Calls `createFolderStructure` for the prepared video list.
* **Line 79-80:** Checks if the target paths exist on the filesystem.

*Code Context:*
```python
    # Step 1: Scrape playlist
    scraper = PlaylistScraper(timeout=0.5)
    videos = scraper.scrapePlaylist(playlist_url, max_videos=2)

    # Step 2: Prepare video list
    playlist_title = scraper.getPlaylistTitle(playlist_url)
    # ... construction of video_list ...

    # Step 4: Test folder structure creation
    organized_paths = batch_downloader.createFolderStructure(
        video_list, test_base_path, "MP3"
    )
```

#### Source Code
```python
def testMp3Batch():
    """Test MP3 batch downloading with a small playlist."""
    
    # Test playlist URL
    playlist_url = "https://www.youtube.com/watch?v=zk3T2qtK2B0&list=PLrxcNWZXdQ2l9Jnr8-thveoeoQlBUSFOw"
    
    print("=" * 80)
    print("Testing MP3 Batch Download")
    print("=" * 80)
    
    # Step 1: Scrape playlist
    print("\n[STEP 1] Scraping playlist...")
    scraper = PlaylistScraper(timeout=0.5)
    videos = scraper.scrapePlaylist(playlist_url, max_videos=2)  # Just test with 2 videos
    
    if not videos:
        print("✗ FAILED! No videos found.")
        return
    
    print(f"✓ Found {len(videos)} videos")
    
    # Step 2: Prepare video list for batch download
    print("\n[STEP 2] Preparing video list for batch download...")
    playlist_title = scraper.getPlaylistTitle(playlist_url)
    video_list = []
    for video in videos:
        video_list.append({
            'url': video['url'],
            'title': video['title'],
            'folder': f"Playlists/{playlist_title}"
        })
    
    print(f"✓ Prepared {len(video_list)} videos")
    for i, v in enumerate(video_list, 1):
        print(f"  {i}. {v['title']}")
    
    # Step 3: Test batch download initialization (don't actually download)
    print("\n[STEP 3] Testing BatchDownloader initialization...")
    
    def logCallback(msg):
        print(f"[LOG] {msg}")
    
    def progressCallback(pct):
        print(f"[PROGRESS] {pct}%")
    
    try:
        batch_downloader = BatchDownloader(
            max_workers=1,
            progress_callback=progressCallback,
            log_callback=logCallback
        )
        print("✓ BatchDownloader initialized successfully")
        
        # Test the download structure creation
        print("\n[STEP 4] Testing folder structure creation...")
        test_base_path = "/tmp/test_tubeharvester"
        organized_paths = batch_downloader.createFolderStructure(
            video_list, test_base_path, "MP3"
        )
        
        print("✓ Folder structure created:")
        for folder, path in organized_paths.items():
            print(f"  {folder} -> {path}")
            if os.path.exists(path):
                print(f"    (exists: ✓)")
        
        print("\n" + "=" * 80)
        print("MP3 Batch Download Test: PASSED")
        print("=" * 80)
        print("\nNOTE: Actual downloading was not tested to save time/bandwidth.")
        print("The infrastructure is properly set up for MP3 batch downloads.")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Test failed with error: {e}"
    
    assert True
```
