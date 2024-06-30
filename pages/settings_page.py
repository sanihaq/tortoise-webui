import gradio as gr
from helpers.settings import settings, save_settings, settingsToDefault, DEFAULT_SAMPLE_RATE, MAXIMUM_CANDIDATE_ABSOLUTE, copySettings
from helpers.utils import reload_tts_model
from pages.quick_gen import candidates

def updatemaxCandidates(value):
    settings["candidates_max_value"] = value
    save_settings()
    return gr.update(value=1, maximum=value)

def updatemaxProduceDebugState(value):
    settings["produce_debug_state"] = value
    save_settings()

def updateTTSModel(deepspeed, kv_cache, half):
    settings["use_deepspeed"] = deepspeed
    settings["kv_cache"] = kv_cache
    settings["half_precision"] = half
    reload_tts_model(settings)
    save_settings()
    return gr.update(interactive=False)

def restoreToDefaultSettings():
    s = settingsToDefault()
    save_settings()
    reload_tts_model(s)
    return [
        gr.update(value=s["candidates_max_value"]),
        gr.update(value=s["candidates_max_value"], maximum=settings["candidates_max_value"]),
        gr.update(value=s["produce_debug_state"]),
        gr.update(value=s["use_deepspeed"]),
        gr.update(value=s["kv_cache"]),
        gr.update(value=s["half_precision"]),
    ]

def settingsInterfaceOnLoad():
    s = copySettings()
    return [
        gr.update(value=s["candidates_max_value"]),
        gr.update(value=1, maximum=settings["candidates_max_value"]),
        gr.update(value=s["produce_debug_state"]),
        gr.update(value=s["use_deepspeed"]),
        gr.update(value=s["kv_cache"]),
        gr.update(value=s["half_precision"]),
    ]

with gr.Blocks() as settingsInterface:
    with gr.Column(scale=1):
        with gr.Group():
            with gr.Row():
                maxCandidates = gr.Number(value=settings["candidates_max_value"], minimum=1, maximum=MAXIMUM_CANDIDATE_ABSOLUTE, label="Maximum Candidates")
                defaultSampleRate = gr.Number(value=DEFAULT_SAMPLE_RATE, interactive=False, label="Default Sample Rate")
            with gr.Row():
                produceDebugState = gr.Checkbox(value=settings["produce_debug_state"], label="Produce Debug State")
                useDeepspeed = gr.Checkbox(value=settings["use_deepspeed"], label="Use Deepspeed")
                kvCache = gr.Checkbox(value=settings["kv_cache"], label="KV Cache")
                half = gr.Checkbox(value=settings["half_precision"], label="Half Precision")

        with gr.Row():
            restore_btn = gr.Button(value="Restore to Default Settings", variant="stop")
            save_btn = gr.Button(value="Reload TTS Model and Save", variant="primary", interactive=False)

            useDeepspeed.change(fn=lambda _: gr.update(interactive=True), inputs=useDeepspeed, outputs=save_btn)
            kvCache.change(fn=lambda _: gr.update(interactive=True), inputs=kvCache, outputs=save_btn)
            half.change(fn=lambda _: gr.update(interactive=True), inputs=half, outputs=save_btn)

            maxCandidates.change(fn=updatemaxCandidates, inputs=maxCandidates, outputs=candidates)
            produceDebugState.change(fn=updatemaxProduceDebugState, inputs=produceDebugState, outputs=None)
            save_btn.click(fn=updateTTSModel, inputs=[useDeepspeed, kvCache, half], outputs=save_btn)
            restore_btn.click(fn=restoreToDefaultSettings, outputs=[maxCandidates, candidates, produceDebugState, useDeepspeed, kvCache, half])

    gr.Blocks.load(settingsInterface, settingsInterfaceOnLoad, outputs=[maxCandidates, candidates, produceDebugState, useDeepspeed, kvCache, half])
