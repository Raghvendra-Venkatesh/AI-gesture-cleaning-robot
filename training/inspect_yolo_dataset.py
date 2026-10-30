from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_names(data_yaml: Path) -> list[str]:
    text = data_yaml.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("names:"):
            value = stripped.split(":", 1)[1].strip()
            if value.startswith("["):
                return [item.strip().strip("'\"") for item in value.strip("[]").split(",")]
    raise ValueError(f"Could not parse names from {data_yaml}")


def inspect_split(root: Path, split: str) -> dict:
    image_dir = root / split / "images"
    label_dir = root / split / "labels"
    images = sorted(path for path in image_dir.glob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)
    labels = sorted(label_dir.glob("*.txt"))
    image_stems = {path.stem for path in images}
    label_stems = {path.stem for path in labels}
    class_counts = Counter()
    bad_lines = []
    empty_labels = 0

    for label_path in labels:
        lines = [line.strip() for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            empty_labels += 1
        for line in lines:
            parts = line.split()
            if len(parts) != 5:
                bad_lines.append({"file": str(label_path), "line": line})
                continue
            try:
                class_counts[int(parts[0])] += 1
                values = [float(value) for value in parts[1:]]
                if not all(0.0 <= value <= 1.0 for value in values):
                    bad_lines.append({"file": str(label_path), "line": line})
            except ValueError:
                bad_lines.append({"file": str(label_path), "line": line})

    return {
        "split": split,
        "images": len(images),
        "labels": len(labels),
        "missing_labels": sorted(image_stems - label_stems),
        "orphan_labels": sorted(label_stems - image_stems),
        "empty_label_files": empty_labels,
        "bad_label_lines": bad_lines,
        "class_counts": dict(sorted(class_counts.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a YOLO dataset.")
    parser.add_argument("--dataset", default="dataset")
    parser.add_argument("--output", default="reports/yolo_dataset_summary.json")
    args = parser.parse_args()

    root = Path(args.dataset)
    names = parse_names(root / "data.yaml")
    report = {
        "dataset": str(root),
        "classes": names,
        "splits": [inspect_split(root, split) for split in ("train", "valid", "test")],
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Classes: {names}")
    for split in report["splits"]:
        print(
            f"{split['split']}: images={split['images']} labels={split['labels']} "
            f"missing={len(split['missing_labels'])} bad={len(split['bad_label_lines'])}"
        )
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
