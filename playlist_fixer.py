import os
import re
import shutil
import sys

# ============================================================
# Interactive iTunes Playlist Converter
# ============================================================
# Converts iTunes playlists from Windows paths to Linux/relative paths
# for use with Navidrome or other music servers
# ============================================================


# ============================================================
# UI/DISPLAY FUNCTIONS
# ============================================================

def print_welcome():
    """Display welcome message and instructions."""
    print("\n" + "=" * 60)
    print("iTunes Playlist Converter for Navidrome")
    print("=" * 60)
    print("\nThis tool converts iTunes .m3u playlists from Windows paths")
    print("to Linux/relative paths for use with Navidrome.\n")


def print_summary(success_count, error_count, errors, output_folder):
    """Display conversion summary report."""
    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    print(f"✅ Success: {success_count} playlist(s)")
    print(f"❌ Errors: {error_count} playlist(s)")

    if errors:
        print("\nError details:")
        for filename, error_msg in errors:
            print(f"  - {filename}: {error_msg}")

    print(f"\n📁 Output location: {output_folder}")


def print_preview(sample_conversions):
    """Display sample path conversions for user confirmation."""
    print("\n" + "=" * 60)
    print("PREVIEW: Sample Path Conversions")
    print("=" * 60)
    for original, converted in sample_conversions:
        print(f"\nBefore: {original}")
        print(f"After:  {converted}")


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


def find_m3u_files(folder_path):
    """Find all .m3u and .m3u8 files in the folder."""
    try:
        files = [f for f in os.listdir(folder_path)
                if f.endswith(".m3u") or f.endswith(".m3u8")]
        return files
    except (OSError, PermissionError):
        return []


# ============================================================
# CONFIGURATION FUNCTIONS
# ============================================================

