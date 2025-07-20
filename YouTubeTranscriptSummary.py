import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import re
import sys

def ensure_youtube_transcript_api():
    try:
        import youtube_transcript_api
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api"])

def get_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Could not extract video ID from the URL.")

def fetch_transcript(video_id, lang="en"):
    from youtube_transcript_api import YouTubeTranscriptApi
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return None

def summarize_text(text, num_sentences=5):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return " ".join(sentences[:num_sentences])

class YouTubeTranscriptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Transcript Analyzer By AJ")
        self.root.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="YouTube Video URL:").pack(anchor=tk.W)
        self.url_entry = ttk.Entry(frm, width=80)







        #if preferabule inital url on the aaa add the line bellow 

        self.url_entry.insert(0, "https://youtu.be/7yDmGnA8Hw0?si=3WPOV1bxE5feqnPq") 
        #https://youtu.be/7yDmGnA8Hw0?si=3WPOV1bxE5feqnPq


        #####################################################################







        self.url_entry.pack(fill=tk.X, pady=5)
        self.url_entry.focus()

        self.fetch_btn = ttk.Button(frm, text="Fetch Transcript", command=self.start_fetch)
        self.fetch_btn.pack(pady=5)

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(frm, textvariable=self.status_var, foreground="blue")
        self.status_label.pack(anchor=tk.W, pady=2)

        self.tab_control = ttk.Notebook(frm)
        self.transcript_tab = ttk.Frame(self.tab_control)
        self.summary_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.transcript_tab, text="Full Transcript")
        self.tab_control.add(self.summary_tab, text="Summary")
        self.tab_control.pack(fill=tk.BOTH, expand=True, pady=10)

        # Transcript Text
        self.transcript_text = scrolledtext.ScrolledText(self.transcript_tab, wrap=tk.WORD, font=("Arial", 11))
        self.transcript_text.pack(fill=tk.BOTH, expand=True)

        # Summary Text
        self.summary_text = scrolledtext.ScrolledText(self.summary_tab, wrap=tk.WORD, font=("Arial", 11))
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Save Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill=tk.X, pady=5)
        self.save_transcript_btn = ttk.Button(btn_frame, text="Save Transcript", command=self.save_transcript)
        self.save_transcript_btn.pack(side=tk.LEFT, padx=5)
        self.save_summary_btn = ttk.Button(btn_frame, text="Save Summary", command=self.save_summary)
        self.save_summary_btn.pack(side=tk.LEFT, padx=5)

    def start_fetch(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a YouTube video URL.")
            return
        self.status_var.set("Fetching transcript...")
        self.transcript_text.delete("1.0", tk.END)
        self.summary_text.delete("1.0", tk.END)
        self.fetch_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.fetch_transcript_thread, args=(url,), daemon=True).start()

    def fetch_transcript_thread(self, url):
        try:
            video_id = get_video_id(url)
        except Exception as e:
            self.status_var.set("Invalid URL.")
            self.fetch_btn.config(state=tk.NORMAL)
            return

        transcript = fetch_transcript(video_id)
        if transcript:
            self.transcript_text.insert(tk.END, transcript)
            summary = summarize_text(transcript, 5)
            self.summary_text.insert(tk.END, summary)
            self.status_var.set("Transcript loaded.")
        else:
            self.status_var.set("Transcript not available for this video.")
        self.fetch_btn.config(state=tk.NORMAL)

    def save_transcript(self):
        text = self.transcript_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No Transcript", "No transcript to save.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Transcript saved to {file}")

    def save_summary(self):
        text = self.summary_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No Summary", "No summary to save.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Summary saved to {file}")

if __name__ == "__main__":
    ensure_youtube_transcript_api()
    root = tk.Tk()
    app = YouTubeTranscriptApp(root)
    root.mainloop()
