import gradio as gr
import sys

sys.path.append("../tortoise-tts")

from helpers.utils import load_tts_model
from helpers.settings import load_settings

settings = load_settings()

load_tts_model(settings)

from pages.quick_gen import quickInterface
from pages.settings_page import settingsInterface
from pages.outputs_page import outputsInterface

with gr.Blocks() as app:
    with gr.Tab("Quick Text to Speech"):
        quickInterface.render()
    with gr.Tab("Outputs"):
        outputsInterface.render()
    with gr.Tab("Settings"):
        settingsInterface.render()

if __name__ == "__main__":
    app.queue().launch()
