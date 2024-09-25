import tkinter as tk
from tkinter import filedialog, messagebox
import librosa
import os
import shutil # manae directories
import json

# Load configuration file
config_file = 'config.json'
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
else:
    config = {'last_folder': ''}
    with open(config_file, 'w') as f:
        json.dump(config, f)

# Get sorter directory and mode from configuration file
sorter_dir = config.get('sorter_dir', '')
mode = config.get('mode', 'light')

# If sorter directory is not set, prompt user to select it
if not sorter_dir:
    sorter_dir = filedialog.askdirectory(title="Select directory to use as sorter folder")
    config['sorter_dir'] = sorter_dir
    with open(config_file, 'w') as f:
        json.dump(config, f)

# Use sorter directory
sorter_path = sorter_dir

def toggle_mode(): # function to toggle between light and dark mode
    global mode
    if root['bg'] == 'white': 
        root.config(bg='#333333')  # Softer gray background
        file_label.config(bg='#333333', fg='white')
        result_label.config(bg='#333333', fg='white')
        open_button.config(bg='gray', fg='white')
        mode_button.config(bg='gray', fg='white')
        quit_button.config(bg='gray', fg='white')
        mode = 'dark'
    else:  # Switch back to light mode
        root.config(bg='white')
        file_label.config(bg='white', fg='black')
        result_label.config(bg='white', fg='black')
        open_button.config(bg='lightgray', fg='black')
        mode_button.config(bg='lightgray', fg='black')
        quit_button.config(bg='lightgray', fg='black')
        mode = 'light'
    config['mode'] = mode
    with open(config_file, 'w') as f:
        json.dump(config, f)
        
def open_file_dialog():
    global config
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")], initialdir=config.get('last_folder', ''))
    if file_path:
        folder_path = os.path.dirname(file_path)
        config['last_folder'] = folder_path
        with open(config_file, 'w') as f:
            json.dump(config, f)
        file_name = file_path.split("/")[-1]  # make the filepath the title
        file_label.config(text=file_name)
        process_audio_file(file_path)
        
        if sorter_dir:
            sorter_path = sorter_dir  # Use the selected directory as the sorter path
            if not os.path.exists(sorter_path):
                os.makedirs(sorter_path)
            
            # Process the audio file and create the BPM range folders
            y, sr = librosa.load(file_path)
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            result_label.config(text=f"Tempo: {tempo:} BPM")
            
            if tempo < 60:
                folder_name = "Below_60_BPM"
            elif 60 <= tempo < 90:
                folder_name = "60_to_90_BPM"
            elif 90 <= tempo < 120:
                folder_name = "90_to_120_BPM"
            elif 120 <= tempo < 150:
                folder_name = "120_to_150_BPM"
            else:
                folder_name = "Above_150_BPM"
            
            bpm_folder_path = os.path.join(sorter_path, folder_name)
            if not os.path.exists(bpm_folder_path):
                os.makedirs(bpm_folder_path)
            # Move the audio file to the BPM range folder
            shutil.move(file_path, bpm_folder_path)
        

# using try accept during audio analizing so program dosent crash if theres a wrong input 
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

# Set mode
if mode == 'dark':
    root.config(bg='#333333')
    file_label.config(bg='#333333', fg='white')
    result_label.config(bg='#333333', fg='white')
    open_button.config(bg='gray', fg='white')
    mode_button.config(bg='gray', fg='white')
    quit_button.config(bg='gray', fg='white')
else:
    root.config(bg='white')
    file_label.config(bg='white', fg='black')
    result_label.config(bg='white', fg='black')
    open_button.config(bg='lightgray', fg='black')
    mode_button.config(bg='lightgray', fg='black')
    quit_button.config(bg='lightgray', fg='black')

root.mainloop()
