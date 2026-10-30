from __future__ import annotations

import argparse
from pathlib import Path

from training.dataset_report import main as report_main


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the provided annotation dataset.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root)
    expected = ["ann_train_val", "ann_test"]
    missing = [name for name in expected if not (root / name).exists()]
    if missing:
        raise SystemExit(f"Missing required dataset folders: {', '.join(missing)}")
    report_main()


if __name__ == "__main__":
    main()
