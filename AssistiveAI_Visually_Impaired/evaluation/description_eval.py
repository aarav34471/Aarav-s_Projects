import argparse
import csv
import json
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CONNECTOR_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "the",
    "there",
    "to",
    "with",
}


def load_captions(captions_path):
    with open(captions_path) as file:
        data = json.load(file)

    image_names = {}
    for image in data["images"]:
        image_names[image["id"]] = image["file_name"]

    captions = {}
    for annotation in data["annotations"]:
        image_id = annotation["image_id"]
        if image_id not in captions:
            captions[image_id] = []
        captions[image_id].append(annotation["caption"])

    return image_names, captions


def clean_caption(caption):
    caption = caption.lower()

    for symbol in [".", ",", "!", "?", ";", ":", '"', "'", "(", ")"]:
        caption = caption.replace(symbol, " ")

    words = []
    for word in caption.split():
        if word not in CONNECTOR_WORDS:
            words.append(word)

    return " ".join(words)


def object_text_from_sam(objects):
    object_names = []

    for object_info in objects:
        object_name = object_info["object"]
        if object_name not in object_names:
            object_names.append(object_name)

    if len(object_names) == 0:
        return "nothing"

    return " ".join(object_names)


def best_bertscore(scorer, system_object_text, cleaned_captions):
    candidates = []
    for _ in cleaned_captions:
        candidates.append(system_object_text)

    precision, recall, f1 = scorer.score(candidates, cleaned_captions)
    best_index = int(f1.argmax())

    return {
        "precision": float(precision[best_index]),
        "recall": float(recall[best_index]),
        "f1": float(f1[best_index]),
        "caption": cleaned_captions[best_index],
    }


def run_description_evaluation(images_dir, captions, model=None, class_names=None, limit=10, output="evaluation/results/description_eval.csv", image_files=None):
    import torch
    from bert_score import BERTScorer
    from vision.object_detection import get_bounding_boxes_from_frame, initModel
    from vision.SAM3_seg import SAM, unload_sam3

    image_names, captions_by_image = load_captions(captions)

    if model is None:
        model, class_names = initModel()

    os.makedirs(os.path.dirname(output), exist_ok=True)

    if image_files is None:
        image_ids = list(captions_by_image.keys())[:limit]
    else:
        file_name_to_id = {}
        for image_id in image_names:
            file_name_to_id[image_names[image_id]] = image_id

        image_ids = []
        for image_file in image_files:
            if image_file in file_name_to_id and file_name_to_id[image_file] in captions_by_image:
                image_ids.append(file_name_to_id[image_file])

    # Phase 1: YOLO + SAM3 — extract object texts from all images
    print("Phase 1: Running YOLO + SAM3 on all images")
    image_data = []
    for image_id in image_ids:
        file_name = image_names[image_id]
        image_path = os.path.join(images_dir, file_name)
        image_captions = captions_by_image[image_id]

        print("SAM3: " + file_name)

        bounding_boxes = get_bounding_boxes_from_frame(image_path, model, class_names, debug=False)
        _masked_image, objects = SAM(bounding_boxes, image_path)
        system_object_text = object_text_from_sam(objects)
        cleaned_captions = [clean_caption(c) for c in image_captions]

        image_data.append({
            "file_name": file_name,
            "system_object_text": system_object_text,
            "cleaned_captions": cleaned_captions,
            "all_captions": image_captions,
        })

    # Free SAM3 before loading BERT
    print("Unloading SAM3 before BERTScore phase")
    unload_sam3()

    # Phase 2: BERTScore only — score the collected texts
    print("Phase 2: Running BERTScore")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("BERTScore using device: " + device)
    scorer = BERTScorer(lang="en", rescale_with_baseline=True, device=device)

    rows = []
    for data in image_data:
        print("BERTScore: " + data["file_name"])
        score = best_bertscore(scorer, data["system_object_text"], data["cleaned_captions"])

        rows.append(
            {
                "image": data["file_name"],
                "system_object_text": data["system_object_text"],
                "best_cleaned_coco_caption": score["caption"],
                "bertscore_precision": score["precision"],
                "bertscore_recall": score["recall"],
                "bertscore_f1": score["f1"],
                "cleaned_coco_captions": " | ".join(data["cleaned_captions"]),
                "all_coco_captions": " | ".join(data["all_captions"]),
            }
        )

    del scorer
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print("BERTScore unloaded")

    with open(output, "w", newline="") as csv_file:
        fieldnames = [
            "image",
            "system_object_text",
            "best_cleaned_coco_caption",
            "bertscore_precision",
            "bertscore_recall",
            "bertscore_f1",
            "cleaned_coco_captions",
            "all_coco_captions",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if len(rows) > 0:
        mean_f1 = sum(row["bertscore_f1"] for row in rows) / len(rows)
    else:
        mean_f1 = 0.0

    print("Average BERTScore F1: " + str(mean_f1))
    print("Saved results to " + output)

    if len(rows) > 0:
        mean_precision = sum(row["bertscore_precision"] for row in rows) / len(rows)
        mean_recall = sum(row["bertscore_recall"] for row in rows) / len(rows)
    else:
        mean_precision = 0.0
        mean_recall = 0.0

    return {
        "mean_bertscore_precision": mean_precision,
        "mean_bertscore_recall": mean_recall,
        "mean_bertscore_f1": mean_f1,
        "rows": len(rows),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", required=True)
    parser.add_argument("--captions", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", default="evaluation/results/description_eval.csv")
    args = parser.parse_args()

    run_description_evaluation(args.images_dir, args.captions, limit=args.limit, output=args.output)


if __name__ == "__main__":
    main()
