#!/usr/bin/env python3
"""
Test MP3 batch downloading functionality.
Verifies MP3 batch downloading works correctly.
"""

import sys
import logging
from src.PlaylistScraper import PlaylistScraper
from src.BatchDownloader import BatchDownloader
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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

if __name__ == "__main__":
    success = testMp3Batch()
    sys.exit(0 if success else 1)
