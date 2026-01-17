# iTunes to Navidrome Playlist Converter

A fully interactive Python utility to migrate iTunes playlists for use with Navidrome music server running in Docker.

## The Problem

When you export playlists from iTunes, they contain Windows absolute paths like:
```
C:\Users\Tom\Music\iTunes\iTunes Media\Music\Artist\Album\Song.mp3
```

But your Docker container running Navidrome uses Linux paths:
```
/music/Artist/Album/Song.mp3
```

If you upload raw iTunes playlist files to Navidrome, you'll see the playlist names but **0 tracks** because Navidrome cannot find Windows paths (e.g., `C:\`) on a Linux filesystem.

This script fixes that by converting the paths automatically.

## What It Does

### Two-Tool Workflow:

**Tool 1: `extract_playlists_from_xml.py`** (Optional - if no iTunes access)
- Extracts playlists directly from `iTunes Library.xml`
- Generates individual `.m3u` files for each playlist
- Preserves track metadata and ordering
- Great for batch extraction or when iTunes isn't available

**Tool 2: `playlist_fixer.py`** (Main converter)
- **Interactive terminal-based workflow** - no manual configuration needed
- Auto-detects Windows path prefixes from your playlists
- Converts Windows backslashes (`\`) to Linux forward slashes (`/`)
- Replaces Windows path prefixes with Linux/Docker paths or relative paths
- Handles encoding issues gracefully (UTF-8 with latin-1 fallback)
- Preserves playlist metadata and comments
- Outputs converted files to a separate folder (doesn't overwrite originals)
- Optional network share copying (NAS, Samba, NFS)
- Real-time progress reporting with track counts
- Comprehensive error handling and validation

## Prerequisites

- Python 3.x installed on your system (no external dependencies needed)
- iTunes library with playlists you want to migrate
- Navidrome music server (typically running in Docker)

## Understanding iTunes Playlist Storage

**Important:** iTunes stores playlists internally in database files (`iTunes Library.xml` and `iTunes Library.itl`), **not** as individual `.m3u` files. You won't find `.m3u` files in your iTunes folder.

Navidrome and other music servers need individual `.m3u` playlist files. Therefore, you must **extract** playlists from iTunes first.

**Your iTunes folder contains:**
```
iTunes/
├── iTunes Library.xml        ← Playlists stored here (readable)
├── iTunes Library.itl        ← Binary database (not readable)
├── iTunes Music/             ← Your music files
└── Album Artwork/
```

## Quick Start

You have two options to extract playlists from iTunes:

---

### Option A: Manual Export (If iTunes is Installed)

**Best for:** Few playlists, iTunes is available

1. Open iTunes
2. For each playlist:
   - Click the playlist in the sidebar
   - Go to **File → Library → Export Playlist**
   - Choose a destination folder (e.g., `Desktop\iTunes_Playlists`)
   - Ensure format is `.m3u` (not `.m3u8` or `.txt`)
   - Click Save
3. Repeat for all playlists you want to migrate

**Then proceed to "Convert Playlists for Navidrome" below.**

---

### Option B: Automatic Extraction from XML (Recommended for Batch)

**Best for:** Many playlists, no iTunes access, or automated workflow

This extracts all playlists at once from your `iTunes Library.xml` file.

#### Step 1: Run the Playlist Extractor

```bash
python extract_playlists_from_xml.py
```

The script will prompt you:

```
============================================================
iTunes Library.xml Playlist Extractor
============================================================

This tool extracts playlists from iTunes Library.xml
and creates individual .m3u files.

------------------------------------------------------------
Step 1: Locate iTunes Library.xml
------------------------------------------------------------
Enter the path to your iTunes Library.xml file.
(Usually in: Music/iTunes/iTunes Library.xml)
You can drag and drop the file here

iTunes Library.xml path: N:\Music\iTunes\iTunes Library.xml

Parsing iTunes Library.xml...
Path: N:\Music\iTunes\iTunes Library.xml

Extracting track information...
✅ Found 5847 tracks
Extracting playlists...
✅ Found 23 user playlist(s)

Playlists found:
  1. Rock Classics (156 tracks)
  2. Jazz Favorites (89 tracks)
  3. Workout Mix (47 tracks)
  ...

------------------------------------------------------------
Step 2: Choose Output Folder
------------------------------------------------------------
Where should the .m3u files be saved?
(Leave blank to create 'extracted_playlists' folder in same location as XML)

Output folder path: [press Enter]

✅ Created output folder: N:\Music\iTunes\extracted_playlists

============================================================
EXTRACTING PLAYLISTS
============================================================

[1/23] (4%) Rock Classics ... ✅ 156 tracks
[2/23] (9%) Jazz Favorites ... ✅ 89 tracks
[3/23] (13%) Workout Mix ... ✅ 47 tracks
...

============================================================
EXTRACTION COMPLETE
============================================================
✅ Success: 23 playlist(s)
❌ Errors: 0 playlist(s)

📁 Output location: N:\Music\iTunes\extracted_playlists

============================================================
NEXT STEPS
============================================================

Your playlists have been extracted with iTunes file paths.
To convert them for Navidrome, run:

  python playlist_fixer.py

And point it to: N:\Music\iTunes\extracted_playlists

🎉 All done!
```

---

### Convert Playlists for Navidrome

Simply run the script and follow the prompts:

```bash
python playlist_fixer.py
```

The script will guide you through 6 interactive steps:

#### Step 1: Input Folder
You'll be prompted to enter the folder containing your iTunes playlists. You can drag and drop the folder into the terminal.

```
============================================================
Step 1: Input Folder
------------------------------------------------------------
Enter the path to your folder containing iTunes .m3u files.
(You can drag and drop the folder here)

Input folder path: C:\Users\Tom\Desktop\iTunes_Playlists

✅ Found 15 playlist file(s)
```

#### Step 2: Auto-Detect Windows Prefix
The script will read your first playlist file and automatically detect the Windows path prefix.

```
============================================================
Step 2: Auto-Detect Windows Path Prefix
------------------------------------------------------------

Sample path found:
  C:\Users\Tom\Music\iTunes\iTunes Media\Music\The Beatles\Abbey Road\01 Come Together.mp3

Auto-detected prefix:
  C:/Users/Tom/Music/iTunes/iTunes Media/Music/

This prefix will be REMOVED from all paths.

Use this prefix? (y/n): y
```

If the auto-detection isn't correct, you can enter the prefix manually.

#### Step 3: Choose Linux Path Prefix
Select what should replace the Windows prefix:

```
============================================================
Step 3: Choose Linux Path Prefix
------------------------------------------------------------

What should replace the Windows prefix?

1. Relative paths: ../
   (Recommended - portable, works if you move folders)

2. Absolute Docker paths: /music/
   (For Docker containers with /music mount)

3. Custom prefix
   (Enter your own)

Choice (1/2/3): 1
```

#### Step 4: Preview Conversion
The script shows you sample conversions for confirmation:

```
============================================================
PREVIEW: Sample Path Conversions
============================================================

Before: C:\Users\Tom\Music\iTunes\iTunes Media\Music\The Beatles\Abbey Road\01 Come Together.mp3
After:  ../The Beatles/Abbey Road/01 Come Together.mp3

Before: C:\Users\Tom\Music\iTunes\iTunes Media\Music\Pink Floyd\Dark Side of the Moon\01 Speak to Me.mp3
After:  ../Pink Floyd/Dark Side of the Moon/01 Speak to Me.mp3

------------------------------------------------------------

Proceed with conversion? (y/n): y
```

#### Step 5: Execute Conversion
The script converts all playlists with real-time progress:

```
============================================================
CONVERTING PLAYLISTS
============================================================

[1/15] (7%) My Favorite Songs.m3u ... ✅ 47 tracks
[2/15] (13%) Rock Classics.m3u ... ✅ 156 tracks
[3/15] (20%) Jazz Collection.m3u ... ✅ 89 tracks
...

============================================================
CONVERSION COMPLETE
============================================================
✅ Success: 15 playlist(s)
❌ Errors: 0 playlist(s)

📁 Output location: C:\Users\Tom\Desktop\iTunes_Playlists\converted_for_linux
```

#### Step 6: Optional Network Share Copy
Optionally copy the converted files to a network share:

```
============================================================
OPTIONAL: Copy to Network Share
============================================================

Would you like to copy the converted playlists to a network share?
(e.g., NAS, Samba share, NFS mount)

Copy to network share? (y/n): y

Enter the network share path:
  Windows UNC: \\server\share\playlists
  Linux mount: /mnt/nas/playlists

Network path: \\nas\music\playlists

✅ Network share validated: \\nas\music\playlists

⚠️  About to copy 15 file(s) to:
   \\nas\music\playlists

Existing files with the same name will be overwritten!

Proceed with copy? (y/n): y

============================================================
COPYING TO NETWORK SHARE
============================================================

[1/15] Copying My Favorite Songs.m3u ... ✅
[2/15] Copying Rock Classics.m3u ... ✅
...

✅ Copied: 15 file(s)
❌ Errors: 0 file(s)

🎉 All done!
```

### Step 3: Upload to Navidrome

1. Find the converted playlists in the `converted_for_linux` subfolder (or network share if you used that option)
2. Upload them to your Navidrome playlists directory
3. Restart Navidrome or refresh playlists in the UI

## Example Conversion

**Before (iTunes export):**
```
C:\Users\Tom\Music\iTunes\iTunes Media\Music\The Beatles\Abbey Road\01 Come Together.mp3
```

**After (script conversion with relative paths):**
```
../The Beatles/Abbey Road/01 Come Together.mp3
```

**After (script conversion with absolute Docker paths):**
```
/music/The Beatles/Abbey Road/01 Come Together.mp3
```

## Features

### ✅ Playlist Extraction Tool (`extract_playlists_from_xml.py`)
- **Parse iTunes Library.xml** - Extract playlists without iTunes installed
- **Batch extraction** - All playlists extracted at once
- **plist XML parser** - Native Python, no external dependencies
- **Track metadata preservation** - Preserves artist, title, duration
- **Smart playlist filtering** - Excludes built-in iTunes playlists
- **Filename sanitization** - Handles special characters in playlist names
- **Progress reporting** - Real-time extraction progress
- **Error handling** - Graceful handling of corrupted playlists

### ✅ Path Conversion Tool (`playlist_fixer.py`)
- **Fully interactive workflow** - no manual configuration needed
- **Auto-detection** of Windows path prefixes
- **Path conversion** from Windows to Linux format
- **Batch processing** of multiple playlists with progress indicators
- **Encoding handling** - UTF-8 with latin-1 fallback for special characters
- **Case-insensitive path matching** for Windows compatibility
- **Proper line ending handling** to prevent corruption
- **Network share support** - copy to NAS/Samba/NFS shares
- **Comprehensive error handling** with detailed error reporting
- **Preview mode** - see sample conversions before processing
- **Safe operation** - outputs to separate folder, never overwrites originals
- **Drag-and-drop support** for folder paths
- **Real-time progress reporting** with track counts
- **Validation** of all user inputs with retry options

### Critical Bug Fixes (v2.0)
- **Line ending corruption fix** - Properly handles Windows `\r\n` line endings
- **Case-sensitive path fix** - Uses case-insensitive regex matching for Windows paths
- **Encoding error fix** - UTF-8 with latin-1 fallback instead of silently dropping characters
- **Comprehensive error handling** - Try-except blocks around all file operations

## Troubleshooting

### "0 tracks" still showing in Navidrome

- Verify your music files are in the correct location on the server
- Check that the file paths in the converted playlists match your actual file structure
- Ensure file permissions allow Navidrome to read the music files
- If using relative paths (`../`), make sure the playlist files are in the correct location relative to your music files

### Encoding errors or special characters not displaying correctly

- The script now tries UTF-8 first, then falls back to latin-1 encoding
- If you see a warning about encoding issues, the script will still process the file
- Check your original iTunes export if song titles with special characters (é, ñ, etc.) are missing

### Path not found or permission denied

- Make sure the folder you specify exists and you have read permissions
- For network shares, ensure the share is mounted and accessible
- You can drag and drop folders into the terminal to avoid typing errors
- The script will validate paths and let you retry if there are issues

### Script shows "No .m3u files found"

- Verify you exported playlists from iTunes as `.m3u` format (not `.m3u8` or other formats)
- The script supports both `.m3u` and `.m3u8` files
- Check that you're pointing to the correct folder containing the playlist files

### Auto-detection suggests wrong prefix

- If the auto-detected Windows prefix is incorrect, choose 'n' when prompted
- You'll be able to enter the prefix manually
- Open one of your `.m3u` files in Notepad to see the exact path structure
- The prefix should be everything up to (and including) the folder before artist names

### Network copy fails

- Ensure the network share is accessible from your computer
- Check that you have write permissions on the network share
- For Windows UNC paths, use format: `\\server\share\folder`
- For Linux mount points, use format: `/mnt/nas/folder`
- The script validates write permissions before copying

### Cancelling the script

- You can press `Ctrl+C` at any time to cancel the script
- All validation prompts offer retry options if you make a mistake
- Original files are never modified - only new files are created

### XML Extraction Issues

**"No user playlists found"**
- The XML parser excludes built-in iTunes playlists (Music, Movies, TV Shows, etc.)
- Check that you actually have user-created playlists in iTunes
- Open `iTunes Library.xml` in a text editor and search for `<key>Playlists</key>` to verify

**"Error parsing XML file"**
- Ensure the file is actually `iTunes Library.xml` (not `.itl` which is binary)
- The XML file may be corrupted - try exporting a fresh library from iTunes
- Very large libraries (100k+ tracks) may take longer to parse - be patient

**"Could not find iTunes Library.xml"**
- Default location is: `Music/iTunes/iTunes Library.xml` (Mac) or `My Music\iTunes\iTunes Library.xml` (Windows)
- If iTunes is installed, go to iTunes Preferences → Advanced to see library location
- You can drag and drop the XML file into the terminal for the correct path

**Extracted playlists have wrong paths**
- This is normal! The XML extraction preserves original iTunes paths
- You still need to run `playlist_fixer.py` on the extracted playlists
- The two-step process is: (1) Extract from XML → (2) Convert paths

**Missing tracks in extracted playlists**
- Check that the tracks exist in your iTunes library
- Dead/missing tracks in iTunes won't have valid file paths
- The extractor skips tracks without a valid `Location` field

## Technical Details

### Dependencies
- Uses only Python standard library (os, re, shutil, sys, xml.etree.ElementTree)
- No external packages required
- Works with Python 3.x on Windows, macOS, and Linux

### How XML Extraction Works (`extract_playlists_from_xml.py`)
1. Parses iTunes Library.xml using native Python XML parser
2. Extracts track database (ID → file path mapping)
3. Extracts playlist data (name → list of track IDs)
4. Filters out built-in iTunes playlists (Master, Distinguished Kind)
5. Resolves track IDs to file paths
6. Generates .m3u files with EXTM3U format and metadata
7. Sanitizes playlist names for filesystem compatibility

### How Path Conversion Works (`playlist_fixer.py`)
1. Reads playlist files line by line
2. Preserves comment lines (starting with `#`)
3. Strips line endings before processing to prevent corruption
4. Converts backslashes to forward slashes
5. Uses case-insensitive regex to replace Windows prefix with Linux prefix
6. Re-adds normalized line endings (`\n`)
7. Writes output files with UTF-8 encoding

### Output Structure
```
iTunes/
├── iTunes Library.xml
└── extracted_playlists/         ← Step 1: XML extraction
    ├── Rock Classics.m3u
    ├── Jazz Favorites.m3u
    └── converted_for_linux/     ← Step 2: Path conversion
        ├── Rock Classics.m3u    (Navidrome-ready)
        └── Jazz Favorites.m3u   (Navidrome-ready)
```

## Contributing

Contributions welcome! This tool is now feature-complete for its intended use case, but potential improvements include:

- GUI interface (currently terminal-only by design)
- Command-line arguments for automation
- Config file support for repeated conversions
- Playlist format conversion (M3U to other formats)
- Cloud storage upload support

## License

Open source - use and modify as needed for your iTunes to Navidrome migration.
