import os
import subprocess
import sys

# ============================================================
# Interactive Music Library Copier for Navidrome
# ============================================================
# Uses rsync to copy artist folders from iTunes library
# to Navidrome music folder structure
# ============================================================


# ============================================================
# UI/DISPLAY FUNCTIONS
# ============================================================

def print_welcome():
    """Display welcome message and instructions."""
    print("\n" + "=" * 60)
    print("Music Library Copier for Navidrome")
    print("=" * 60)
    print("\nThis tool copies your music library from iTunes to Navidrome")
    print("using rsync for efficient, incremental copying.\n")


def print_navidrome_structure_info():
    """Display information about Navidrome folder structure requirements."""
    print("\n" + "=" * 60)
    print("Navidrome Folder Structure")
    print("=" * 60)
    print("\nNavidrome expects music files organized in a simple structure:")
    print("\n  /music/Artist/Album/Song.mp3")
    print("\nOr for Docker containers:")
    print("\n  /music/Artist/Album/Song.mp3")
    print("\nKey points:")
    print("  • Each artist should have their own folder")
    print("  • Each album should be a subfolder within the artist folder")
    print("  • Songs should be directly in the album folder")
    print("  • No iTunes-specific folders (e.g., 'iTunes Media', 'ITunes Music')")
    print("\nExample structure:")
    print("  /music/")
    print("    ├── The Beatles/")
    print("    │   ├── Abbey Road/")
    print("    │   │   ├── 01 Come Together.mp3")
    print("    │   │   └── 02 Something.mp3")
    print("    │   └── Sgt. Pepper's/")
    print("    │       └── ...")
    print("    └── Pink Floyd/")
    print("        └── Dark Side of the Moon/")
    print("            └── ...")
    print("\n" + "-" * 60)


def print_summary(copied_count, skipped_count, errors):
    """Display copy summary report."""
    print("\n" + "=" * 60)
    print("COPY COMPLETE")
    print("=" * 60)
    print(f"✅ Processed: {copied_count} artist folder(s)")
    if skipped_count > 0:
        print(f"⏭️  Skipped: {skipped_count} artist folder(s)")
    print(f"❌ Errors: {len(errors)} artist folder(s)")

    if errors:
        print("\nError details:")
        for artist, error_msg in errors:
            print(f"  - {artist}: {error_msg}")
    
    if copied_count > 0:
        print("\nℹ️  Note: rsync only transferred new or changed files.")
        print("   Existing files were preserved and not re-copied.")


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def validate_path_exists(path):
    """Check if path exists."""
    return os.path.exists(path)


def validate_is_directory(path):
    """Check if path is a directory."""
    return os.path.isdir(path)


def validate_writable(path):
    """Check if directory is writable by attempting to create a temp file."""
    test_file = os.path.join(path, ".write_test_temp")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except (OSError, PermissionError):
        return False


