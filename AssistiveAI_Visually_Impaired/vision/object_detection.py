#pip install ultralytics

import torch
from ultralytics import YOLO

device = "cuda" if torch.cuda.is_available() else "cpu"

print("YOLO using device: " + device)

def initModel():
    model = YOLO("yolo26n.pt")
    class_names = model.names
    return model, class_names

def get_bounding_boxes_from_frame(frame, model, class_names, debug):
    results = model(frame, verbose=False, device=device)
    bounding_boxes = []

    for result in results:
        if (debug):
            result.show()
        for box in result.boxes:
            bounding_boxes.append(
                {
                    "object" : class_names[int(box.cls)],
                    "box" : box.xywh.tolist()[0],
                    "confidence" : box.conf.tolist()[0]
                }
            )

    if (debug):
        print("==========(" + frame + ")==========\n")    
        for box in bounding_boxes:
            print(str(box) + "\n")

    return bounding_boxes
