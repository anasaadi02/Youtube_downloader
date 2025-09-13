# YouTube Video Downloader

A simple and user-friendly YouTube video downloader built with Python, Streamlit, and yt-dlp. Download YouTube videos in the highest available quality with a clean web interface.

## Features

- 🎥 Download YouTube videos in highest available quality (video + audio merged)
- 📁 Automatically saves to your Downloads folder
- 🌐 Clean and intuitive Streamlit web interface
- ✅ Success/error messages with file information
- 🔧 Uses yt-dlp with optimized settings for best quality

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

## Usage

1. **Run the Streamlit app**
   ```bash
   streamlit run youtube_downloader.py
   ```

2. **Open your web browser**
   - The app will automatically open at `http://localhost:8501`
   - If it doesn't open automatically, copy the URL from the terminal

3. **Download a video**
   - Paste a YouTube video URL in the input field
   - Click the "Download Video" button
   - Wait for the download to complete
   - Find your video in the Downloads folder!

## Requirements

- Python 3.7 or higher
- Internet connection
- Windows, macOS, or Linux

## Dependencies

- `streamlit` - Web interface framework
- `yt-dlp` - YouTube video downloader
- `pathlib` - Cross-platform path handling (built-in)
- `os` - Operating system interface (built-in)

## How it works

The script uses yt-dlp with the following optimized settings:
- `format: "bestvideo+bestaudio/best"` - Downloads the best available video and audio, then merges them
- `merge_output_format: "mp4"` - Outputs in MP4 format
- `outtmpl` - Saves files with the video title as filename in the Downloads folder

## Troubleshooting

- **"Please enter a valid YouTube URL"**: Make sure you're using a complete YouTube URL (e.g., `https://www.youtube.com/watch?v=...`)
- **Download failed**: Check your internet connection and try again. Some videos may be restricted or unavailable
- **File not found**: The video was downloaded but the filename might be slightly different due to special characters

## License

This project is open source and available under the MIT License.
