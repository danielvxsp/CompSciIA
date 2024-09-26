import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
import librosa
import os
import shutil
import json

# Load configuration file
config_file = 'config.json'
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
else:
    config = {'last_folder': '', 'sorter_dir': '', 'mode': 'light'}
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

def toggle_mode():  # Function to toggle between light and dark mode
    global mode
    if mode == 'light':
        apply_dark_mode([root, main_frame, settings_frame])
        apply_dark_mode(main_widgets)
        apply_dark_mode(settings_widgets)
        mode = 'dark'
    else:
        apply_light_mode([root, main_frame, settings_frame])
        apply_light_mode(main_widgets)
        apply_light_mode(settings_widgets)
        mode = 'light'
    
    config['mode'] = mode
    with open(config_file, 'w') as f:
        json.dump(config, f)

def apply_dark_mode(widgets):
    for widget in widgets:
        widget.config(bg='#333333')
        # Only apply 'fg' to widgets that have text
        if isinstance(widget, (tk.Label, tk.Button, tk.Entry)):
            widget.config(fg='white')
            mode_label.config(image=dark_mode_image)

def apply_light_mode(widgets):
    for widget in widgets:
        widget.config(bg='white')
        # Only apply 'fg' to widgets that have text
        if isinstance(widget, (tk.Label, tk.Button, tk.Entry)):
            widget.config(fg='black')
            mode_label.config(image=light_mode_image)

def open_file_dialog():
    global config
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")],
                                           initialdir=config.get('last_folder', ''))
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

# Using try-except during audio analyzing so program doesn't crash if there's a wrong input
def process_audio_file(file_path):
    try:
        y, sr = librosa.load(file_path)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        result_label.config(text=f"Tempo: {tempo:} BPM")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing the file:\n{e}")

# Switch to the settings frame
def show_settings():
    main_frame.pack_forget()
    settings_frame.pack(fill='both', expand=True)
    if mode == 'dark':
        apply_dark_mode(settings_widgets)
    else:
        apply_light_mode(settings_widgets)

# Switch back to the main frame
def show_main():
    settings_frame.pack_forget()
    main_frame.pack(fill='both', expand=True)
    if mode == 'dark':
        apply_dark_mode(main_widgets)
    else:
        apply_light_mode(main_widgets)

# Create the main window
root = tk.Tk()
root.title("Audio Sorter")
root.geometry("400x300")
root.config(bg='white')

light_mode_image = PhotoImage(file='music sorter project/light_mode.png') 
dark_mode_image = PhotoImage(file='music sorter project/dark_mode.png')    

# Main frame (the initial window)
main_frame = tk.Frame(root, bg='white')
main_frame.pack(fill='both', expand=True)

file_label = tk.Label(main_frame, text="No file selected", bg='white', fg='black', wraplength=350)
file_label.pack(pady=10)

open_button = tk.Button(main_frame, text="Choose Audio File", command=open_file_dialog, bg='lightgray', fg='black')
open_button.pack(pady=10)

result_label = tk.Label(main_frame, text="", bg='white', fg='black', wraplength=350, font=("Helvetica", 13))
result_label.pack(pady=25)

quit_button = tk.Button(main_frame, text="Quit", command=root.quit, bg='lightgray', fg='black')
quit_button.pack(side="bottom", pady=10)

# Create a settings button
settings_button = tk.Button(main_frame, text="Settings", command=show_settings)
settings_button.pack(pady=(0, 10))

# Settings frame (this will replace the main frame when opened)
settings_frame = tk.Frame(root, bg='white')

# Label to display the current sorter directory
sorter_path_label = tk.Label(settings_frame, text=f"Current directory: {sorter_dir}", bg='white', fg='black', wraplength=350)
sorter_path_label.pack(pady=10)

def browse_sorter_path():
    new_sorter_path = filedialog.askdirectory()
    if new_sorter_path:
        config['sorter_dir'] = new_sorter_path
        sorter_path_label.config(text=f"Current directory: {new_sorter_path}")

browse_button = tk.Button(settings_frame, text="Chose Directory", command=browse_sorter_path)
browse_button.pack(pady=(20, 3))

description = tk.Label(settings_frame, text="changes where analized audio files are stored and sorted", bg='white', fg='black')
description.pack(pady=(0, 10))

def save_settings():
    config['sorter_dir'] = sorter_path_label.cget("text").replace("Current directory: ", "")
    with open(config_file, 'w') as f:
        json.dump(config, f)
    show_main()

mode_label = tk.Label(settings_frame, image=light_mode_image)
mode_label.pack(pady=(20, 3))

description_mode = tk.Label(settings_frame, text="Light / Dark", bg='white', fg='black')
description_mode.pack(pady=(0, 10))

mode_label.bind("<Button-1>", lambda e: toggle_mode())

save_button = tk.Button(settings_frame, text="Back", command=save_settings)
save_button.pack(pady=20)

# Collect all widgets for universal theme toggle
main_widgets = [file_label, result_label, open_button, quit_button, settings_button]
settings_widgets = [sorter_path_label, browse_button, save_button, mode_label, description, description_mode]

# Set mode based on config
if mode == 'dark':
    apply_dark_mode([root, main_frame, settings_frame])
    apply_dark_mode(main_widgets)
    apply_dark_mode(settings_widgets)
else:
    apply_light_mode([root, main_frame, settings_frame])
    apply_light_mode(main_widgets)
    apply_light_mode(settings_widgets)

root.mainloop()
