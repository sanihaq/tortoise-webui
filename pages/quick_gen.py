import sys
import os
import torch
import torchaudio
import gradio as gr
from datetime import datetime

from tortoise.utils.audio import load_voices

from helpers.utils import tts, save_audio, getOutputFolder, get_voice_list
from helpers.settings import settings, MAXIMUM_CANDIDATE_ABSOLUTE

def quick_text_to_speech(
    text="The expressiveness of autoregressive transformers is literally nuts! I absolutely adore them.",
    voice=['random'],
    preset='fast',
    candidates=1,
    seed = None,
    cvvp_amount = 0.0
):
    """Generate speech from text using a given voice and preset."""

    if torch.backends.mps.is_available():
        use_deepspeed = False

    results = []

    voice_samples, conditioning_latents = load_voices(voice)

    gen, dbg_state = tts.tts_with_preset(
        text, k=candidates, voice_samples=voice_samples,
        conditioning_latents=conditioning_latents, preset=preset,
        use_deterministic_seed=seed, return_deterministic_state=True,
        cvvp_amount=cvvp_amount
    )

    id = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    out = getOutputFolder()
    # Save generated audio
    if isinstance(gen, list):
        for j, g in enumerate(gen):
            output_file =  f'{id}_{j}.wav'
            save_audio(g, output_file)
            results.append(gr.Audio( value=f"{out}/{output_file}", visible=True))
    else:
        output_file = f'{id}.wav'
        save_audio(gen, output_file)
        results.append(gr.Audio(value=f"{out}/{output_file}", visible=True))

    results += [gr.update(visible=False) for _ in range(MAXIMUM_CANDIDATE_ABSOLUTE - candidates)]

    if settings["produce_debug_state"] == True:
            os.makedirs('debug_states', exist_ok=True)
            torch.save(dbg_state, f'debug_states/quick_gen_{selected_voice}.pth')

    return results


def submit_action(text, voice, additional_voices, preset, candidates, seed, cvvp, progress=gr.Progress(track_tqdm=True)):
    progress(0, desc="Starting...")
    # Disable the submit button
    yield [gr.update(value="wait for generation to complete", variant="secondary", interactive=False)] + audio
    # # Run the quick_text_to_speech function
    results = quick_text_to_speech(text, [voice] + additional_voices, preset, candidates, seed, cvvp)
    # # Enable the submit button
    yield [gr.update(value="Generate Audio", variant="primary", interactive=True)] + results

with gr.Blocks() as quickInterfaceOutputs:
    audio = [gr.Audio(visible=True)] + [gr.Audio(visible=False) for _ in range(MAXIMUM_CANDIDATE_ABSOLUTE - 1)]

with gr.Blocks() as quickInterface:
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                text = gr.Textbox(
                    lines=5, label="Text",
                    value="The expressiveness of autoregressive transformers is literally nuts! I absolutely adore them."
                )
                with gr.Row():
                    voice = gr.Dropdown(choices=["random"]+get_voice_list(), value="random", label="Voice")
                    preset = gr.Dropdown(choices=["ultra_fast", "fast", "standard", "high_quality"], value="fast", label="Preset")
                with gr.Accordion("Advanced Options", open=False):
                    additional_voices = gr.Dropdown(choices=get_voice_list(), value="random", multiselect=True, label="Additional Voices")
                    with gr.Row():
                        seed = gr.Number(value=None, label="seed")
                        cvvp = gr.Slider(minimum=0.0, maximum=1.0, value=0, label="cvvp", interactive=False)
                candidates = gr.Slider(minimum=1, maximum=settings["candidates_max_value"], value=1, step=1, label="Candidates")
                submit_button = gr.Button("Generate Audio", variant="primary")   

        with gr.Column(scale=1, elem_id="outputs"):
            quickInterfaceOutputs.render()

    submit_button.click(
        fn=submit_action, 
        inputs=[text, voice, additional_voices, preset, candidates, seed, cvvp], 
        outputs=[submit_button] + audio
    )
    
    quickInterface.load(None, [], [seed], js="() => {document.querySelector('input[type=number]').value = ''}")
