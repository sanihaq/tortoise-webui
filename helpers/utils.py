import os
import torch
import torchaudio
from datetime import datetime
from tortoise.api import TextToSpeech, MODELS_DIR
from tortoise.utils.audio import get_voices

from helpers.settings import DEFAULT_SAMPLE_RATE, output_path

tts = None

def load_tts_model(settings):
    global tts
    tts = TextToSpeech(models_dir=MODELS_DIR, use_deepspeed=settings["use_deepspeed"], kv_cache=settings["kv_cache"], half=settings["half_precision"])
    print("\ntts model loaded with")
    print(settings)
    print("\n")

def unload_tts_model():
    global tts
    tts = None
    torch.cuda.empty_cache()  # if using GPU
    print("Model unloaded")

def reload_tts_model(settings):
    unload_tts_model()
    load_tts_model(settings)

def getOutputFolder():
    today = datetime.utcnow().strftime('%Y-%m-%d')
    return f"{output_path}/{today}"

def save_audio(audio, output_file):
    """Helper function to save audio to a file."""
    p = getOutputFolder()
    os.makedirs(p, exist_ok=True)
    torchaudio.save(os.path.join(p, output_file), audio.squeeze(0).cpu(), DEFAULT_SAMPLE_RATE)

def get_voice_list():
    # TODO: add custom voice list, instrad of []
    return list(get_voices([]).keys())
