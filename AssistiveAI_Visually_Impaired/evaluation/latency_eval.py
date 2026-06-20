import argparse
import csv
import os
import sys
import time


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def get_image_paths(images_dir, limit, image_files=None):
    image_paths = []
    if image_files is None:
        file_names = sorted(os.listdir(images_dir))
    else:
        file_names = image_files

    for file_name in file_names:
        lower_name = file_name.lower()
        if lower_name.endswith(".jpg") or lower_name.endswith(".jpeg") or lower_name.endswith(".png"):
            image_paths.append(os.path.join(images_dir, file_name))

    if image_files is None:
        return image_paths[:limit]

    return image_paths


def run_latency_evaluation(images_dir, model=None, class_names=None, limit=10, output="evaluation/results/latency_eval.csv", image_files=None):
    print("Loading models. This part is not timed.")
    from vision.object_detection import get_bounding_boxes_from_frame, initModel
    from vision.SAM3_seg import SAM, unload_sam3
    from vision.BLIP_scene import BLIP_caption, unload_blip
    from language.scene_description import construct_sentence

    if model is None:
        model, class_names = initModel()
    print("Models loaded.")

    image_paths = get_image_paths(images_dir, limit, image_files)
    if len(image_paths) == 0:
        print("No images found in " + images_dir)
        return

    os.makedirs(os.path.dirname(output), exist_ok=True)

    # Phase 1: YOLO + SAM3 for all images
    print("Phase 1: Timing YOLO + SAM3 on all images")
    sam_data = []
    for image_path in image_paths:
        file_name = os.path.basename(image_path)
        print("YOLO + SAM3: " + file_name)

        start = time.perf_counter()
        bounding_boxes = get_bounding_boxes_from_frame(image_path, model, class_names, debug=False)
        yolo_seconds = time.perf_counter() - start

        start = time.perf_counter()
        masked_image, objects = SAM(bounding_boxes, image_path)
        sam_seconds = time.perf_counter() - start

        sam_data.append({
            "file_name": file_name,
            "yolo_seconds": yolo_seconds,
            "sam_seconds": sam_seconds,
            "masked_image": masked_image,
            "objects": objects,
            "detections": len(bounding_boxes),
        })

    # Free SAM3 before loading BLIP
    print("Unloading SAM3 before BLIP phase")
    unload_sam3()

    # Phase 2: BLIP only for all images
    print("Phase 2: Timing BLIP on all images")
    rows = []
    for data in sam_data:
        file_name = data["file_name"]
        print("BLIP: " + file_name)
        objects = data["objects"]
        masked_image = data["masked_image"]

        start = time.perf_counter()
        caption = BLIP_caption(masked_image)
        blip_seconds = time.perf_counter() - start

        start = time.perf_counter()
        sentence = str(caption) + ". " + construct_sentence(objects)
        language_seconds = time.perf_counter() - start

        yolo_seconds = data["yolo_seconds"]
        sam_seconds = data["sam_seconds"]
        total_seconds = yolo_seconds + sam_seconds + blip_seconds + language_seconds

        rows.append(
            {
                "image": file_name,
                "yolo_seconds": yolo_seconds,
                "sam_seconds": sam_seconds,
                "blip_seconds": blip_seconds,
                "language_seconds": language_seconds,
                "total_seconds": total_seconds,
                "detections": data["detections"],
                "scene_objects": len(objects),
                "sentence": sentence,
            }
        )

    unload_blip()

    with open(output, "w", newline="") as csv_file:
        fieldnames = [
            "image",
            "yolo_seconds",
            "sam_seconds",
            "blip_seconds",
            "language_seconds",
            "total_seconds",
            "detections",
            "scene_objects",
            "sentence",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if len(rows) == 0:
        print("No timed rows saved. Try increasing --limit.")
        return

    mean_yolo = sum(row["yolo_seconds"] for row in rows) / len(rows)
    mean_sam = sum(row["sam_seconds"] for row in rows) / len(rows)
    mean_blip = sum(row["blip_seconds"] for row in rows) / len(rows)
    mean_language = sum(row["language_seconds"] for row in rows) / len(rows)
    mean_total = sum(row["total_seconds"] for row in rows) / len(rows)

    print("Average YOLO latency: " + str(mean_yolo) + " seconds")
    print("Average SAM3 latency: " + str(mean_sam) + " seconds")
    print("Average BLIP latency: " + str(mean_blip) + " seconds")
    print("Average language latency: " + str(mean_language) + " seconds")
    print("Average total latency: " + str(mean_total) + " seconds")
    print("Saved results to " + output)

    return {
        "mean_yolo": mean_yolo,
        "mean_sam": mean_sam,
        "mean_blip": mean_blip,
        "mean_language": mean_language,
        "mean_total": mean_total,
        "rows": len(rows),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", default="evaluation/results/latency_eval.csv")
    args = parser.parse_args()

    run_latency_evaluation(args.images_dir, limit=args.limit, output=args.output)


if __name__ == "__main__":
    main()
