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
    except Exception:
        return None

def summarize_text(text, num_sentences=5):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return " ".join(sentences[:num_sentences])

class YouTubeTranscriptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Transcript Summary")
        self.root.geometry("820x650")
        self.root.minsize(600, 400)
        self.create_widgets()

    def create_widgets(self):
        # Top frame for URL input
        url_frame = ttk.Frame(self.root, padding=15)
        url_frame.pack(fill=tk.X)
        ttk.Label(url_frame, text="YouTube Video URL:").pack(anchor=tk.W)
        self.url_entry = ttk.Entry(url_frame, width=85)
        self.url_entry.pack(fill=tk.X, pady=(0, 10))
        self.url_entry.insert(0, "https://youtu.be/7yDmGnA8Hw0?si=3WPOV1bxE5feqnPq")
        self.url_entry.focus()

        # Buttons (Fetch & Clear)
        btn_frame = ttk.Frame(self.root, padding=(10,0))
        btn_frame.pack(fill=tk.X)
        self.fetch_btn = ttk.Button(btn_frame, text="Fetch Transcript", command=self.start_fetch)
        self.fetch_btn.pack(side=tk.LEFT)
        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_all)
        self.clear_btn.pack(side=tk.LEFT, padx=10)

        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, foreground="blue")
        self.status_label.pack(anchor=tk.W, pady=(5, 0))

        # Tabbed notebook for transcript & summary
        self.tab_control = ttk.Notebook(self.root)
        self.transcript_tab = ttk.Frame(self.tab_control)
        self.summary_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.transcript_tab, text="Full Transcript")
        self.tab_control.add(self.summary_tab, text="Summary")
        self.tab_control.pack(fill=tk.BOTH, expand=True, pady=10)

        # Transcript text area
        self.transcript_text = scrolledtext.ScrolledText(self.transcript_tab, wrap=tk.WORD, font=("Arial", 11))
        self.transcript_text.pack(fill=tk.BOTH, expand=True)

        # Summary text area
        self.summary_text = scrolledtext.ScrolledText(self.summary_tab, wrap=tk.WORD, font=("Arial", 11))
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Save Buttons (Initially disabled)
        save_frame = ttk.Frame(self.root, padding=(10,10))
        save_frame.pack(fill=tk.X)
        self.save_transcript_btn = ttk.Button(save_frame, text="Save Transcript", command=self.save_transcript)
        self.save_transcript_btn.pack(side=tk.LEFT, padx=5)
        self.save_summary_btn = ttk.Button(save_frame, text="Save Summary", command=self.save_summary)
        self.save_summary_btn.pack(side=tk.LEFT, padx=5)
        self.update_save_buttons(False, False)

        # Tooltips (via hover events)
        self.add_tooltips()

    def add_tooltips(self):
        # Simple tooltip implementation for major controls
        self._create_tooltip(self.url_entry, "Paste your YouTube URL here.")
        self._create_tooltip(self.fetch_btn, "Fetches and displays the transcript for the video.")
        self._create_tooltip(self.clear_btn, "Clears all fields and status.")
        self._create_tooltip(self.save_transcript_btn, "Save the entire transcript to a text file.")
        self._create_tooltip(self.save_summary_btn, "Save the summary to a text file.")

    def _create_tooltip(self, widget, text):
        tip = tk.Toplevel(widget)
        tip.withdraw()
        tip.overrideredirect(True)
        lbl = tk.Label(tip, text=text, background="#ffffe0", relief="solid", borderwidth=1,
                       font=("Arial", 9))
        lbl.pack()
        def show_tip(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tip.geometry(f"+{x}+{y}")
            tip.deiconify()
        def hide_tip(event):
            tip.withdraw()
        widget.bind("<Enter>", show_tip)
        widget.bind("<Leave>", hide_tip)

    def start_fetch(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a YouTube video URL.")
            return
        self.status_var.set("Fetching transcript...")
        self.transcript_text.delete("1.0", tk.END)
        self.summary_text.delete("1.0", tk.END)
        self.fetch_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        self.update_save_buttons(False, False)
        threading.Thread(target=self.fetch_transcript_thread, args=(url,), daemon=True).start()

    def fetch_transcript_thread(self, url):
        try:
            video_id = get_video_id(url)
        except Exception:
            self.set_status_and_reset("Invalid URL.", is_error=True)
            return

        transcript = fetch_transcript(video_id)
        if transcript:
            self.root.after(0, self.display_transcript, transcript)
        else:
            self.set_status_and_reset("Transcript not available for this video.", is_error=True)

    def display_transcript(self, transcript):
        self.transcript_text.insert(tk.END, transcript)
        summary = summarize_text(transcript, 5)
        self.summary_text.insert(tk.END, summary)
        self.status_var.set("Transcript loaded.")
        self.fetch_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.NORMAL)
        self.update_save_buttons(True, True)

    def set_status_and_reset(self, message, is_error=False):
        self.status_var.set(message)
        self.fetch_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.NORMAL)
        self.update_save_buttons(False, False)

    def update_save_buttons(self, transcript_ready, summary_ready):
        self.save_transcript_btn.config(state=(tk.NORMAL if transcript_ready else tk.DISABLED))
        self.save_summary_btn.config(state=(tk.NORMAL if summary_ready else tk.DISABLED))

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

    def clear_all(self):
        self.url_entry.delete(0, tk.END)
        self.status_var.set("")
        self.transcript_text.delete("1.0", tk.END)
        self.summary_text.delete("1.0", tk.END)
        self.update_save_buttons(False, False)
        self.url_entry.focus()

if __name__ == "__main__":
    ensure_youtube_transcript_api()
    root = tk.Tk()
    app = YouTubeTranscriptApp(root)
    root.mainloop()
