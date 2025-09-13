import streamlit as st
import yt_dlp
import os
import subprocess
import tempfile
from pathlib import Path

def get_downloads_folder():
    """Get the Downloads folder path for the current user."""
    home = Path.home()
    downloads_folder = home / "Downloads"
    return str(downloads_folder)

def clean_youtube_url(url):
    """Clean and validate YouTube URL."""
    import re
    
    # Remove extra parameters that might cause issues
    if '&' in url:
        url = url.split('&')[0]
    
    # Ensure it's a valid YouTube URL
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in youtube_patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"
    
    return url  # Return original if no pattern matches

def get_video_info(url):
    """Get video information without downloading."""
    ydl_opts = {
        'quiet': False,  # Show warnings for debugging
        'no_warnings': False,
        'extract_flat': False,
        'socket_timeout': 30,  # 30 second timeout
        'retries': 3,  # Retry up to 3 times
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                return True, info
            else:
                return False, "No video information found"
    except Exception as e:
        error_msg = str(e)
        # Provide more specific error messages
        if "Private video" in error_msg:
            return False, "This video is private and cannot be accessed"
        elif "Video unavailable" in error_msg:
            return False, "This video is unavailable (may be deleted or restricted)"
        elif "Sign in to confirm your age" in error_msg:
            return False, "This video is age-restricted and requires sign-in"
        elif "Video not available" in error_msg:
            return False, "This video is not available in your region"
        elif "HTTP Error 403" in error_msg:
            return False, "Access denied - video may be restricted"
        elif "HTTP Error 404" in error_msg:
            return False, "Video not found - may be deleted or URL is incorrect"
        elif "timeout" in error_msg.lower():
            return False, "Request timed out - video may be unavailable or slow to load"
        else:
            return False, f"Error: {error_msg}"

def download_video(url, output_folder, start_time=None, end_time=None, audio_only=False):
    """Download YouTube video using yt-dlp with specified options."""
    if audio_only:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
            'no_warnings': False,
            'extract_flat': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }
    else:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
            'no_warnings': False,
            'extract_flat': False,
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info first to get the title
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # Check if video formats are available
            formats = info.get('formats', [])
            video_formats = [f for f in formats if f.get('vcodec') != 'none']
            
            if not video_formats:
                return False, "No video formats available for this URL", None, duration
            
            # Download the video
            ydl.download([url])
            
            # Find the downloaded file - look for .mp4 or .mp3 files
            file_extension = '.mp3' if audio_only else '.mp4'
            downloaded_files = []
            for file in os.listdir(output_folder):
                if file.endswith(file_extension):
                    # Check if the filename contains the video title (with some flexibility)
                    title_clean = video_title.replace(' ', '').replace('｜', '').replace('|', '').lower()
                    file_clean = file.replace(' ', '').replace('｜', '').replace('|', '').lower()
                    
                    # Check if video title is contained in filename or vice versa
                    if (title_clean in file_clean or file_clean in title_clean or 
                        any(word in file_clean for word in title_clean.split() if len(word) > 3)):
                        downloaded_files.append(os.path.join(output_folder, file))
            
            if downloaded_files:
                # Get the most recently created file
                file_path = max(downloaded_files, key=os.path.getctime)
                
                # If trimming is requested, use ffmpeg to trim the video
                if start_time is not None and end_time is not None:
                    trimmed_path = trim_video(file_path, start_time, end_time, video_title)
                    if trimmed_path:
                        # Clean up the original full video file
                        try:
                            os.remove(file_path)
                        except:
                            pass  # Ignore if file can't be deleted
                        return True, trimmed_path, video_title, duration
                    else:
                        return False, "Failed to trim video", video_title, duration
                
                return True, file_path, video_title, duration
            else:
                # If no specific match, look for any recent files
                import time
                recent_files = []
                current_time = time.time()
                for file in os.listdir(output_folder):
                    if file.endswith(file_extension):
                        file_path = os.path.join(output_folder, file)
                        # Check if file was created in the last 5 minutes
                        if (current_time - os.path.getctime(file_path)) < 300:
                            recent_files.append(file_path)
                
                if recent_files:
                    file_path = max(recent_files, key=os.path.getctime)
                    
                    # If trimming is requested, use ffmpeg to trim the video
                    if start_time is not None and end_time is not None:
                        trimmed_path = trim_video(file_path, start_time, end_time, video_title)
                        if trimmed_path:
                            # Clean up the original full video file
                            try:
                                os.remove(file_path)
                            except:
                                pass  # Ignore if file can't be deleted
                            return True, trimmed_path, video_title, duration
                        else:
                            return False, "Failed to trim video", video_title, duration
                    
                    return True, file_path, video_title, duration
                else:
                    return False, "Video downloaded but MP4 file not found", video_title, duration
                
    except Exception as e:
        return False, f"Download failed: {str(e)}", None, 0

