from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

def summarize_split(split_dir: Path) -> dict:
    label_counts = Counter()
    file_counts = {}
    corrupt_files = []
    missing_landmarks = 0
    samples = 0
    max_labels = 0
    user_ids = defaultdict(int)

    for file_path in sorted(split_dir.glob("*.json")):
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            corrupt_files.append(str(file_path))
            continue

        file_counts[file_path.name] = len(data)
        samples += len(data)

        for sample in data.values():
            labels = sample.get("labels") or []
            landmarks = sample.get("landmarks") or []
            max_labels = max(max_labels, len(labels))
            label_counts.update(labels)
            if labels and not landmarks:
                missing_landmarks += 1
            user_id = sample.get("user_id")
            if user_id:
                user_ids[user_id] += 1

    return {
        "split": split_dir.name,
        "files": len(file_counts),
        "samples": samples,
        "file_counts": file_counts,
        "label_counts": dict(sorted(label_counts.items())),
        "max_labels_per_sample": max_labels,
        "missing_landmark_samples": missing_landmarks,
        "corrupt_files": corrupt_files,
        "unique_users": len(user_ids),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect gesture annotation JSON files.")
    parser.add_argument("--root", default=".", help="Project root containing ann_* folders.")
    parser.add_argument("--output", default="reports/dataset_summary.json")
    args = parser.parse_args()

    root = Path(args.root)
    splits = [path for path in [root / "ann_train_val", root / "ann_test", root / "ann_subsample"] if path.exists()]
    report = {"splits": [summarize_split(split) for split in splits]}

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    for split in report["splits"]:
        print(f"{split['split']}: {split['samples']} samples, {split['files']} files")
        print(f"  labels: {split['label_counts']}")
        print(f"  corrupt_files: {len(split['corrupt_files'])}")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
