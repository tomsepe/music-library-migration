# iTunes to Navidrome Migration Tool

This project provides tools to help migrate your iTunes music library to Navidrome. Navidrome is a self-hosted music server that requires Linux-style paths for file locations, while iTunes exports playlists using Windows-style paths.

## Project Goal

The goal is to take an iTunes music library and use it as a guide to import music files into Navidrome. This involves converting iTunes playlist files (.m3u) to be compatible with Navidrome's Linux-based path structure.

## How It Works

1. iTunes exports playlists using Windows absolute paths (e.g., `C:\Users\Tom\Music\...`)
2. Navidrome expects Linux-style paths (e.g., `/music/...`)
3. This tool converts the paths and fixes the playlist files for Navidrome

## Current Tool: `playlist_fixer.py`

This script automates the conversion of iTunes playlist files:

### Features:
- Converts Windows backslashes to Linux forward slashes
- Replaces Windows paths with Linux paths
- Preserves comments in playlist files
- Creates a separate output folder to avoid overwriting originals
- Interactive user prompts for configuration
- Input validation and error handling
- Progress reporting during processing
- Confirmation before operation
- Comprehensive error messages

### Usage:
1. Export your iTunes playlists: In iTunes, go to File > Library > Export Playlist and save them as .m3u files to a folder on your Desktop
2. Run the script: `python playlist_fixer.py`
3. Follow the interactive prompts to enter:
   - Path to your iTunes playlists folder
   - Windows path prefix from iTunes
   - Linux path prefix for Navidrome

### Example Configuration:
```python
INPUT_FOLDER = "C:/Users/Username/Desktop/iTunes_Playlists"
WINDOWS_PREFIX = "C:/Users/Username/Music/iTunes/iTunes Media/Music/"
LINUX_PREFIX = "../"
```

## Enhanced Features:
- Interactive user prompts instead of manual code editing
- Input validation for all paths
- Progress reporting during processing
- Confirmation before operation
- Error handling and graceful exits
- Clear progress indicators
- Comprehensive error messages

## Next Steps

This is an unfinished tool that can be extended to:
1. Automate the entire import process from iTunes to Navidrome
2. Handle music file copying/moving
3. Create a complete migration workflow
4. Support different path structures based on user setup

## Contributing

This project is a work in progress. Contributions to improve the iTunes to Navidrome migration workflow are welcome. Please submit issues or pull requests to help enhance this tool.