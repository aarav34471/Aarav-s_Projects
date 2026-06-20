from platform import processor
import os
import torch
from PIL import Image
from transformers import AutoProcessor, Blip2ForConditionalGeneration

device = "cuda" if torch.cuda.is_available() else "cpu"

print("BLIP2 using device: " + device)

MODEL_ID = "Salesforce/blip2-flan-t5-xl"
#Salesforce/blip2-opt-2.7b-coco
#Salesforce/blip2-opt-2.7b
dirname = os.path.dirname(__file__)
'Download model and cache'
MODEL_DIR = os.path.join(dirname, f"models/{MODEL_ID}")
processor = AutoProcessor.from_pretrained(MODEL_ID, cache_dir=MODEL_DIR)
model = Blip2ForConditionalGeneration.from_pretrained(MODEL_ID, torch_dtype=torch.float16, cache_dir=MODEL_DIR)
'Access model locally (will need to rename some files)'
#MODEL_DIR = os.path.join(dirname, f"models/{MODEL_ID}/weights")
#processor = AutoProcessor.from_pretrained(MODEL_DIR)
#model = Blip2ForConditionalGeneration.from_pretrained(MODEL_DIR, torch_dtype=torch.float16)
model.to(device)

def BLIP2_caption(frame):
    #img = Image.open(frame).convert('RGB')
    #print("Captioning image...")
    #print("Process")
    #prompt = "What can you see in this scene?"
    inputs = processor(frame, return_tensors="pt").to(device, torch.float16)
    #print("caption")
    generated_ids = model.generate(**inputs, max_new_tokens=20)
    #print("decode")
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    #print(generated_text.capitalize())
    return generated_text.capitalize()

#BLIP2_caption("D:/Documents/DL_CW/assistive_AI_for_visually_impaired_users/test_pics/bus.jpg") #a group of people standing next to a bus
#BLIP2_caption("D:/Documents/DL_CW/assistive_AI_for_visually_impaired_users/test_pics/crowd.jpg") #a crowd of people walking down a city street
#BLIP2_caption("D:/Documents/DL_CW/assistive_AI_for_visually_impaired_users/test_pics/sidewalk.png") #a colorful building with a bicycle
