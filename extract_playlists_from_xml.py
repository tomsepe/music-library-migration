import os
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import re

# ============================================================
# iTunes Library.xml Playlist Extractor
# ============================================================
# Extracts playlists from iTunes Library.xml and generates .m3u files
# Use this if you don't have iTunes installed or have many playlists
# ============================================================


def parse_plist_dict(element):
    """Parse a plist <dict> element into a Python dictionary."""
    result = {}
    children = list(element)

    i = 0
    while i < len(children):
        if children[i].tag == 'key':
            key = children[i].text
            i += 1
            if i < len(children):
                value = parse_plist_value(children[i])
                result[key] = value
        i += 1

    return result


def parse_plist_array(element):
    """Parse a plist <array> element into a Python list."""
    return [parse_plist_value(child) for child in element]


def parse_plist_value(element):
    """Parse a plist value element and return the appropriate Python type."""
    if element.tag == 'dict':
        return parse_plist_dict(element)
    elif element.tag == 'array':
        return parse_plist_array(element)
    elif element.tag == 'string':
        return element.text if element.text else ''
    elif element.tag == 'integer':
        return int(element.text) if element.text else 0
    elif element.tag == 'true':
        return True
    elif element.tag == 'false':
        return False
    elif element.tag == 'date':
        return element.text if element.text else ''
    elif element.tag == 'data':
        return element.text if element.text else ''
    else:
        return None


def decode_file_url(url):
    """Convert file:// URL to regular file path."""
    if not url:
        return None

    # Remove file:// prefix
    if url.startswith('file://'):
        url = url[7:]

    # URL decode
    path = unquote(url)

    # Handle localhost prefix
    if path.startswith('localhost/'):
        path = path[10:]

    # Convert forward slashes to backslashes on Windows if needed
    # For now, keep forward slashes as the converter script handles this

    return path


def extract_tracks(library_dict):
    """Extract track information from iTunes library."""
    tracks = {}

    if 'Tracks' not in library_dict:
        return tracks

    tracks_dict = library_dict['Tracks']

    for track_id, track_info in tracks_dict.items():
        if 'Location' in track_info:
            location = decode_file_url(track_info['Location'])
            if location:
                tracks[track_id] = {
                    'location': location,
                    'name': track_info.get('Name', ''),
                    'artist': track_info.get('Artist', ''),
                    'album': track_info.get('Album', ''),
                    'total_time': track_info.get('Total Time', 0)
                }

    return tracks


def extract_playlists(library_dict, tracks):
    """Extract playlist information from iTunes library."""
    playlists = []

    if 'Playlists' not in library_dict:
        return playlists

    playlists_array = library_dict['Playlists']

    for playlist_info in playlists_array:
        # Skip special iTunes playlists
        if playlist_info.get('Master'):
            continue
        if playlist_info.get('Distinguished Kind'):
            continue

        # Get playlist name
        name = playlist_info.get('Name', 'Untitled Playlist')

        # Skip if no playlist items
        if 'Playlist Items' not in playlist_info:
            continue

        # Extract track locations
        track_locations = []
        for item in playlist_info['Playlist Items']:
            track_id = str(item.get('Track ID', ''))
            if track_id in tracks:
                track_data = tracks[track_id]
                track_locations.append({
                    'location': track_data['location'],
                    'name': track_data['name'],
                    'artist': track_data['artist'],
                    'total_time': track_data['total_time']
                })

        if track_locations:
            playlists.append({
                'name': name,
                'tracks': track_locations
            })

    return playlists


def sanitize_filename(filename):
    """Sanitize playlist name for use as filename."""
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing spaces and periods
    filename = filename.strip('. ')

    # Ensure it's not empty
    if not filename:
        filename = 'Untitled'

    return filename


def write_m3u_playlist(playlist, output_folder):
    """Write a playlist to an .m3u file."""
    # Sanitize filename
    safe_name = sanitize_filename(playlist['name'])
    output_path = os.path.join(output_folder, f"{safe_name}.m3u")

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write M3U header
            f.write('#EXTM3U\n')

            # Write each track
            for track in playlist['tracks']:
                # Write extended info line
                # Format: #EXTINF:duration_in_seconds,Artist - Track Name
                duration_seconds = track['total_time'] // 1000 if track['total_time'] else -1
                artist = track['artist'] if track['artist'] else 'Unknown Artist'
                name = track['name'] if track['name'] else 'Unknown Track'

                f.write(f"#EXTINF:{duration_seconds},{artist} - {name}\n")

                # Write file path
                f.write(f"{track['location']}\n")

        return True, len(playlist['tracks'])

    except Exception as e:
        return False, str(e)


