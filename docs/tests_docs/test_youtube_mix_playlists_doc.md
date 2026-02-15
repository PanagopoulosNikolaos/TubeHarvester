# test_youtube_mix_playlists.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [testYoutubeMixDetection](#testyoutubemixdetection) | Function | Validates the identification logic for algorithmic playlist IDs. |
| [testUrlNormalization](#testurlnormalization) | Function | Verifies URL cleaning for mix-type playlists. |
| [testActualYoutubeAccess](#testactualyoutubeaccess) | Function | Performs an integration test against live YouTube mix data. |

## Overview
The `test_youtube_mix_playlists.py` file focuses on the specialized logic required to handle YouTube's "Mix" and algorithmic playlists. These playlists differ from user-created ones in their ID structure (e.g., starting with `RD`) and require alternative scraping strategies.

## testYoutubeMixDetection

**Primary Library:** `src.PlaylistScraper`  
**Purpose:** Validates the regex or prefix-based identification of algorithmic playlist IDs.

#### Overview
This test ensures that the `PlaylistScraper` can accurately distinguish between standard playlist IDs (starting with `PL`, `UU`, `UC`) and various forms of YouTube-generated mix IDs (starting with `RD`, `RDCL`, `RDAM`, etc.).

#### Signature
```python
def testYoutubeMixDetection() -> bool
```

#### Workflow (Executable Logic Only)

**Phase 1: Mix ID Validation**
Iterates through a set of known mix ID prefixes.
* **Line 24-29:** Asserts that `scraper.isYoutubeMix()` returns `True` for each.

**Phase 2: Standard ID Validation**
Iterates through non-mix IDs to prevent false positives.
* **Line 31-36:** Asserts that `scraper.isYoutubeMix()` returns `False` for standard prefixes.

#### Source Code
```python
def testYoutubeMixDetection():
    """Test that the scraper can detect YouTube mix URLs."""
    scraper = PlaylistScraper()
    
    # Test various YouTube mix prefixes
    mix_ids = ['RDxxxx', 'RDExxxx', 'RDCLxxxx', 'RDCLAKxxxx', 'RDAMVMxxxx', 'RDCMxxxx']
    non_mix_ids = ['PLxxxx', 'UUxxxx', 'UCxxxx']
    
    print("Testing YouTube mix detection...")
    
    for mix_id in mix_ids:
        result = scraper.isYoutubeMix(mix_id)
        print(f" {mix_id}: {'✓' if result else '✗'} (expected: ✓)")
        if not result:
            print(f"    ERROR: Failed to detect {mix_id} as a mix")
            return False
    
    for non_mix_id in non_mix_ids:
        result = scraper.isYoutubeMix(non_mix_id)
        print(f" {non_mix_id}: {'✗' if result else '✓'} (expected: ✓)")
        if result:
            print(f"    ERROR: Incorrectly detected {non_mix_id} as a mix")
            return False
    
    print("✓ YouTube mix detection working correctly")
    assert True
```

---

## testUrlNormalization

**Purpose:** Verifies that URLs containing mix parameters are correctly formatted for the scraper.

**Implementation (Executable Logic Only):**
* **Line 46-47:** Normalizes a URL containing both a video ID (`watch?v=xxx`) and a mix ID (`&list=RD...`).
* **Line 52-53:** Normalizes a standard `/playlist?list=PL` URL.
* **Line 57:** Asserts success.

---

## testActualYoutubeAccess

**Primary Library:** `src.PlaylistScraper`  
**Purpose:** Verifies real-world connectivity and parsing for highly dynamic mix playlists.

#### Overview
This test attempts to scrape a live YouTube mix. Because mixes are algorithmic and can be region-locked or blocked by anti-bot measures, the test includes extensive logging and exception handling to provide context on failure without necessarily breaking the test suite.

#### Workflow (Executable Logic Only)
* **Line 70:** Attempts to retrieve the title of a live mix.
* **Line 74:** Attempts to scrape the first 5 videos from the mix.
* **Line 81-88:** Catches network or restriction errors and logs them with categorized explanations (anti-bot, region-lock, etc.).
```
