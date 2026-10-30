from __future__ import annotations

from pathlib import Path

import cv2


class YoloGestureRecognizer:
    def __init__(self, model_path: str | Path, confidence_threshold: float):
        from ultralytics import YOLO

        self.model = YOLO(str(model_path))
        self.confidence_threshold = confidence_threshold

    def predict_frame(self, frame) -> tuple[str | None, float, object]:
        results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
        if not results:
            return None, 0.0, None

        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return None, 0.0, result

        best_index = int(result.boxes.conf.argmax().item())
        confidence = float(result.boxes.conf[best_index].item())
        class_id = int(result.boxes.cls[best_index].item())
        label = str(result.names[class_id])
        return label, confidence, result

    def draw_detections(self, frame, result) -> None:
        if result is None or result.boxes is None:
            return
        names = result.names
        for box in result.boxes:
            confidence = float(box.conf.item())
            class_id = int(box.cls.item())
            label = f"{names[class_id]} {confidence:.2f}"
            x1, y1, x2, y2 = [int(value) for value in box.xyxy[0].tolist()]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 220, 0), 2)
            cv2.putText(frame, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 0), 2)