def parse_itunes_library(xml_path):
    """Parse iTunes Library.xml file."""
    print(f"\nParsing iTunes Library.xml...")
    print(f"Path: {xml_path}\n")

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # iTunes library XML is a plist format
        # Structure: <plist><dict>...</dict></plist>
        plist_dict = None
        for child in root:
            if child.tag == 'dict':
                plist_dict = parse_plist_dict(child)
                break

        if not plist_dict:
            print("❌ Error: Could not find library dictionary in XML")
            return None

        return plist_dict

    except ET.ParseError as e:
        print(f"❌ Error parsing XML file: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None


def main():
    """Main function for interactive workflow."""
    try:
        print("\n" + "=" * 60)
        print("iTunes Library.xml Playlist Extractor")
        print("=" * 60)
        print("\nThis tool extracts playlists from iTunes Library.xml")
        print("and creates individual .m3u files.\n")

        # Step 1: Get iTunes Library.xml path
        print("-" * 60)
        print("Step 1: Locate iTunes Library.xml")
        print("-" * 60)
        print("Enter the path to your iTunes Library.xml file.")
        print("(Usually in: Music/iTunes/iTunes Library.xml)")
        print("You can drag and drop the file here")

        xml_path = input("\niTunes Library.xml path: ").strip()

        # Remove quotes
        xml_path = xml_path.strip('"').strip("'")

        # Normalize path
        xml_path = os.path.normpath(xml_path)

        # Validate file exists
        if not os.path.exists(xml_path):
            print(f"\n❌ Error: File not found: {xml_path}")
            return

        if not os.path.isfile(xml_path):
            print(f"\n❌ Error: Path is not a file: {xml_path}")
            return

        # Step 2: Parse the XML
        library_dict = parse_itunes_library(xml_path)
        if not library_dict:
            return

        # Step 3: Extract tracks
        print("Extracting track information...")
        tracks = extract_tracks(library_dict)
        print(f"✅ Found {len(tracks)} tracks")

        # Step 4: Extract playlists
        print("Extracting playlists...")
        playlists = extract_playlists(library_dict, tracks)

        if not playlists:
            print("\n❌ No user playlists found in iTunes library")
            print("(Built-in iTunes playlists are excluded)")
            return

        print(f"✅ Found {len(playlists)} user playlist(s)")

        # Show playlist names
        print("\nPlaylists found:")
        for i, playlist in enumerate(playlists, 1):
            track_count = len(playlist['tracks'])
            print(f"  {i}. {playlist['name']} ({track_count} tracks)")

        # Step 5: Choose output folder
        print("\n" + "-" * 60)
        print("Step 2: Choose Output Folder")
        print("-" * 60)
        print("Where should the .m3u files be saved?")
        print("(Leave blank to create 'extracted_playlists' folder in same location as XML)")

        output_folder = input("\nOutput folder path: ").strip()

        if not output_folder:
            # Default to same directory as XML
            xml_dir = os.path.dirname(xml_path)
            output_folder = os.path.join(xml_dir, "extracted_playlists")
        else:
            # Remove quotes
            output_folder = output_folder.strip('"').strip("'")
            output_folder = os.path.normpath(output_folder)

        # Create output folder
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                print(f"\n✅ Created output folder: {output_folder}")
            else:
                print(f"\n✅ Using output folder: {output_folder}")
        except Exception as e:
            print(f"\n❌ Error creating output folder: {e}")
            return

        # Step 6: Export playlists
        print("\n" + "=" * 60)
        print("EXTRACTING PLAYLISTS")
        print("=" * 60 + "\n")

        success_count = 0
        error_count = 0
        errors = []

        for i, playlist in enumerate(playlists, 1):
            playlist_name = playlist['name']
            percentage = int((i / len(playlists)) * 100)

            success, result = write_m3u_playlist(playlist, output_folder)

            if success:
                track_count = result
                print(f"[{i}/{len(playlists)}] ({percentage}%) {playlist_name} ... ✅ {track_count} tracks")
                success_count += 1
            else:
                error_msg = result
                print(f"[{i}/{len(playlists)}] ({percentage}%) {playlist_name} ... ❌ ERROR: {error_msg}")
                error_count += 1
                errors.append((playlist_name, error_msg))

        # Summary
        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"✅ Success: {success_count} playlist(s)")
        print(f"❌ Errors: {error_count} playlist(s)")

        if errors:
            print("\nError details:")
            for playlist_name, error_msg in errors:
                print(f"  - {playlist_name}: {error_msg}")

        print(f"\n📁 Output location: {output_folder}")

        # Next steps
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("\nYour playlists have been extracted with iTunes file paths.")
        print("To convert them for Navidrome, run:")
        print("\n  python playlist_fixer.py")
        print(f"\nAnd point it to: {output_folder}")
        print("\n🎉 All done!\n")

    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
