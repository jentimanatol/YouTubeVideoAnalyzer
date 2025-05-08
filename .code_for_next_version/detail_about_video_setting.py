import sys
import subprocess

def ensure_pytubefix():
    try:
        import pytubefix
    except ImportError:
        print("pytubefix not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytubefix"])
        print("pytubefix installed. Please rerun the script.")
        sys.exit(0)

def format_filesize(bytes_size):
    if bytes_size is None:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def analyze_youtube_video(url):
    from pytubefix import YouTube
    try:
        yt = YouTube(url)
        result = []
        result.append("=== YouTube Video Analysis ===\n")
        result.append(f"Title: {yt.title}")
        result.append(f"Author: {yt.author}")
        result.append(f"Length: {yt.length} seconds ({yt.length // 60}:{yt.length % 60:02d})")
        result.append(f"Views: {yt.views:,}")
        try:
            result.append(f"Publish Date: {yt.publish_date}")
        except Exception:
            result.append("Publish Date: Not available")
        desc = yt.description.replace('\n', ' ')
        if len(desc) > 200:
            desc = desc[:200] + "..."
        result.append(f"Description: {desc}\n")

        # Streams
        result.append("=== Available Streams ===\n")
        result.append("Progressive Streams (video + audio):")
        progressive = yt.streams.filter(progressive=True).order_by('resolution')
        if progressive:
            for stream in progressive:
                result.append(
                    f"  - Resolution: {stream.resolution}, Format: {stream.mime_type}, "
                    f"Size: {format_filesize(stream.filesize)}, itag: {stream.itag}"
                )
        else:
            result.append("  No progressive streams available.")
        result.append("\nAdaptive Streams (video only):")
        video_only = yt.streams.filter(adaptive=True, only_video=True).order_by('resolution')
        if video_only:
            for stream in video_only:
                result.append(
                    f"  - Resolution: {stream.resolution}, Format: {stream.mime_type}, "
                    f"FPS: {stream.fps}, Size: {format_filesize(stream.filesize)}, itag: {stream.itag}"
                )
        else:
            result.append("  No video-only streams available.")
        result.append("\nAudio Only Streams:")
        audio_only = yt.streams.filter(only_audio=True).order_by('abr')
        if audio_only:
            for stream in audio_only:
                result.append(
                    f"  - Bitrate: {stream.abr}, Format: {stream.mime_type}, "
                    f"Size: {format_filesize(stream.filesize)}, itag: {stream.itag}"
                )
        else:
            result.append("  No audio-only streams available.")

        # Captions
        result.append("\n=== Available Captions ===")
        captions = yt.captions
        if captions:
            for caption in captions:
                result.append(f"  - {caption.name} ({caption.code})")
        else:
            result.append("  No captions available.")

        return '\n'.join(result)
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    ensure_pytubefix()
    print("YouTube Video Analyzer\n" + "="*23)
    url = input("Enter the YouTube video URL: ").strip()
    print("\nAnalyzing video...\n")
    analysis = analyze_youtube_video(url)
    print(analysis)
    save = input("\nSave this analysis to a file? (y/n): ").strip().lower()
    if save == 'y':
        fname = input("Enter filename [default: analysis.txt]: ").strip()
        if not fname:
            fname = "analysis.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(analysis)
        print(f"Analysis saved to {fname}")

if __name__ == "__main__":
    main()