def check_rsync_available():
    """Check if rsync is available on the system."""
    try:
        result = subprocess.run(
            ['rsync', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ============================================================
# CONFIGURATION FUNCTIONS
# ============================================================

def get_input_folder():
    """Prompt user for input folder (iTunes music folder) and validate it."""
    while True:
        print("\n" + "-" * 60)
        print("Step 1: Input Folder (iTunes Music Location)")
        print("-" * 60)
        print("Enter the path to your iTunes music folder.")
        print("\nThis should be the folder containing your artist folders.")
        print("Common locations:")
        print("  • Windows: C:\\Users\\YourName\\Music\\iTunes\\iTunes Media\\Music")
        print("  • Windows: C:\\Users\\YourName\\Music\\iTunes\\ITunes Music")
        print("  • macOS: ~/Music/iTunes/iTunes Media/Music")
        print("\n(You can drag and drop the folder here)")

        path = input("\nInput folder path: ").strip()

        # Remove quotes (from drag-and-drop)
        path = path.strip('"').strip("'")

        # Normalize path separators
        path = os.path.normpath(path)

        # Validate path exists
        if not validate_path_exists(path):
            print(f"\n❌ Error: Path does not exist: {path}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        # Validate it's a directory
        if not validate_is_directory(path):
            print(f"\n❌ Error: Path is not a directory: {path}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        # Check if folder contains artist subdirectories
        try:
            items = os.listdir(path)
            # Look for at least one subdirectory (potential artist folder)
            has_subdirs = any(os.path.isdir(os.path.join(path, item)) for item in items)
            if not has_subdirs:
                print(f"\n⚠️  Warning: No subdirectories found in: {path}")
                print("This might not be the correct iTunes music folder.")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
        except (OSError, PermissionError) as e:
            print(f"\n❌ Error reading folder contents: {e}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        print(f"\n✅ Input folder validated: {path}")
        return path


def get_output_folder():
    """Prompt user for output folder (Navidrome music folder) and validate it."""
    while True:
        print("\n" + "-" * 60)
        print("Step 2: Output Folder (Navidrome Music Location)")
        print("-" * 60)
        print("Enter the path where Navidrome expects your music files.")
        print("\nThis is typically:")
        print("  • Docker volume mount: /mnt/music or /music")
        print("  • Local folder: C:\\Music or ~/Music")
        print("  • Network share: \\\\nas\\music or /mnt/nas/music")
        print("\nThe tool will copy artist folders into this location.")
        print("(You can drag and drop the folder here)")

        path = input("\nOutput folder path: ").strip()

        # Remove quotes (from drag-and-drop)
        path = path.strip('"').strip("'")

        # Normalize path separators
        path = os.path.normpath(path)

        # Validate path exists
        if not validate_path_exists(path):
            print(f"\n❌ Error: Path does not exist: {path}")
            create = input("Create this folder? (y/n): ").strip().lower()
            if create == 'y':
                try:
                    os.makedirs(path, exist_ok=True)
                    print(f"✅ Created folder: {path}")
                except Exception as e:
                    print(f"❌ Error creating folder: {e}")
                    retry = input("Try again? (y/n): ").strip().lower()
                    if retry != 'y':
                        return None
                    continue
            else:
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
                continue

        # Validate it's a directory
        if not validate_is_directory(path):
            print(f"\n❌ Error: Path is not a directory: {path}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        # Validate writable
        if not validate_writable(path):
            print(f"\n❌ Error: No write permission for: {path}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        print(f"\n✅ Output folder validated: {path}")
        return path


def preview_copy_operation(input_folder, output_folder):
    """Show preview of what will be copied and ask for confirmation."""
    print("\n" + "=" * 60)
    print("PREVIEW: Copy Operation")
    print("=" * 60)

    try:
        # Get list of artist folders (directories in input folder)
        items = os.listdir(input_folder)
        artist_folders = [item for item in items if os.path.isdir(os.path.join(input_folder, item))]

        if not artist_folders:
            print("\n⚠️  Warning: No artist folders found in input directory")
            print("This might not be the correct iTunes music folder.")
            confirm = input("\nProceed anyway? (y/n): ").strip().lower()
            return confirm == 'y'

        total_artists = len(artist_folders)
        print(f"\nFound {total_artists} artist folder(s) to copy")

        # Show first 10 artist folders as examples
        print("\nSample artist folders:")
        for i, artist in enumerate(artist_folders[:10], 1):
            print(f"  {i}. {artist}")
        if total_artists > 10:
            print(f"  ... and {total_artists - 10} more")

        print(f"\nSource: {input_folder}")
        print(f"Destination: {output_folder}")
        print("\nOperation:")
        print("  • Artist folders will be copied from source to destination")
        print("  • Existing artist folders in destination will be updated (rsync)")
        print("  • Files will be preserved (no deletion of existing files)")
        print("  • Only new/changed files will be transferred")

        print("\n" + "-" * 60)
        confirm = input("\nProceed with copy? (y/n): ").strip().lower()
        return confirm == 'y'

    except Exception as e:
        print(f"\n❌ Error reading input folder: {e}")
        return False


# ============================================================
# COPY FUNCTIONS
# ============================================================

def copy_artist_folders_rsync(input_folder, output_folder):
    """
    Copy artist folders from input to output using rsync.
    Returns (copied_count, skipped_count, errors_list)
    """
    try:
        # Get list of artist folders
        items = os.listdir(input_folder)
        artist_folders = [item for item in items if os.path.isdir(os.path.join(input_folder, item))]

        if not artist_folders:
            print("\n❌ No artist folders found in input directory")
            return (0, 0, [])

        print("\n" + "=" * 60)
        print("COPYING ARTIST FOLDERS")
        print("=" * 60 + "\n")

        copied_count = 0
        skipped_count = 0
        errors = []
        total_artists = len(artist_folders)

        for idx, artist_folder in enumerate(artist_folders, 1):
            source_path = os.path.join(input_folder, artist_folder)
            dest_path = os.path.join(output_folder, artist_folder)

            # Calculate percentage
            percentage = int((idx / total_artists) * 100)

            # Check if destination already exists
            dest_exists = os.path.exists(dest_path)

            try:
                # Build rsync command
                # -a: archive mode (preserves permissions, timestamps, etc.)
                # -v: verbose (one line per file)
                # --partial: keep partial files on interruption
                # --human-readable: human-readable sizes
                # Trailing slash on source means copy contents of folder, not folder itself
                rsync_cmd = [
                    'rsync',
                    '-av',
                    '--partial',
                    '--human-readable',
                    source_path + os.sep,  # Trailing slash means copy contents
                    dest_path
                ]

                # Run rsync (suppress stdout for cleaner output, stderr for errors)
                result = subprocess.run(
                    rsync_cmd,
                    stdout=subprocess.PIPE,  # Capture but don't display
                    stderr=subprocess.PIPE,  # Capture errors
                    text=True,
                    timeout=3600  # 1 hour timeout per artist
                )

                if result.returncode == 0:
                    # Rsync handles incremental updates automatically
                    # If destination exists, it's an update; otherwise it's a new copy
                    status = "Updated" if dest_exists else "Copied"
                    print(f"[{idx}/{total_artists}] ({percentage}%) {artist_folder} ... ✅ {status}")
                    copied_count += 1
                else:
                    error_msg = result.stderr.strip() or "rsync failed"
                    print(f"[{idx}/{total_artists}] ({percentage}%) {artist_folder} ... ❌ ERROR: {error_msg}")
                    errors.append((artist_folder, error_msg))

            except subprocess.TimeoutExpired:
                error_msg = "Timeout (exceeded 1 hour)"
                print(f"[{idx}/{total_artists}] ({percentage}%) {artist_folder} ... ❌ ERROR: {error_msg}")
                errors.append((artist_folder, error_msg))
            except Exception as e:
                error_msg = str(e)
                print(f"[{idx}/{total_artists}] ({percentage}%) {artist_folder} ... ❌ ERROR: {error_msg}")
                errors.append((artist_folder, error_msg))

        return (copied_count, skipped_count, errors)

    except Exception as e:
        print(f"\n❌ Error reading input folder: {e}")
        return (0, 0, [])


# ============================================================
# MAIN WORKFLOW
# ============================================================

def main():
    """Main interactive workflow."""
    try:
        # Welcome message
        print_welcome()

        # Check for rsync
        if not check_rsync_available():
            print("\n❌ Error: rsync is not available on this system")
            print("\nrsync is required for this tool. Please install rsync:")
            print("  • Windows: Install via WSL, Git Bash, or Cygwin")
            print("  • macOS: Already installed (or install via Homebrew)")
            print("  • Linux: Install via package manager (e.g., apt install rsync)")
            sys.exit(1)

        print("✅ rsync is available\n")

        # Show Navidrome structure info
        print_navidrome_structure_info()

        # Step 1: Get input folder
        input_folder = get_input_folder()
        if not input_folder:
            print("\n❌ Cancelled by user")
            return

        # Step 2: Get output folder
        output_folder = get_output_folder()
        if not output_folder:
            print("\n❌ Cancelled by user")
            return

        # Step 3: Preview and confirm
        if not preview_copy_operation(input_folder, output_folder):
            print("\n❌ Cancelled by user")
            return

        # Step 4: Execute copy
        copied_count, skipped_count, errors = copy_artist_folders_rsync(
            input_folder, output_folder
        )

        # Display summary
        print_summary(copied_count, skipped_count, errors)

        print("\n🎉 All done!\n")
        print("Next steps:")
        print("  1. Verify your music files in the Navidrome music folder")
        print("  2. Update your Navidrome configuration if needed")
        print("  3. Restart Navidrome or trigger a library scan")
        print("  4. Your playlists should now work with the copied music files\n")

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
