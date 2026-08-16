import os

import torch
from transformers import BlipProcessor, BlipForQuestionAnswering

device = "cuda" if torch.cuda.is_available() else "cpu"

model = None
processor = None
MODEL_ID = os.environ.get("AVA_BLIP_MODEL", "Salesforce/blip-vqa-base")


def load_blip():
    global model, processor
    if model is not None:
        return
    print("BLIP using device: " + device)
    processor = BlipProcessor.from_pretrained(MODEL_ID)
    model = BlipForQuestionAnswering.from_pretrained(MODEL_ID).to(device)


def unload_blip():
    global model, processor
    if model is None:
        return
    print("Unloading BLIP model from GPU")
    model = None
    processor = None
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def BLIP_caption(frame):
    load_blip()
    text = "a photo of"
    inputs = processor(frame, text, return_tensors="pt").to(device)
    out = model.generate(**inputs, max_new_tokens=50)
    generated_text = processor.decode(out[0], skip_special_tokens=True)
    return generated_text.capitalize()
