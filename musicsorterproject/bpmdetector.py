import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
import librosa
import os
import shutil 
import json
import numpy 
from mutagen._file import File

class BPMFileSorter:
    BPM_RANGES = {
        (0, 60): "Below_60_BPM",
        (60, 90): "60_to_90_BPM",
        (90, 120): "90_to_120_BPM",
        (120, 150): "120_to_150_BPM",
        (150, 300): "Above_150_BPM"
    }

    def __init__(self, sorter_dir):
        self.sorter_dir = sorter_dir

    def get_bpm_folder(self, tempo):
        for (low, high), folder in self.BPM_RANGES.items():
            if low <= tempo < high:
                return folder
        return "Above_150_BPM"

    def organize_file(self, file_path, tempo):
        folder_name = self.get_bpm_folder(tempo)
        dest_folder = os.path.join(self.sorter_dir, folder_name)
        os.makedirs(dest_folder, exist_ok=True)
        shutil.copy(file_path, dest_folder)

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {'last_folder': '', 'sorter_dir': '', 'mode': 'light'}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value

sorted_file_path = None # intitalize gmobal

# Load configuration file
config_manager = ConfigManager()

# Get sorter directory and mode from configuration file
sorter_dir = config_manager.get('sorter_dir', '')
mode = config_manager.get('mode', 'light')

# If sorter directory is not set, prompt user to select it
if not sorter_dir:
    sorter_dir = filedialog.askdirectory(title="Select directory to use as sorter folder")
    config_manager.set('sorter_dir', sorter_dir)
    with open(config_file, 'w') as f:
        config_manager.save_config()

# Use sorter directory
sorter_path = sorter_dir

def toggle_mode():  # Function to toggle between light and dark mode
    global mode
    if mode == 'light':
        apply_dark_mode([root, main_frame, settings_frame, metadata_frame])
        apply_dark_mode(main_widgets)
        apply_dark_mode(settings_widgets)
        apply_dark_mode(metadata_widgets)
        mode = 'dark'
    else:
        apply_light_mode([root, main_frame, settings_frame, metadata_frame])
        apply_light_mode(main_widgets)
        apply_light_mode(settings_widgets)
        apply_light_mode(metadata_widgets)
        mode = 'light'
    
    config_manager.set('mode', mode)
    config_manager.save_config()

def apply_dark_mode(widgets):
    for widget in widgets:
        widget.config(bg='#373737')
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

def display_metadata(file_path):
    try:
        audio = File(file_path)  # Load the audio file using mutagen
        metadata = {}
        
        if audio is not None:
            metadata['Title'] = audio.get('TIT2', 'Unknown')  # Title
            metadata['Artist'] = audio.get('TPE1', 'Unknown')  # Artist
            metadata['Album'] = audio.get('TALB', 'Unknown')  # Album
            metadata['Duration'] = round(audio.info.length, 2) if audio.info else 'Unknown'  # Duration in seconds
            metadata['Sample Rate'] = audio.info.sample_rate if audio.info else 'Unknown'
        
        # Display metadata in the UI
        metadata_label.config(text=f"Title: {metadata['Title']}\n"
                                   f"Artist: {metadata['Artist']}\n"
                                   f"Album: {metadata['Album']}\n"
                                   f"Duration: {metadata['Duration']} sec\n"
                                   f"Sample Rate: {metadata['Sample Rate']} Hz")
            
    except Exception as e:
        print(f"Error retrieving metadata: {e}")
        metadata_label.config(text="Error reading metadata.")

# Using try-except during audio analyzing so program doesn't crash if there's a wrong input
def get_tempo(file_path):
    try:
        y, sr = librosa.load(file_path)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        return tempo

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing the file:\n{e}")     

def detect_key(file_path):
    y, sr = librosa.load(file_path)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key = numpy.argmax(chroma.mean(axis=1))  # Simplified key detection
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    detected_key = keys[key]
    key_label.config(text=f"key: {keys[key]}")
        
def open_file_dialog():
    global sorted_file_path
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")],
                                           initialdir=config_manager.get('last_folder', ''))
    if file_path:
        folder_path = os.path.dirname(file_path)
        config_manager.set('last_folder', folder_path)
        config_manager.save_config()
        
        file_name = file_path.split("/")[-1]
        file_label.config(text=file_name)

        tempo = get_tempo(file_path)
        result_label.config(text=f"Tempo: {tempo:} BPM")    
        detect_key(file_path)
        display_metadata(file_path)

        if sorter_dir:
            # Create file sorter instance and organize the file
            file_sorter = BPMFileSorter(sorter_dir)
            file_sorter.organize_file(file_path, tempo)
            destination_label.config(text=f"File organized in {file_sorter.get_bpm_folder(tempo)}")

            # Process the audio file and create the BPM range folders

# Switch to the settings frame
def show_settings():
    main_frame.pack_forget()
    settings_frame.pack(fill='both', expand=True)
    if mode == 'dark':
        apply_dark_mode(settings_widgets)
    else:
        apply_light_mode(settings_widgets)
        