def get_input_folder():
    """Prompt user for input folder and validate it."""
    while True:
        print("\n" + "-" * 60)
        print("Step 1: Input Folder")
        print("-" * 60)
        print("Enter the path to your folder containing iTunes .m3u files.")
        print("(You can drag and drop the folder here)")

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

        # Check for .m3u files
        m3u_files = find_m3u_files(path)
        if not m3u_files:
            print(f"\n❌ Error: No .m3u or .m3u8 files found in: {path}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        print(f"\n✅ Found {len(m3u_files)} playlist file(s)")
        return path


def auto_detect_windows_prefix(input_folder):
    """Auto-detect Windows prefix from first playlist file."""
    print("\n" + "-" * 60)
    print("Step 2: Auto-Detect Windows Path Prefix")
    print("-" * 60)

    m3u_files = find_m3u_files(input_folder)
    if not m3u_files:
        return None

    first_file = os.path.join(input_folder, m3u_files[0])

    try:
        # Try UTF-8 first
        try:
            with open(first_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            print(f"⚠️  Warning: Encoding issues in {m3u_files[0]}, using fallback encoding")
            with open(first_file, 'r', encoding='latin-1') as f:
                lines = f.readlines()

        # Find first non-comment, non-empty line
        sample_path = None
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                sample_path = line
                break

        if not sample_path:
            print("❌ Could not find a valid path in the playlist file")
            return None

        print(f"\nSample path found:")
        print(f"  {sample_path}\n")

        # Try to extract prefix (everything before the artist folder)
        # Common pattern: C:/Users/Tom/Music/iTunes/iTunes Media/Music/Artist/Album/Song.mp3
        # We want: C:/Users/Tom/Music/iTunes/iTunes Media/Music/

        # Convert backslashes to forward slashes for consistency
        sample_path_normalized = sample_path.replace("\\", "/")

        # Try to find "Music/" as a common ending point
        music_index = sample_path_normalized.lower().rfind("/music/")
        if music_index != -1:
            # Include the /Music/ part
            suggested_prefix = sample_path_normalized[:music_index + 7]
        else:
            # Fallback: take everything up to the last 3 path components
            # (usually Artist/Album/Song.mp3)
            parts = sample_path_normalized.split("/")
            if len(parts) > 3:
                suggested_prefix = "/".join(parts[:-3]) + "/"
            else:
                suggested_prefix = ""

        if suggested_prefix:
            print(f"Auto-detected prefix:")
            print(f"  {suggested_prefix}")
            print(f"\nThis prefix will be REMOVED from all paths.")
            confirm = input("\nUse this prefix? (y/n): ").strip().lower()

            if confirm == 'y':
                return suggested_prefix

        # Manual entry
        print("\nEnter the Windows path prefix manually.")
        print("(This is the part that will be REMOVED from all paths)")
        print("Example: C:/Users/Tom/Music/iTunes/iTunes Media/Music/")
        prefix = input("\nWindows prefix: ").strip()

        # Normalize and ensure it ends with /
        prefix = prefix.replace("\\", "/")
        if prefix and not prefix.endswith("/"):
            prefix += "/"

        return prefix

    except Exception as e:
        print(f"❌ Error reading playlist file: {e}")
        return None


def get_linux_prefix():
    """Prompt user to choose Linux prefix replacement."""
    print("\n" + "-" * 60)
    print("Step 3: Choose Linux Path Prefix")
    print("-" * 60)
    print("\nWhat should replace the Windows prefix?")
    print("\n1. Relative paths: ../")
    print("   (Recommended - portable, works if you move folders)")
    print("\n2. Absolute Docker paths: /music/")
    print("   (For Docker containers with /music mount)")
    print("\n3. Custom prefix")
    print("   (Enter your own)")

    while True:
        choice = input("\nChoice (1/2/3): ").strip()

        if choice == '1':
            return "../"
        elif choice == '2':
            return "/music/"
        elif choice == '3':
            custom = input("Enter custom prefix: ").strip()
            # Normalize slashes
            custom = custom.replace("\\", "/")
            # Ensure it ends with /
            if custom and not custom.endswith("/"):
                custom += "/"
            return custom
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def preview_conversion(input_folder, windows_prefix, linux_prefix):
    """Show sample conversions and ask for confirmation."""
    m3u_files = find_m3u_files(input_folder)
    if not m3u_files:
        return False

    first_file = os.path.join(input_folder, m3u_files[0])

    try:
        # Read first file
        try:
            with open(first_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(first_file, 'r', encoding='latin-1') as f:
                lines = f.readlines()

        # Find up to 3 sample paths
        samples = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                # Convert path
                cleaned = stripped.replace("\\", "/")
                pattern = re.escape(windows_prefix)
                converted = re.sub(pattern, linux_prefix, cleaned, flags=re.IGNORECASE)
                samples.append((stripped, converted))
                if len(samples) >= 3:
                    break

        if samples:
            print_preview(samples)
            print("\n" + "-" * 60)
            confirm = input("\nProceed with conversion? (y/n): ").strip().lower()
            return confirm == 'y'
        else:
            print("\n⚠️  Warning: No valid paths found to preview")
            confirm = input("Proceed anyway? (y/n): ").strip().lower()
            return confirm == 'y'

    except Exception as e:
        print(f"❌ Error creating preview: {e}")
        return False


# ============================================================
# CONVERSION FUNCTIONS
# ============================================================

def convert_single_playlist(input_path, output_path, windows_prefix, linux_prefix):
    """
    Convert a single playlist file.
    Returns (success: bool, track_count: int, error_msg: str)
    """
    try:
        # Read file with proper encoding handling
        try:
            with open(input_path, 'r', encoding='utf-8') as f_in:
                lines = f_in.readlines()
        except UnicodeDecodeError:
            # Fallback to latin-1
            with open(input_path, 'r', encoding='latin-1') as f_in:
                lines = f_in.readlines()

        new_lines = []
        track_count = 0

        for line in lines:
            # Skip comments (lines starting with #)
            if line.startswith("#"):
                new_lines.append(line)
                continue

            # Fix: Strip line endings BEFORE processing to avoid corruption
            cleaned_line = line.rstrip('\r\n')

            # Skip empty lines
            if not cleaned_line:
                new_lines.append('\n')
                continue

            # 1. Replace Windows backslashes (\) with Linux forward slashes (/)
            cleaned_line = cleaned_line.replace("\\", "/")

            # 2. Replace the Windows path with the Linux path (case-insensitive)
            # Fix: Use regex with IGNORECASE flag for case-insensitive replacement
            if windows_prefix:
                pattern = re.escape(windows_prefix)
                cleaned_line = re.sub(pattern, linux_prefix, cleaned_line, flags=re.IGNORECASE)

            # Re-add normalized line ending
            new_lines.append(cleaned_line + '\n')
            track_count += 1

        # Write the new file
        with open(output_path, 'w', encoding='utf-8') as f_out:
            f_out.writelines(new_lines)

        return (True, track_count, None)

    except PermissionError as e:
        return (False, 0, f"Permission denied: {e}")
    except Exception as e:
        return (False, 0, str(e))


def fix_playlists_batch(input_folder, output_folder, windows_prefix, linux_prefix):
    """
    Convert all playlists in the input folder.
    Returns (success_count, error_count, errors_list)
    """
    # Create output folder if it doesn't exist
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    except Exception as e:
        print(f"\n❌ Error creating output folder: {e}")
        return (0, 0, [])

    # Get list of playlist files
    m3u_files = find_m3u_files(input_folder)
    total_files = len(m3u_files)

    if total_files == 0:
        print("\n❌ No playlist files found")
        return (0, 0, [])

    print("\n" + "=" * 60)
    print("CONVERTING PLAYLISTS")
    print("=" * 60 + "\n")

    success_count = 0
    error_count = 0
    errors = []

    for idx, filename in enumerate(m3u_files, 1):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # Calculate percentage
        percentage = int((idx / total_files) * 100)

        # Convert the playlist
        success, track_count, error_msg = convert_single_playlist(
            input_path, output_path, windows_prefix, linux_prefix
        )

        if success:
            print(f"[{idx}/{total_files}] ({percentage}%) {filename} ... ✅ {track_count} tracks")
            success_count += 1
        else:
            print(f"[{idx}/{total_files}] ({percentage}%) {filename} ... ❌ ERROR: {error_msg}")
            error_count += 1
            errors.append((filename, error_msg))

    return (success_count, error_count, errors)


# ============================================================
# NETWORK SHARE FUNCTIONS
# ============================================================

def get_network_destination():
    """
    Prompt user for network share destination.
    Returns validated path or None.
    """
    print("\n" + "=" * 60)
    print("OPTIONAL: Copy to Network Share")
    print("=" * 60)
    print("\nWould you like to copy the converted playlists to a network share?")
    print("(e.g., NAS, Samba share, NFS mount)")

    copy_network = input("\nCopy to network share? (y/n): ").strip().lower()

    if copy_network != 'y':
        return None

    while True:
        print("\nEnter the network share path:")
        print("  Windows UNC: \\\\server\\share\\playlists")
        print("  Linux mount: /mnt/nas/playlists")

        path = input("\nNetwork path: ").strip()

        # Remove quotes
        path = path.strip('"').strip("'")

        # Normalize path
        path = os.path.normpath(path)

        # Validate path exists
        if not validate_path_exists(path):
            print(f"\n❌ Error: Network path does not exist or is not accessible: {path}")
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

        print(f"\n✅ Network share validated: {path}")
        return path


def copy_to_network_share(source_folder, dest_path):
    """
    Copy converted playlists to network share.
    Returns (success_count, error_count, errors_list)
    """
    # Get list of files to copy
    try:
        files = [f for f in os.listdir(source_folder)
                if f.endswith(".m3u") or f.endswith(".m3u8")]
    except Exception as e:
        print(f"\n❌ Error reading source folder: {e}")
        return (0, 0, [])

    if not files:
        print("\n❌ No files to copy")
        return (0, 0, [])

    # Confirmation
    print(f"\n⚠️  About to copy {len(files)} file(s) to:")
    print(f"   {dest_path}")
    print("\nExisting files with the same name will be overwritten!")

    confirm = input("\nProceed with copy? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n❌ Network copy cancelled")
        return (0, 0, [])

    print("\n" + "=" * 60)
    print("COPYING TO NETWORK SHARE")
    print("=" * 60 + "\n")

    success_count = 0
    error_count = 0
    errors = []
    total_files = len(files)

    for idx, filename in enumerate(files, 1):
        source_file = os.path.join(source_folder, filename)
        dest_file = os.path.join(dest_path, filename)

        try:
            # Copy file preserving metadata
            shutil.copy2(source_file, dest_file)
            print(f"[{idx}/{total_files}] Copying {filename} ... ✅")
            success_count += 1
        except Exception as e:
            print(f"[{idx}/{total_files}] Copying {filename} ... ❌ ERROR: {e}")
            error_count += 1
            errors.append((filename, str(e)))

    # Summary
    print("\n" + "-" * 60)
    print(f"✅ Copied: {success_count} file(s)")
    print(f"❌ Errors: {error_count} file(s)")

    if errors:
        print("\nError details:")
        for filename, error_msg in errors:
            print(f"  - {filename}: {error_msg}")

    return (success_count, error_count, errors)


# ============================================================
# MAIN WORKFLOW
# ============================================================

def main():
    """Main interactive workflow."""
    try:
        # Welcome message
        print_welcome()

        # Step 1: Get input folder
        input_folder = get_input_folder()
        if not input_folder:
            print("\n❌ Cancelled by user")
            return

        # Step 2: Auto-detect Windows prefix
        windows_prefix = auto_detect_windows_prefix(input_folder)
        if not windows_prefix:
            print("\n❌ Could not determine Windows prefix")
            return

        # Step 3: Get Linux prefix
        linux_prefix = get_linux_prefix()
        if not linux_prefix:
            print("\n❌ Invalid Linux prefix")
            return

        # Step 4: Preview and confirm
        if not preview_conversion(input_folder, windows_prefix, linux_prefix):
            print("\n❌ Cancelled by user")
            return

        # Step 5: Execute conversion
        output_folder = os.path.join(input_folder, "converted_for_linux")
        success_count, error_count, errors = fix_playlists_batch(
            input_folder, output_folder, windows_prefix, linux_prefix
        )

        # Display summary
        print_summary(success_count, error_count, errors, output_folder)

        # Step 6: Optional network share copy
        if success_count > 0:
            network_path = get_network_destination()
            if network_path:
                copy_to_network_share(output_folder, network_path)

        print("\n🎉 All done!\n")

    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
