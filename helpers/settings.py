import os
import json

MAXIMUM_CANDIDATE_ABSOLUTE = 99
DEFAULT_SAMPLE_RATE = 24000
output_path = 'outputs/'
config_file = "config.json"

default_settings = {
    "candidates_max_value": 10,
    "produce_debug_state": False,
    "use_deepspeed": False,
    "kv_cache": True,
    "half_precision": True
}

settings = {}

def copySettings():
    s = settings.copy()
    return s

def settingsToDefault():
    global settings
    settings = default_settings.copy()
    return settings

def load_settings():
    global settings
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            settings = json.load(f)
    else:
        settingsToDefault()
    return settings

def save_settings():
    global settings
    with open(config_file, 'w') as f:
        json.dump(settings, f)