def show_metadata_frame():
    global sorted_file_path
    main_frame.pack_forget()  # Hide the main frame
    metadata_frame.pack(fill='both', expand=True)

    # Display the metadata from the selected file
    if sorted_file_path:
        metadata = display_metadata(sorted_file_path)

        if metadata:
            metadata_text = (f"Title: {metadata['Title']}\n"
                          f"Artist: {metadata['Artist']}\n"
                          f"Album: {metadata['Album']}\n"
                          f"Duration: {metadata['Duration']} sec\n"
                          f"Sample Rate: {metadata['Sample Rate']} Hz")
        else:
            metadata_text = "No metadata found or error loading metadata."

        metadata_label.config(text=metadata_text)
        
        # store scraped metadata in the json file to acces a history of scanned files and their results

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
root.geometry("550x450")
root.config(bg='white')

# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Build the path to the image files
light_mode_image = PhotoImage(file=os.path.join(base_dir, 'light_mode.png')) 
dark_mode_image = PhotoImage(file=os.path.join(base_dir, 'dark_mode.png'))      

# Main frame (the initial window)
main_frame = tk.Frame(root, bg='white')
main_frame.pack(fill='both', expand=True)

file_label = tk.Label(main_frame, text="No file selected", bg='white', fg='black', wraplength=350)
file_label.pack(pady=20)

open_button = tk.Button(main_frame, text="Choose Audio File", command=open_file_dialog, bg='lightgray', fg='black')
open_button.pack(pady=10)

result_label = tk.Label(main_frame, text="", bg='white', fg='black', wraplength=350, font=("Helvetica", 13))
result_label.pack(pady=(10, 5))

key_label = tk.Label(main_frame, text="", bg='white', fg='black', wraplength=350, font=("Helvetica", 13))
key_label.pack(pady=5)

destination_label = tk.Label(main_frame, text="", bg='white', fg='black', wraplength=350, font=("Helvetica", 13))
destination_label.pack(pady=25)

quit_button = tk.Button(main_frame, text="Quit", command=root.quit, bg='lightgray', fg='black')
quit_button.pack(side="bottom", pady=20)

# Create a settings buttohttps://www.washingtonpost.com/crossword-puzzles/daily/?id=tca241003&set=wapo-daily&puzzleType=crossword&playId=405b5858-2d0a-4089-aa08-cb3fe076888an
settings_button = tk.Button(main_frame, text="Settings", command=show_settings)
settings_button.pack(pady=(0, 10))

metadata_button = tk.Button(main_frame, text="Show Metadata", command=show_metadata_frame, bg='lightgray', fg='black')
metadata_button.pack(pady=(10, 10))

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
browse_button.pack(pady=(35, 3))

description = tk.Label(settings_frame, text="changes where analized audio files are stored and sorted", bg='white', fg='black')
description.pack(pady=(0, 10))

def save_settings():
    new_path = sorter_path_label.cget("text").replace("Current directory: ", "")
    config_manager.set('sorter_dir', new_path)
    config_manager.save_config()
    show_main()
    
def back_to_main():
    # Go back to the main frame
    metadata_frame.pack_forget()  # Hide the metadata frame
    main_frame.pack(fill='both', expand=True)

mode_label = tk.Label(settings_frame, image=light_mode_image)
mode_label.pack(pady=(20, 3))

description_mode = tk.Label(settings_frame, text="Light / Dark", bg='white', fg='black')
description_mode.pack(pady=(0, 30))

mode_label.bind("<Button-1>", lambda e: toggle_mode())

save_button = tk.Button(settings_frame, text="Save", command=save_settings)
save_button.pack(pady=20)

metadata_frame = tk.Frame(root, bg='white')

# Label to display the metadata
metadata_label = tk.Label(metadata_frame, text="Metadata will be displayed here", bg='white', fg='black', wraplength=350)
metadata_label.pack(pady=20)

# Back button to go back to the main frame
back_button = tk.Button(metadata_frame, text="Back", command=back_to_main, bg='lightgray', fg='black')
back_button.pack(pady=20)


# Collect all widgets for universal theme toggle
main_widgets = [file_label, result_label, key_label, destination_label, open_button, quit_button, metadata_button, settings_button]
settings_widgets = [sorter_path_label, browse_button, save_button, mode_label, description, description_mode]
metadata_widgets = [metadata_label, back_button]

# Set mode based on config
if mode == 'dark':
    apply_dark_mode([root, main_frame, settings_frame, metadata_frame])
    apply_dark_mode(main_widgets)
    apply_dark_mode(settings_widgets)
    apply_dark_mode(metadata_widgets)
else:
    apply_light_mode([root, main_frame, settings_frame, metadata_frame])
    apply_light_mode(main_widgets)
    apply_light_mode(settings_widgets)
    apply_light_mode(metadata_widgets)

root.mainloop()
