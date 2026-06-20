from transformers import Sam3Processor, Sam3Model
import torch
from PIL import Image
import requests
import numpy as np
import matplotlib
import os
dirname = os.path.dirname(__file__)



device = "cuda" if torch.cuda.is_available() else "cpu"
'Download model and cache'
#MODEL_DIR = os.path.join(dirname, "models/facebook/sam3")
#model = Sam3Model.from_pretrained("facebook/sam3", cache_dir=MODEL_DIR).to(device)
#processor = Sam3Processor.from_pretrained("facebook/sam3", cache_dir=MODEL_DIR0)
'Access model locally (will need to rename some files)'
MODEL_DIR = ""
if os.name == 'nt':
    MODEL_DIR = os.path.join(dirname, "models\\facebook\\sam3\\weights")
else:
    MODEL_DIR = os.path.join(dirname, "models/facebook/sam3/weights")

USE_HALF_PRECISION = True  # Set to True to load SAM3 in fp16 (~1.7 GB GPU, faster)

model = None
processor = None


def load_sam3():
    global model, processor
    if model is not None:
        return
    dtype = torch.float16 if USE_HALF_PRECISION else None
    model = Sam3Model.from_pretrained(MODEL_DIR, device_map=None, torch_dtype=dtype).to(device)
    processor = Sam3Processor.from_pretrained(MODEL_DIR)
    print(f"SAM3 model loaded on device: {next(model.parameters()).device}, dtype: {next(model.parameters()).dtype}")


def unload_sam3():
    global model, processor
    if model is None:
        return
    print("Unloading SAM3 model from GPU")
    model = None
    processor = None
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def overlay_masks(image, masks):
    image = image.convert("RGBA")
    masks = 255 * masks.cpu().numpy().astype(np.uint8)
    
    n_masks = masks.shape[0]
    cmap = matplotlib.colormaps.get_cmap("rainbow").resampled(n_masks)
    colors = [
        tuple(int(c * 255) for c in cmap(i)[:3])
        for i in range(n_masks)
    ]

    for mask, color in zip(masks, colors):
        mask = Image.fromarray(mask)
        overlay = Image.new("RGBA", image.size, color + (0,))
        alpha = mask.point(lambda v: int(v * 0.5))
        overlay.putalpha(alpha)
        image = Image.alpha_composite(image, overlay)
    return image

def cutout_masks(image, masks, boxes):
    image_array = np.array(image) 
    h, w = image_array.shape[:2] 
    centers = []
    cutouts = [] 

    for i, mask in enumerate(masks): 
        mask_array = mask.cpu().numpy() 
        box = boxes[i]
        center = [float((box[0] + box[2]) / 2), float((box[1] + box[3]) / 2)]
        centers.append(center)
        # Create RGBA for this specific object 
        rgba = np.zeros((h, w, 4), dtype=np.uint8) 
        rgba[:, :, :3] = image_array 
        rgba[:, :, 3] = (mask_array * 255).astype(np.uint8) 

        # Save with numbered filename 
        #individual_output = output_path.replace('.png', f'_{i+1}.png') 
        cutout = Image.fromarray(rgba, 'RGBA') 
        #cutout.show()
        #cutout.save(individual_output) 
        #print(f"Saved cutout {i+1} to: {individual_output}") 

        cutouts.append(cutout)
    return cutouts, centers

def position_of_object(imgDim, centers):
    positions = [0,0,0]
    for center in centers:
        x = center[0]
        relativeX = center[0] / imgDim[0]
        if relativeX < 0.33:
            positions[0] += 1
        elif relativeX > 0.66:
            positions[2] += 1
        else:
            positions[1] += 1
    return positions

def get_unique_prompts(object_boxes, confidence_threshold=0.4):
    prompts = []
    for box in object_boxes:
        if box["confidence"] >= confidence_threshold and box["object"] not in prompts:
            prompts.append(box["object"])
    return prompts

def SAM_masks_for_evaluation(object_boxes, image, confidence_threshold=0.4):
    load_sam3()
    image = Image.open(image).convert("RGB")
    predictions = []

    for prompt in get_unique_prompts(object_boxes, confidence_threshold):
        inputs = processor(images=image, text=prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model(**inputs)

        results = processor.post_process_instance_segmentation(
            outputs,
            threshold=0.5,
            mask_threshold=0.5,
            target_sizes=inputs.get("original_sizes").tolist()
        )[0]

        scores = results.get("scores")
        for i, mask in enumerate(results["masks"]):
            score = None
            if scores is not None:
                score = float(scores[i].detach().cpu().item())
            predictions.append(
                {
                    "object": prompt,
                    "mask": mask.detach().cpu().numpy().astype(bool),
                    "box": results["boxes"][i].detach().cpu().tolist(),
                    "score": score,
                }
            )

    return predictions

def SAM(object_boxes, image):
    load_sam3()
    #image_url = "http://images.cocodataset.org/val2017/000000077595.jpg"
    #image = Image.open(requests.get(image_url, stream=True).raw).convert("RGB")
    image = Image.open(image).convert("RGB")
    # Segment using text prompt
    prompts = []
    for box in object_boxes:
        if box["confidence"] >= 0.4 and box["object"] not in prompts: # 
            prompts.append(box["object"])
    full_mask = []
    objects = []
    for prompt in prompts:
        inputs = processor(images=image, text=prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model(**inputs)
        # Post-process results
        results = processor.post_process_instance_segmentation(
            outputs,
            threshold=0.5,
            mask_threshold=0.5,
            target_sizes=inputs.get("original_sizes").tolist()
        )[0]
        print(f"Found {len(results['masks'])} objects for prompt '{prompt}'")
        if len(results["masks"]) > 0:
            full_mask.append(results["masks"])
            mImage = overlay_masks(image, results["masks"])
            cImage, centers = cutout_masks(image, results["masks"], results["boxes"])
            imgDim = image.size
            positions = position_of_object(imgDim, centers)
            if positions[0] > 0:
                objects.append({
                    "object": prompt,
                    "position": "left",
                    "count": positions[0]
                })
            if positions[1] > 0:
                objects.append({
                    "object": prompt,
                    "position": "center",
                    "count": positions[1]
                })
            if positions[2] > 0:
                objects.append({
                    "object": prompt,
                    "position": "right",
                    "count": positions[2]
                })
    if len(full_mask) == 0:
        return image, objects
    maskedImg = overlay_masks(image, torch.cat(full_mask))
    return maskedImg, objects

# Results contain:
# - masks: Binary masks resized to original image size
# - boxes: Bounding boxes in absolute pixel coordinates (xyxy format)
# - scores: Confidence scores
