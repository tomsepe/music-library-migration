# Here is the Python script to help automate the migration of your iTunes playlists for playback in Navidrome.

# Why you need this
# iTunes exports playlists using Windows absolute paths (e.g., C:\Users\Tom\Music\...). Your Docker container (Navidrome) looks for files using Linux paths (e.g., /music/...).

# If you upload the raw iTunes files, Navidrome will see the playlist name but show 0 tracks because it cannot find C:\ on a Linux server. This script fixes the slashes and swaps the file paths for you.

import os
import sys
import shutil
from pathlib import Path

# --- Enhanced Interactive Configuration ---
def get_user_input():
    """Get all required configuration from user with validation."""

    # 1. Get input folder
    while True:
        input_folder = input("Enter the path to your iTunes playlists folder: ").strip()
        if not input_folder:
            print("❌ Path cannot be empty. Please try again.")
            continue
        if not os.path.exists(input_folder):
            print(f"❌ Path does not exist: {input_folder}")
            continue
        if not os.path.isdir(input_folder):
            print(f"❌ Path is not a directory: {input_folder}")
            continue
        break

    # 2. Get Windows prefix
    while True:
        windows_prefix = input("Enter the Windows path prefix from iTunes (e.g., C:/Users/Username/Music/iTunes/iTunes Media/Music/): ").strip()
        if not windows_prefix:
            print("❌ Windows prefix cannot be empty. Please try again.")
            continue
        # Normalize the path for comparison
        if windows_prefix.endswith('/'):
            windows_prefix = windows_prefix.rstrip('/')
        break

    # 3. Get Linux prefix
    while True:
        print("\nChoose Linux path prefix:")
        print("1. Relative path (e.g., ../) - Recommended for flexibility")
        print("2. Absolute path (e.g., /music/) - For specific Docker setup")
        choice = input("Enter your choice (1 or 2, default is 1): ").strip()

        if choice == "2":
            linux_prefix = input("Enter the absolute Linux path prefix (e.g., /music/): ").strip()
        else:
            linux_prefix = "../"
            print("Using relative path: ../")

        if not linux_prefix:
            print("❌ Linux prefix cannot be empty. Please try again.")
            continue
        break

    return input_folder, windows_prefix, linux_prefix

def validate_paths(input_folder, windows_prefix, linux_prefix):
    """Validate that paths are valid and make sense."""
    print("\n🔍 Validating paths...")

    # Check that input folder exists
    if not os.path.exists(input_folder):
        raise ValueError(f"Input folder does not exist: {input_folder}")

    # Count potential playlist files
    playlist_count = 0
    for filename in os.listdir(input_folder):
        if filename.endswith((".m3u", ".m3u8")):
            playlist_count += 1

    if playlist_count == 0:
        print("⚠️ Warning: No .m3u or .m3u8 files found in the input folder.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm not in ('y', 'yes'):
            print("Operation cancelled by user.")
            sys.exit(0)

    print(f"✅ Found {playlist_count} playlist files in {input_folder}")
    print(f"✅ Windows prefix: {windows_prefix}")
    print(f"✅ Linux prefix: {linux_prefix}")

def confirm_operation(input_folder, windows_prefix, linux_prefix):
    """Ask user for confirmation before proceeding."""
    print("\n📋 Summary of operation:")
    print(f"   Input folder: {input_folder}")
    print(f"   Windows prefix: {windows_prefix}")
    print(f"   Linux prefix: {linux_prefix}")

    confirm = input("\nProceed with conversion? (y/n): ").strip().lower()
    if confirm not in ('y', 'yes'):
        print("Operation cancelled by user.")
        sys.exit(0)

    print("\n🔄 Starting conversion...")

def create_output_folder(input_folder):
    """Create output folder with proper naming."""
    output_folder = os.path.join(input_folder, "converted_for_linux")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Created output folder: {output_folder}")
    return output_folder

def process_playlist_files(input_folder, output_folder, windows_prefix, linux_prefix):
    """Process all playlist files with progress reporting."""
    playlist_files = []
    for filename in os.listdir(input_folder):
        if filename.endswith((".m3u", ".m3u8")):
            playlist_files.append(filename)

    if not playlist_files:
        print("⚠️  No playlist files to process.")
        return 0

    print(f"\n📊 Processing {len(playlist_files)} playlist files...")

    processed_count = 0
    for i, filename in enumerate(playlist_files, 1):
        try:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Process the file with error handling
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f_in:
                lines = f_in.readlines()

            new_lines = []
            for line in lines:
                # Skip comments (lines starting with #)
                if line.startswith("#"):
                    new_lines.append(line)
                    continue

                # 1. Replace Windows backslashes (\) with Linux forward slashes (/)
                cleaned_line = line.replace("\\", "/")

                # 2. Replace the Windows path with the Linux path
                if windows_prefix in cleaned_line:
                    cleaned_line = cleaned_line.replace(windows_prefix, linux_prefix)

                new_lines.append(cleaned_line)

            # Write the new file
            with open(output_path, 'w', encoding='utf-8') as f_out:
                f_out.writelines(new_lines)

            # Progress reporting
            progress = f"[{i}/{len(playlist_files)}]"
            print(f"✅ {progress} Fixed: {filename}")
            processed_count += 1

        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            continue

    return processed_count

def main():
    """Main function with enhanced interactivity."""
    print("=" * 60)
    print("🎵 iTunes to Navidrome Playlist Converter")
    print("=" * 60)
    print("This tool helps convert iTunes playlist files for Navidrome.")
    print("Navidrome requires Linux-style paths, while iTunes uses Windows paths.")
    print("=" * 60)

    try:
        # Get configuration from user
        input_folder, windows_prefix, linux_prefix = get_user_input()

        # Validate paths
        validate_paths(input_folder, windows_prefix, linux_prefix)

        # Confirm operation
        confirm_operation(input_folder, windows_prefix, linux_prefix)

        # Create output folder
        output_folder = create_output_folder(input_folder)

        # Process playlist files
        count = process_playlist_files(input_folder, output_folder, windows_prefix, linux_prefix)

        # Final report
        print("\n🎉 Conversion complete!")
        print(f"✅ Successfully converted {count} playlist files.")
        print(f"📁 Converted files are in: {output_folder}")
        print("\n💡 Next steps:")
        print("   1. Review the converted playlists in the output folder")
        print("   2. Import these playlists into Navidrome")
        print("   3. If you want to also copy music files, you'll need to do that separately")

    except KeyboardInterrupt:
        print("\n\n⚠️ Operation interrupted by user.")
        print("Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your input and try again.")
        sys.exit(1)

# --- Additional Functions (commented out for now, can be implemented later) ---
# Additional function to create:
# ask user for path to samba share or nfs share to copy the files to
# move the files
# party time!

if __name__ == "__main__":
    main()
