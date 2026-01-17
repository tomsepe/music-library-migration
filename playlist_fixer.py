import os

# Here is the Python script to help automate the migration of your iTunes playlists for playback in Navidrome.

# Why you need this
# iTunes exports playlists using Windows absolute paths (e.g., C:\Users\Tom\Music\...). Your Docker container (Navidrome) looks for files using Linux paths (e.g., /music/...).

# If you upload the raw iTunes files, Navidrome will see the playlist name but show 0 tracks because it cannot find C:\ on a Linux server. This script fixes the slashes and swaps the file paths for you.

# --- CONFIGURATION (EDIT THESE 3 LINES) ---
# 1. Where are your iTunes .m3u files right now? (Use forward slashes / even on Windows)

# instruct user:
# Export Playlists: In iTunes, go to File > Library > Export Playlist and save them as .m3u to a folder on your Desktop (e.g., iTunes_Playlists).

# NED CODE: ask user to input path to to input folder and store in variable:
INPUT_FOLDER = "path to input folder or individual music file"

# 2. What part of the path needs to be removed? 
#    (Open an .m3u in Notepad to see exactly how iTunes wrote it)
WINDOWS_PREFIX = "C:/Users/Tom/Music/iTunes/iTunes Media/Music/"

# 3. What should replace it? 
#    Use "../" for relative paths (Recommended - works if you move folders later)
#    OR use "/music/" if you want absolute Docker paths.
LINUX_PREFIX = "../" 

# --- THE LOGIC ---
def fix_playlists():
    # Create an output folder so we don't overwrite originals
    output_folder = os.path.join(INPUT_FOLDER, "converted_for_linux")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    count = 0
    print(f"Scanning: {INPUT_FOLDER}...\n")

    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".m3u") or filename.endswith(".m3u8"):
            input_path = os.path.join(INPUT_FOLDER, filename)
            output_path = os.path.join(output_folder, filename)
            
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
                if WINDOWS_PREFIX in cleaned_line:
                    cleaned_line = cleaned_line.replace(WINDOWS_PREFIX, LINUX_PREFIX)
                
                new_lines.append(cleaned_line)

            # Write the new file
            with open(output_path, 'w', encoding='utf-8') as f_out:
                f_out.writelines(new_lines)
            
            print(f"✅ Fixed: {filename}")
            count += 1

    print(f"\n🎉 Done! {count} playlists converted.")
    print(f"📁 Find them here: {output_folder}")

# additional function to create:
# ask user for path to samba share or nfs share to copy the files to
# move the files
# party time!

if __name__ == "__main__":
    fix_playlists()