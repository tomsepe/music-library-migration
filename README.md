# iTunes to Navidrome Playlist Converter

A Python utility to migrate iTunes playlists for use with Navidrome music server running in Docker.

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

- Reads iTunes-exported `.m3u` and `.m3u8` playlist files
- Converts Windows backslashes (`\`) to Linux forward slashes (`/`)
- Replaces Windows path prefixes with Linux/Docker paths or relative paths
- Preserves playlist metadata and comments
- Outputs converted files to a separate folder (doesn't overwrite originals)

## Prerequisites

- Python 3.x installed on your system
- iTunes playlists exported as `.m3u` files
- Navidrome music server (typically running in Docker)

## Quick Start

### Step 1: Export Your iTunes Playlists

1. Open iTunes
2. Go to **File → Library → Export Playlist**
3. Save as `.m3u` format to a folder (e.g., `iTunes_Playlists` on your Desktop)
4. Repeat for each playlist you want to migrate

### Step 2: Configure the Script

Open `playlist_fixer.py` and edit these three configuration variables:

```python
# 1. Where are your iTunes .m3u files?
INPUT_FOLDER = "path to input folder or individual music file"

# 2. What part of the path needs to be removed?
#    (Open an .m3u in Notepad to see how iTunes wrote the paths)
WINDOWS_PREFIX = "C:/Users/Tom/Music/iTunes/iTunes Media/Music/"

# 3. What should replace it?
LINUX_PREFIX = "../"  # Relative path (recommended)
# OR
LINUX_PREFIX = "/music/"  # Absolute Docker path
```

**How to find your WINDOWS_PREFIX:**
1. Open one of your exported `.m3u` files in Notepad
2. Look at the file paths - they'll look like: `C:\Users\YourName\Music\...`
3. Copy everything up to (and including) the last folder before artist names
4. Replace backslashes with forward slashes

**Choosing LINUX_PREFIX:**
- Use `"../"` for relative paths (recommended - more portable)
- Use `"/music/"` if your Docker volume is mounted at `/music/` and you want absolute paths

### Step 3: Run the Script

```bash
python playlist_fixer.py
```

The script will:
- Create a `converted_for_linux` subfolder in your input directory
- Convert all `.m3u` and `.m3u8` files
- Show progress for each playlist

### Step 4: Upload to Navidrome

1. Copy the converted playlist files from the `converted_for_linux` folder
2. Upload them to your Navidrome playlists directory
3. Restart Navidrome or refresh playlists in the UI

## Example

**Before (iTunes export):**
```
C:\Users\Tom\Music\iTunes\iTunes Media\Music\The Beatles\Abbey Road\01 Come Together.mp3
```

**After (script conversion with relative paths):**
```
../The Beatles/Abbey Road/01 Come Together.mp3
```

## Project Status

### ✅ Working Features
- Path conversion from Windows to Linux format
- Batch processing of multiple playlists
- Preserves playlist metadata
- Safe output to separate folder

### 🚧 Planned Features (Currently Unfinished)
- Interactive user input for folder paths (currently requires manual editing)
- Automatic file copying to network shares (Samba/NFS)
- Verification that music files exist before conversion

See lines 16, 72-75 in `playlist_fixer.py` for TODO items.

## Troubleshooting

**"0 tracks" still showing in Navidrome:**
- Verify your music files are in the correct location on the server
- Check that the file paths in the converted playlists match your actual file structure
- Ensure file permissions allow Navidrome to read the music files

**Encoding errors:**
- The script uses UTF-8 encoding with error handling for special characters
- If you see issues with song titles, check your original iTunes export encoding

**Path not found:**
- Make sure your `INPUT_FOLDER` uses forward slashes (`/`) even on Windows
- Use absolute paths, e.g., `C:/Users/Tom/Desktop/iTunes_Playlists`

## Contributing

This is a work-in-progress utility. Feel free to:
- Add the missing user input functionality
- Implement network file copying
- Add file existence validation
- Improve error handling

## License

Open source - use and modify as needed for your iTunes to Navidrome migration.
