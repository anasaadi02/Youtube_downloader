# YouTube Video Downloader & Trimmer

A powerful and user-friendly YouTube video downloader and trimmer built with Python, Streamlit, yt-dlp, and FFmpeg. Download YouTube videos in the highest available quality, extract MP3 audio, or trim specific segments with a clean web interface.

## Features

- 🎥 **Video Download**: MP4 format in highest available quality
- 🎵 **Audio Download**: MP3 format at 320 kbps (best quality)
- ✂️ **Video Trimming**: Cut specific segments from videos with precise time control
- 📁 **Smart File Management**: Automatically saves to Downloads folder
- 🌐 **Clean Interface**: Intuitive Streamlit web interface with video preview
- ⚡ **Fast Processing**: Optimized yt-dlp settings for best performance
- 🔧 **Error Handling**: Comprehensive error detection and user-friendly messages
- 📱 **Responsive Design**: Works on all devices and screen sizes

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd video-downloader
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg** (required for video trimming and audio conversion)
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

## Usage

1. **Run the Streamlit app**
   ```bash
   streamlit run youtube_downloader.py
   ```

2. **Open your web browser**
   - The app will automatically open at `http://localhost:8501`
   - If it doesn't open automatically, copy the URL from the terminal

3. **Download videos or audio**
   - Paste a YouTube video URL in the input field
   - Click "Get Video Info" to load video details and preview
   - Choose download type: Video (MP4) or Audio (MP3)
   - Click "Download Full" for complete video/audio
   - Or set start/end times and click "Download Selected Part" for video trimming
   - Find your files in the Downloads folder!

## Quick Start Guide

### 📥 Full Download
1. Paste YouTube URL → Click "Get Video Info"
2. Choose Video (MP4) or Audio (MP3)
3. Click "Download Full"
4. Find your file in Downloads folder!

### ✂️ Video Trimming
1. Paste YouTube URL → Click "Get Video Info"
2. Select "Video (MP4)" option
3. Set start time (e.g., 1:30) and end time (e.g., 3:45)
4. Click "Download Selected Part"
5. Get your trimmed video clip!

## Requirements

- Python 3.7 or higher
- Internet connection
- FFmpeg (for video trimming and audio conversion)
- Windows, macOS, or Linux

## Dependencies

- `streamlit` - Web interface framework
- `yt-dlp` - YouTube video downloader
- `ffmpeg` - Video/audio processing (external dependency)
- `pathlib` - Cross-platform path handling (built-in)
- `os` - Operating system interface (built-in)
- `subprocess` - Process management (built-in)

## How it works

### Video Download
- Uses yt-dlp with optimized settings for best quality
- `format: "bestvideo+bestaudio/best"` - Downloads best video and audio, then merges them
- `merge_output_format: "mp4"` - Outputs in MP4 format
- `outtmpl` - Saves files with video title as filename

### Audio Download
- Extracts audio using yt-dlp's postprocessor
- Converts to MP3 format at 320 kbps (highest standard quality)
- Uses FFmpeg for audio conversion

### Video Trimming
- Downloads full video first
- Uses FFmpeg to trim specific time segments
- Automatically cleans up original file after trimming
- Supports precise MM:SS time format input

## Troubleshooting

### Common Issues
- **"Please enter a valid YouTube URL"**: Make sure you're using a complete YouTube URL
- **"Video is private/age-restricted"**: Some videos cannot be downloaded due to restrictions
- **"FFmpeg not found"**: Install FFmpeg and add it to your system PATH
- **"Request timed out"**: Video may be unavailable or slow to load

### Error Messages
- **Age-restricted content**: Video requires sign-in to confirm age
- **Geographic restrictions**: Video not available in your region
- **Private video**: Video is private and cannot be accessed
- **Video unavailable**: Video may be deleted or restricted

### Performance Tips
- Use clean YouTube URLs without extra parameters
- Ensure stable internet connection for large files
- Close other bandwidth-intensive applications during download

