import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
from datetime import datetime
import subprocess

# Get Python and Spleeter paths
PYTHON_PATH = sys.executable
SPLEETER_PATH = os.path.join(os.path.dirname(PYTHON_PATH), 'spleeter')

def select_audio_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[
            ("Audio Files", "*.mp3 *.wav *.m4a *.flac")
        ]
    )
    return file_path

def select_stem_config():
    root = tk.Tk()
    root.withdraw()
    choice = tk.messagebox.askyesnocancel(
        "Stem Configuration",
        "Select stem configuration:\n\n"
        "Yes = 2 stems (Vocals + Accompaniment)\n"
        "No = 4 stems\n"
        "Cancel = 5 stems"
    )
    if choice is True:
        return "2stems"
    elif choice is False:
        return "4stems"
    else:
        return "5stems"

def create_stems_folder():
    if not os.path.exists("stems"):
        os.makedirs("stems")

def zip_stems(input_file, stems_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    zip_name = f"stems/{base_name}_{timestamp}_stems.zip"
    
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        zipf.write(input_file, os.path.basename(input_file))
        for folder in os.listdir(stems_path):
            folder_path = os.path.join(stems_path, folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    arcname = os.path.join(folder, file)
                    zipf.write(file_path, arcname)

def main():
    audio_file = select_audio_file()
    if not audio_file:
        print("No file selected. Exiting...")
        return

    stem_config = select_stem_config()
    create_stems_folder()

    print(f"Processing audio file with Spleeter ({stem_config})...")
    try:
        # Use Python to call spleeter module directly
        result = subprocess.run([
            PYTHON_PATH, '-m', 'spleeter', 'separate',
            '-p', f'spleeter:{stem_config}',
            '-o', 'stems',
            audio_file
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error processing file:")
            print(result.stderr)
            return
            
        print("Creating zip archive...")
        zip_stems(audio_file, "stems")
        print("Done! Check the stems folder for your processed audio.")
        
    except FileNotFoundError:
        print("Error: Python or Spleeter not found. Please ensure correct installation.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()