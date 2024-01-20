import numpy as np
import soundfile as sf
import pyaudio
import tkinter as tk
from tkinter import ttk, filedialog
import threading
import Helium
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AudioProcessor:
    def __init__(self):
        self.chunk = 1024 * 4
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.rate = 16000
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.player = None
        self.recording = False
        self.save_path = None
        self.recorded_data = []

        self.root = tk.Tk()
        self.root.title("Audio Processor")

        # Wyśrodkowanie okna
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"600x600+{x}+{y}")
        self.root.resizable(width=False, height=False)

        # Przycisk nagrywania
        self.start_button = ttk.Button(self.root, text="Start/Stop", command=self.toggle_recording, style="TButton")
        self.start_button.grid(row=0, column=0, pady=(50, 0), padx=(20, 20), sticky=tk.N)

        # Dioda
        self.indicator_led = tk.Canvas(self.root, width=20, height=20, bg="red", relief=tk.GROOVE)
        self.indicator_led.grid(row=1, column=0, pady=(10, 0), padx=(20, 20), sticky=tk.N)

        # Status
        self.status_label = tk.Label(self.root, text="Stopped", font=('Arial', 10))
        self.status_label.grid(row=2, column=0, pady=(0, 30), padx=(20, 20), sticky=tk.N)

        # Wykres
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.ax.set_title('Przebieg czasowo-amplitudowy')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=3, column=0, pady=(0, 40), padx=(50, 50), sticky=tk.N)

        # Przycisk zapisu
        self.save_button = ttk.Button(self.root, text="Save File", command=self.save_to_file, style="TButton", state=tk.DISABLED)
        self.save_button.grid(row=4, column=0, pady=(0, 50), padx=(20, 20), sticky=tk.N)

        # Styl przycisków
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10, font=('Arial', 12), background='#000000', foreground='#000000', relief=tk.GROOVE)

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recorded_data = []
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        self.player = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk
        )

        self.recording = True
        self.start_button.config(text="Stop Recording")
        self.indicator_led.configure(bg="green")
        self.status_label.config(text="Recording...")
        self.save_button.config(state=tk.DISABLED)
        threading.Thread(target=self.process_audio).start()

    def stop_recording(self):
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.player:
            self.player.stop_stream()
            self.player.close()
        self.start_button.config(text="Start/Stop")
        self.indicator_led.configure(bg="red")
        self.status_label.config(text="Stopped")
        self.save_button.config(state=tk.NORMAL)

    def process_audio(self):
        while self.recording:
            data = np.fromstring(self.stream.read(self.chunk), dtype=np.float32)
            helium = Helium.voice2hel(data)
            self.recorded_data.extend(helium)
            self.player.write(helium, self.chunk)

            # Aktualizowanie wykresu
            self.ax.clear()
            self.ax.plot(np.arange(len(self.recorded_data)) / self.rate, self.recorded_data)
            self.ax.set_title('Przebieg czasowo-amplitudowy')
            self.ax.grid(True)
            self.canvas.draw()

    def save_to_file(self):
        if not self.save_path:
            self.save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Wave files", "*.wav")])
        if self.save_path:
            sf.write(self.save_path, np.array(self.recorded_data), self.rate)

    def run_gui(self):
        self.root.mainloop()

if __name__ == "__main__":
    audio_processor = AudioProcessor()
    audio_processor.run_gui()
