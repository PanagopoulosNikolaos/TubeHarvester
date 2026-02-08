#!/usr/bin/env python3
"""
Test playlist URL handling functionality.
Verifies playlist scraping works with both video URL with playlist parameter and direct playlist URL.
"""

import sys
import logging
from src.PlaylistScraper import PlaylistScraper

# Configure logging to see any warnings/errors
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_playlist_scraping():
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
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_playlist_scraping()
