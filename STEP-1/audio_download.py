import os
import yt_dlp
import json # Import json to pretty-print options

def save_youtube_audio_from_input():
    """
    Prompts the user for a YouTube URL, then downloads the audio-only
    version of the video and saves it as an MP3 file, prepending the
    video's upload date to the filename.
    """
    # --- Get URL from User Input ---
    url = input("Please enter the YouTube URL: ")

    if not url:
        print("No URL entered. Exiting.")
        return

    # --- Set up yt-dlp Options ---
    output_folder = "downloaded_audio"
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        print(f"Creating output directory: {output_folder}")
        os.makedirs(output_folder)

    # Define yt-dlp options. This dictionary configures how yt-dlp
    # will download and process the video.
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(upload_date)s_%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        
        # This option explicitly tells ffmpeg which protocols to use,
        # which can help when dealing with live streams.
        'downloader_args': {'ffmpeg': ['-protocol_whitelist', 'file,http,https,tcp,tls,rtmp,udp']},
        
        'writedescription': False,
        'writeinfojson': False,
        'writethumbnail': False,
        
        # Set 'verbose': True to get detailed debug output from yt-dlp
        # This will show exactly what yt-dlp and ffmpeg are doing.
        'verbose': True, 
        
        # --- MODIFIED LINE ---
        # Set 'noplaylist': True to ensure only the single video from the URL is downloaded,
        # even if the URL is part of a playlist. This forces single video download.
        'noplaylist': True,
    }

    print("\n--- yt-dlp Options Being Used ---")
    print(json.dumps(ydl_opts, indent=4))
    print("---------------------------------\n")

    print(f"\nAttempting to download audio from: {url}")

    try:
        # Create a YoutubeDL object with the defined options and initiate the download.
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print("\nDownload and conversion successful!")

    except yt_dlp.utils.DownloadError as e:
        # Catch specific yt-dlp download errors.
        print(f"\nAn error occurred during download: {e}")
    except Exception as e:
        # Catch any other unexpected errors.
        print(f"\nAn unexpected error occurred: {e}")


# --- Main execution block ---
if __name__ == "__main__":
    save_youtube_audio_from_input()