def trim_video(input_path, start_time, end_time, video_title):
    """Trim video using ffmpeg."""
    import time
    try:
        # Create output filename
        output_folder = get_downloads_folder()
        
        # Clean filename for filesystem - keep more characters but remove problematic ones
        safe_title = "".join(c for c in video_title if c.isalnum() or c in "._- ").strip()
        # Remove multiple spaces and replace with single space
        safe_title = " ".join(safe_title.split())
        # Limit filename length
        if len(safe_title) > 100:
            safe_title = safe_title[:100]
        
        output_filename = f"{safe_title}_clip.mp4"
        output_path = os.path.join(output_folder, output_filename)
        
        # Debug: Show the paths being used
        st.info(f"Input file: {input_path}")
        st.info(f"Output file: {output_path}")
        
        # Run ffmpeg command with better seeking to avoid white screen
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),  # Seek before input for better accuracy
            '-i', input_path,
            '-t', str(end_time - start_time),  # Use duration instead of end time
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-y',  # Overwrite output file if it exists
            output_path
        ]
        
        # Execute ffmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
        else:
            # Try with a different approach for better keyframe handling
            st.warning("First attempt failed, trying with re-encoding for better accuracy...")
            
            # Alternative command with re-encoding to avoid keyframe issues
            cmd2 = [
                'ffmpeg',
                '-ss', str(start_time),
                '-i', input_path,
                '-t', str(end_time - start_time),
                '-c:v', 'libx264',  # Re-encode video to avoid keyframe issues
                '-c:a', 'aac',      # Re-encode audio
                '-preset', 'fast',   # Fast encoding
                '-crf', '23',        # Good quality
                '-y',
                output_path
            ]
            
            result2 = subprocess.run(cmd2, capture_output=True, text=True)
            
            if result2.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                # Try with a simpler filename as final fallback
                st.warning("Re-encoding failed, trying with simpler filename...")
                simple_filename = f"video_clip_{int(time.time())}.mp4"
                simple_output_path = os.path.join(output_folder, simple_filename)
                
                cmd2[8] = simple_output_path  # Update the output path
                result3 = subprocess.run(cmd2, capture_output=True, text=True)
                
                if result3.returncode == 0 and os.path.exists(simple_output_path):
                    return simple_output_path
                else:
                    st.error(f"FFmpeg error: {result.stderr}")
                    st.error(f"Re-encoding error: {result2.stderr}")
                    st.error(f"Final fallback error: {result3.stderr}")
                    st.error(f"Commands used: {' '.join(cmd)} | {' '.join(cmd2)}")
                    return None
            
    except FileNotFoundError:
        st.error("FFmpeg not found. Please install FFmpeg and add it to your PATH.")
        return None
    except Exception as e:
        st.error(f"Error trimming video: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="YouTube Video Downloader & Trimmer",
        page_icon="📥",
        layout="wide"
    )
    
    st.title("📥 YouTube Video Downloader & Trimmer")
    st.markdown("Download YouTube videos in the highest available quality or trim specific segments!")
    
    # Get Downloads folder path
    downloads_folder = get_downloads_folder()
    
    # Create input field for YouTube URL
    url = st.text_input(
        "Enter YouTube Video URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste the YouTube video URL you want to download"
    )
    
    # Initialize session state for video info
    if 'video_info' not in st.session_state:
        st.session_state.video_info = None
    if 'video_duration' not in st.session_state:
        st.session_state.video_duration = 0
    
    # Get video info when URL is provided
    if url and ("youtube.com" in url or "youtu.be" in url):
        if st.button("🔍 Get Video Info", type="secondary"):
            with st.spinner("Getting video information..."):
                # Clean the URL first
                cleaned_url = clean_youtube_url(url)
                if cleaned_url != url:
                    st.info(f"🔧 Cleaned URL: {cleaned_url}")
                
                success, info = get_video_info(cleaned_url)
                if success:
                    st.session_state.video_info = info
                    st.session_state.video_duration = info.get('duration', 0)
                    st.success("✅ Video information loaded!")
                else:
                    st.error(f"❌ Failed to get video info: {info}")
                    st.info("💡 Try these solutions:")
                    st.markdown("- Check if the video is public and not age-restricted")
                    st.markdown("- Try copying the URL again from YouTube")
                    st.markdown("- Some videos may be region-blocked")
    elif url and not ("youtube.com" in url or "youtu.be" in url):
        st.warning("⚠️ Please enter a valid YouTube URL")
    
    # Display video preview and controls
    if st.session_state.video_info:
        video_info = st.session_state.video_info
        duration = st.session_state.video_duration
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📺 Video Preview")
            st.video(url)
            
            # Video details
            st.markdown(f"**Title:** {video_info.get('title', 'Unknown')}")
            st.markdown(f"**Duration:** {duration // 60}:{duration % 60:02d}")
            st.markdown(f"**Uploader:** {video_info.get('uploader', 'Unknown')}")
        
        with col2:
            st.subheader("✂️ Trim Settings")
            
            # Time selection
            max_duration = duration if duration > 0 else 3600  # Default to 1 hour if duration unknown
            
            # Time input in MM:SS format
            col_time1, col_time2 = st.columns(2)
            
            with col_time1:
                start_time_str = st.text_input(
                    "Start Time :",
                    value="0:00",
                    help="Format: minutes:seconds (e.g., 1:30)"
                )
            
            with col_time2:
                end_time_str = st.text_input(
                    "End Time :",
                    value="1:00",
                    help="Format: minutes:seconds (e.g., 2:45)"
                )
            
            # Convert MM:SS to seconds
            def parse_time_to_seconds(time_str):
                try:
                    if ':' in time_str:
                        parts = time_str.split(':')
                        if len(parts) == 2:
                            minutes, seconds = int(parts[0]), int(parts[1])
                            return minutes * 60 + seconds
                    return int(time_str)  # Fallback to seconds if no colon
                except:
                    return 0
            
            start_time = parse_time_to_seconds(start_time_str)
            end_time = parse_time_to_seconds(end_time_str)
            
            # Validate time inputs
            if start_time >= max_duration:
                start_time = 0
            if end_time > max_duration:
                end_time = max_duration
            if end_time <= start_time:
                end_time = start_time + 1
            
            # Duration display
            clip_duration = end_time - start_time
            st.info(f"**Clip Duration:** {clip_duration // 60}:{clip_duration % 60:02d}")
            
            # Download options
            st.subheader("📥 Download Options")
            
            # Download type selection
            download_type = st.radio(
                "Choose download type:",
                ["🎥 Video (MP4)", "🎵 Audio Only (MP3)"],
                horizontal=True
            )
            
            is_audio_only = download_type == "🎵 Audio Only (MP3)"
            
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                if st.button("🚀 Download Full", type="primary", use_container_width=True):
                    with st.spinner(f"Downloading {'audio' if is_audio_only else 'video'}... Please wait."):
                        success, result, title, _ = download_video(url, downloads_folder, audio_only=is_audio_only)
                    
                    if success:
                        file_type = "Audio" if is_audio_only else "Video"
                        st.success(f"✅ {file_type} downloaded successfully!")
                        st.info(f"**File saved as:** `{os.path.basename(result)}`")
                        st.info(f"**Location:** `{result}`")
                        if is_audio_only:
                            st.info("**Quality:** 320 kbps MP3")
                    else:
                        st.error(f"❌ Download failed: {result}")
            
            with col_dl2:
                # Only show trimming for video downloads
                if not is_audio_only:
                    # Validate time inputs before allowing download
                    time_valid = True
                    if start_time >= end_time:
                        st.warning("⚠️ End time must be greater than start time")
                        time_valid = False
                    elif start_time < 0 or end_time < 0:
                        st.warning("⚠️ Time values must be positive")
                        time_valid = False
                    elif end_time > max_duration:
                        st.warning(f"⚠️ End time exceeds video duration ({max_duration // 60}:{max_duration % 60:02d})")
                        time_valid = False
                    
                    if st.button("✂️ Download Selected Part", type="primary", use_container_width=True, disabled=not time_valid):
                        if time_valid:
                            with st.spinner("Downloading and trimming video... Please wait."):
                                success, result, title, _ = download_video(url, downloads_folder, start_time, end_time)
                            
                            if success:
                                st.success(f"✅ Video clip downloaded successfully!")
                                st.info(f"**File saved as:** `{os.path.basename(result)}`")
                                st.info(f"**Location:** `{result}`")
                                st.info(f"**Duration:** {clip_duration // 60}:{clip_duration % 60:02d}")
                            else:
                                st.error(f"❌ Download failed: {result}")
                        else:
                            st.error("❌ Please fix the time inputs before downloading")
                else:
                    st.info("🎵 Audio trimming not available - download full audio track")
    
    # Instructions
    st.markdown("---")
    col_inst1, col_inst2 = st.columns(2)
    

if __name__ == "__main__":
    main()
