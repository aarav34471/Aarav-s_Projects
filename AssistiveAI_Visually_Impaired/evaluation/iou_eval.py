import argparse
import csv
import os
import sys

import numpy as np
from pycocotools.coco import COCO

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def mask_iou(pred_mask, gt_mask):
    pred_mask = pred_mask.astype(bool)
    gt_mask = gt_mask.astype(bool)

    if pred_mask.shape != gt_mask.shape:
        return 0.0

    intersection = np.logical_and(pred_mask, gt_mask).sum()
    union = np.logical_or(pred_mask, gt_mask).sum()

    if union == 0:
        return 0.0

    return intersection / union


def get_coco_masks(coco, image_id):
    masks = []
    annotation_ids = coco.getAnnIds(imgIds=image_id)
    annotations = coco.loadAnns(annotation_ids)

    for annotation in annotations:
        category = coco.loadCats(annotation["category_id"])[0]["name"]
        masks.append(
            {
                "object": category,
                "mask": coco.annToMask(annotation),
            }
        )

    return masks


def run_iou_evaluation(images_dir, annotations, model=None, class_names=None, limit=20, output="evaluation/results/iou_eval.csv", image_files=None):
    from vision.object_detection import get_bounding_boxes_from_frame, initModel
    from vision.SAM3_seg import SAM_masks_for_evaluation

    if model is None:
        model, class_names = initModel()

    coco = COCO(annotations)
    if image_files is None:
        image_ids = coco.getImgIds()[:limit]
    else:
        file_name_to_id = {}
        for image_id in coco.getImgIds():
            image_info = coco.loadImgs(image_id)[0]
            file_name_to_id[image_info["file_name"]] = image_id

        image_ids = []
        for image_file in image_files:
            if image_file in file_name_to_id:
                image_ids.append(file_name_to_id[image_file])

    os.makedirs(os.path.dirname(output), exist_ok=True)

    rows = []
    unmatched_predictions = 0
    for image_id in image_ids:
        image_info = coco.loadImgs(image_id)[0]
        image_path = os.path.join(images_dir, image_info["file_name"])
        print("Evaluating " + image_info["file_name"])

        bounding_boxes = get_bounding_boxes_from_frame(image_path, model, class_names, debug=False)
        sam_masks = SAM_masks_for_evaluation(bounding_boxes, image_path)
        coco_masks = get_coco_masks(coco, image_id)
        coco_objects = set(coco_mask["object"] for coco_mask in coco_masks)

        for sam_mask in sam_masks:
            if sam_mask["object"] not in coco_objects:
                unmatched_predictions += 1
                continue

            best_iou = 0.0

            for coco_mask in coco_masks:
                if sam_mask["object"] == coco_mask["object"]:
                    iou = mask_iou(sam_mask["mask"], coco_mask["mask"])
                    if iou > best_iou:
                        best_iou = iou

            rows.append(
                {
                    "image": image_info["file_name"],
                    "object": sam_mask["object"],
                    "best_iou": best_iou,
                }
            )

    with open(output, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["image", "object", "best_iou"])
        writer.writeheader()
        writer.writerows(rows)

    if len(rows) > 0:
        mean_iou = sum(row["best_iou"] for row in rows) / len(rows)
    else:
        mean_iou = 0.0

    print("Mean IoU: " + str(mean_iou))
    print("Unmatched predictions skipped: " + str(unmatched_predictions))
    print("Saved results to " + output)

    return {
        "mean_iou": mean_iou,
        "unmatched_predictions": unmatched_predictions,
        "rows": len(rows),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", required=True)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", default="evaluation/results/iou_eval.csv")
    args = parser.parse_args()

    run_iou_evaluation(args.images_dir, args.annotations, limit=args.limit, output=args.output)


if __name__ == "__main__":
    main()
