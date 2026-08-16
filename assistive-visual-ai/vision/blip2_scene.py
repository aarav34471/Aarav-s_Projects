import os

import torch
from transformers import AutoProcessor, Blip2ForConditionalGeneration

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if torch.cuda.is_available() else torch.float32

print("BLIP2 using device: " + device)

MODEL_ID = os.environ.get("AVA_BLIP2_MODEL", "Salesforce/blip2-flan-t5-xl")
dirname = os.path.dirname(__file__)
MODEL_DIR = os.path.join(dirname, f"models/{MODEL_ID}")
processor = AutoProcessor.from_pretrained(MODEL_ID, cache_dir=MODEL_DIR)
model = Blip2ForConditionalGeneration.from_pretrained(MODEL_ID, torch_dtype=dtype, cache_dir=MODEL_DIR)
model.to(device)

def BLIP2_caption(frame):
    inputs = processor(frame, return_tensors="pt").to(device, dtype)
    generated_ids = model.generate(**inputs, max_new_tokens=20)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    return generated_text.capitalize()
