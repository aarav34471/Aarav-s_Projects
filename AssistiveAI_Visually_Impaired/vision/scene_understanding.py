import cv2

PRIORITY = {
  'person':   3,   # always speak
  'car':      3,
  'bus':      3,
  'bicycle':  3,
  'dog':      2,
  'cat':      2,
  'chair':    1,   # mention if prominent
  'table':    1,
  'tv':       1,
  # unknown class -> default 1
}

def filter_objects(objects, filter_threshold):
    filterable = sorted(objects, key=lambda x: x["priority"], reverse=True)
    filtered = []
    for obj in filterable[:filter_threshold]:
        filtered.append({"object": obj["object"],
            "position": obj["position"],
            "count": None
            })
    return filtered
    
    



def place_object_in_scene(object_boxes, frame, debug, filter_threshold):
    #get dimensions of images for positions
    img = cv2.imread(frame)
    imgW = img.shape[1]
    imgH = img.shape[0]
    scene = []
    objects = []
    for box in object_boxes:
        if box["confidence"] < 0.4:
            break
        x, y, w, h = box["box"]
        relativeX = x / imgW
        if relativeX < 0.33:
            position = "left"
        elif relativeX > 0.66:
            position = "right"
        else:
            position = "center"
        priority = PRIORITY.get(box["object"], 1)
        if priority == 3:
            scene.append({
                "object": box["object"],
                "position": position,
                "count": None
            })
        else:
            objects.append({
                "object": box["object"],
                "position": position,
                "count": None,
                "priority": priority
            })
    if len(objects) > 0:
        scene.extend(filter_objects(objects, filter_threshold))
    if (debug):
        for item in scene:
            print(str(item) + "\n")
    return scene