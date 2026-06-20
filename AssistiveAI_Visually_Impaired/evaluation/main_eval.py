import argparse
import csv
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def write_summary(summary, output):
    os.makedirs(os.path.dirname(output), exist_ok=True)

    with open(output, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["evaluation", "metric", "value"])
        writer.writeheader()

        for evaluation_name in summary:
            result = summary[evaluation_name]
            if result is None:
                continue

            for metric in result:
                writer.writerow(
                    {
                        "evaluation": evaluation_name,
                        "metric": metric,
                        "value": result[metric],
                    }
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", required=True)
    parser.add_argument("--instances", required=True)
    parser.add_argument("--captions", required=True)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output-dir", default="evaluation/results")
    args = parser.parse_args()

    from evaluation.iou_eval import run_iou_evaluation
    from evaluation.description_eval import run_description_evaluation
    from evaluation.latency_eval import run_latency_evaluation
    from evaluation.shared_images import get_image_file_names
    from vision.object_detection import initModel

    os.makedirs(args.output_dir, exist_ok=True)
    image_files = get_image_file_names(args.instances, args.limit)

    iou_output = os.path.join(args.output_dir, "iou_eval.csv")
    description_output = os.path.join(args.output_dir, "description_eval.csv")
    latency_output = os.path.join(args.output_dir, "latency_eval.csv")
    summary_output = os.path.join(args.output_dir, "main_eval_summary.csv")

    from vision.SAM3_seg import unload_sam3
    from vision.BLIP_scene import unload_blip

    print("Loading YOLO model (shared across all evaluations)")
    model, class_names = initModel()

    print("Running IoU evaluation")
    iou_summary = run_iou_evaluation(
        args.images_dir,
        args.instances,
        model,
        class_names,
        args.limit,
        iou_output,
        image_files,
    )
    unload_sam3()

    print("Running description evaluation")
    description_summary = run_description_evaluation(
        args.images_dir,
        args.captions,
        model,
        class_names,
        args.limit,
        description_output,
        image_files,
    )
    unload_sam3()

    print("Running latency evaluation")
    latency_summary = run_latency_evaluation(
        args.images_dir,
        model,
        class_names,
        args.limit,
        latency_output,
        image_files,
    )
    unload_sam3()
    unload_blip()

    summary = {
        "iou": iou_summary,
        "description": description_summary,
        "latency": latency_summary,
    }
    write_summary(summary, summary_output)

    print("Saved IoU results to " + iou_output)
    print("Saved description results to " + description_output)
    print("Saved latency results to " + latency_output)
    print("Saved summary to " + summary_output)


if __name__ == "__main__":
    main()
