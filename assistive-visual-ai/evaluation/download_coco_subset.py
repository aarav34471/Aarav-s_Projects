"""Download the exact COCO validation images referenced by the local annotations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlretrieve


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANNOTATIONS = PROJECT_ROOT / "coco_100/annotations/instances_val2017_100.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "coco_100/val2017"


def download_subset(annotations_path: Path, output_dir: Path) -> None:
    with annotations_path.open(encoding="utf-8") as source:
        annotations = json.load(source)

    output_dir.mkdir(parents=True, exist_ok=True)
    images = annotations.get("images", [])

    for index, image in enumerate(images, start=1):
        destination = output_dir / image["file_name"]
        if destination.exists():
            print(f"[{index}/{len(images)}] exists: {destination.name}")
            continue

        url = image.get("coco_url") or image.get("flickr_url")
        if not url:
            raise ValueError(f"No download URL for {image['file_name']}")

        print(f"[{index}/{len(images)}] downloading: {destination.name}")
        urlretrieve(url, destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    download_subset(args.annotations, args.output)


if __name__ == "__main__":
    main()
