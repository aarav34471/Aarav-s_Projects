from PIL import Image
import torch
from transformers import BlipProcessor, BlipForQuestionAnswering

device = "cuda" if torch.cuda.is_available() else "cpu"

model = None
processor = None


def load_blip():
    global model, processor
    if model is not None:
        return
    print("BLIP using device: " + device)
    processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
    model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base").to(device)


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
    #frame = Image.open(frame).convert('RGB')
    #print("Captioning image...")
    text = "a photo of"
    inputs = processor(frame, text, return_tensors="pt").to(device)
    #inputs = processor(frame, return_tensors="pt")
    #print("Generating caption...")
    out = model.generate(**inputs, max_new_tokens=50)
    #print("Generated caption:")
    generated_text = processor.decode(out[0], skip_special_tokens=True)
    #print(generated_text.capitalize())
    return generated_text.capitalize()

#BLIP_caption("D:/Documents/DL_CW/assistive_AI_for_visually_impaired_users/test_pics/bus.jpg") #People walking on sidewalk
#BLIP_caption("D:/Documents/DL_CW/assistive_AI_for_visually_impaired_users/test_pics/crowd.jpg") #busy street
#BLIP_caption("D:/Documents/DL_CW/assistive_AI_for_visually_impaired_users/test_pics/sidewalk.png") #outdoor cafe
