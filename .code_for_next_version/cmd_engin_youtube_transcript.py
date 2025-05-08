import sys
import re

def ensure_youtube_transcript_api():
    try:
        import youtube_transcript_api
    except ImportError:
        print("youtube-transcript-api not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api"])
        print("youtube-transcript-api installed. Please rerun the script.")
        sys.exit(0)

def get_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    # Handles various YouTube URL formats
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Could not extract video ID from the URL.")

def fetch_transcript(video_id, lang="en"):
    from youtube_transcript_api import YouTubeTranscriptApi
    try:
        # Try to get transcript in the desired language
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return None

def summarize_text(text, num_sentences=5):
    # Naive summary: just return the first num_sentences sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    return " ".join(sentences[:num_sentences])

def main():
    ensure_youtube_transcript_api()
    url = input("Enter the YouTube video URL: ").strip()
    try:
        video_id = get_video_id(url)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\nFetching transcript...")
    transcript = fetch_transcript(video_id)
    if transcript:
        print("\n=== Full Transcript ===\n")
        print(transcript)
        print("\n=== Summary (first 5 sentences) ===\n")
        print(summarize_text(transcript, 5))
    else:
        print("Transcript not available for this video or in the desired language.")

if __name__ == "__main__":
    main()
