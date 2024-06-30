import os
import gradio as gr
from datetime import datetime
from gradio_calendar import Calendar
from helpers.settings import output_path

def extract_timestamp(file_path):
    """
    Extract the timestamp from the file path.
    """
    filename = file_path.split('/')[-1]
    timestamp = filename.split('.')[0]
    return timestamp

def sort_files_by_time(file_paths):
    """
    Sort the file paths based on the extracted timestamp.
    """
    def extract_time_components(timestamp):
        """
        Extract hour, minute, and second from the timestamp.
        """
        try:
            time_part = timestamp.split('_')[0]
            time_obj = datetime.strptime(time_part, '%Y-%m-%d-%H-%M-%S')
            return time_obj
        except ValueError:
            return None

    file_paths_with_time = [(file, extract_time_components(extract_timestamp(file))) for file in file_paths]
    sorted_file_paths = sorted(
        [f for f, t in file_paths_with_time if t is not None],
        key=lambda f: extract_time_components(extract_timestamp(f)),
        reverse=True
    )
    return sorted_file_paths

def list_audio_files(date):
    today = date.strftime('%Y-%m-%d')
    p = f"{output_path}/{today}"
    files = []
    if os.path.exists(p):
        files = [os.path.join(p, f) for f in os.listdir(p) if f.endswith(('.wav'))]
    return sort_files_by_time(files)

def listFiles(date):
    files = list_audio_files(date)
    return [gr.update(choices=getDropdownData(files)) ,gr.update(value=files, label=getFilesLabel(files))]

def getFilesLabel(files):
    return "No files for the day" if files == [] else f"files: {len(files)}"

def extract_filename(path):
    return path.split('/')[-1]

def getDropdownData(files):
    return [(extract_filename(path), path) for path in files] 

def play_audio(file_path):
    return file_path

def selectAudio(audio):
    return gr.update(value=audio, label=extract_filename(audio))

with gr.Blocks() as outputsInterface:
    date = datetime.utcnow()
    files = list_audio_files(date)

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                calendar=Calendar(type="datetime", label="Choose a Date", info="to List All the Audio generated that Day")
                audioDropdown = gr.Dropdown(label="select Audio", choices=getDropdownData(files))
                filesList = gr.Files(label=getFilesLabel(files), value=files, file_types=[".wav"], interactive=False)
        with gr.Column(scale=2):
            with gr.Group():
                play=gr.Audio(interactive=False, autoplay=True)
                with gr.Row():
                    move1 = gr.Button("Move To 1")
                    move2 = gr.Button("Move To 2")
                    star = gr.Button("Add a Star", variant="primary")
            with gr.Row():
                with gr.Column():
                    with gr.Group():
                        loc1=gr.Dropdown(label="Location 1")
                        loc1_s=gr.Dropdown(label="Select Audio")
                        loc1_f=gr.File( interactive=False)
                with gr.Column():
                    with gr.Group():
                        loc2=gr.Dropdown(label="Location 2")
                        loc2_s=gr.Dropdown(label="Select Audio")
                        loc2_f=gr.Files( interactive=False)
                
        calendar.change(listFiles, inputs=calendar, outputs=[audioDropdown, filesList])
        audioDropdown.change(fn=selectAudio, inputs=audioDropdown, outputs=play)
        loc1_s.change(fn=selectAudio, inputs=loc1_s, outputs=play)
        loc2_s.change(fn=selectAudio, inputs=loc2_s, outputs=play)
