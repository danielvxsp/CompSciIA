import tkinter as tk
from tkinter import filedialog, messagebox
import librosa
import os

# function to toggle between light and dark mode
def toggle_mode():
    if root['bg'] == 'white': 
        root.config(bg='black')
        file_label.config(bg='black', fg='white')
        result_label.config(bg='black', fg='white')
        open_button.config(bg='gray', fg='white')
        mode_button.config(bg='gray', fg='white')
        quit_button.config(bg='gray', fg='white')
    else:  # Switch back to light mode
        root.config(bg='white')
        file_label.config(bg='white', fg='black')
        result_label.config(bg='white', fg='black')
        open_button.config(bg='lightgray', fg='black')
        mode_button.config(bg='lightgray', fg='black')
        quit_button.config(bg='lightgray', fg='black')

def open_file_dialog():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
    if file_path:
        file_name = file_path.split("/")[-1]  # make the filepath the title
        file_label.config(text=file_name)
        process_audio_file(file_path)

# using try accept during audoanalizing so program dosent crash if theres a wrong input 
def process_audio_file(file_path):
    try:
        y, sr = librosa.load(file_path)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        result_label.config(text=f"Tempo: {tempo:} BPM")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing the file:\n{e}")

root = tk.Tk()
root.title("Audio Tempo Detector with Light/Dark Mode")
root.geometry("400x300")

root.config(bg='white')

file_label = tk.Label(root, text="No file selected", bg='white', fg='black', wraplength=350)
file_label.pack(pady=10)

open_button = tk.Button(root, text="Choose Audio File", command=open_file_dialog, bg='lightgray', fg='black')
open_button.pack(pady=10)

result_label = tk.Label(root, text="", bg='white', fg='black', wraplength=350, font=("Helvetica", 13))
result_label.pack(pady=25)

# button to change between light and dark modes
mode_button = tk.Button(root, text="Mode", command=toggle_mode, bg='lightgray', fg='black', width=6, height=1)
mode_button.place(x=10, y=10)  # Positioned in the top-left corner

quit_button = tk.Button(root, text="Quit", command=root.quit, bg='lightgray', fg='black')
quit_button.pack(side="bottom", pady=10)

root.resizable(True, True)

root.mainloop()
