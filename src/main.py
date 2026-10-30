from __future__ import annotations

import json
import time
from pathlib import Path

import cv2

from src.camera import open_camera
from src.gesture_mapping import GestureMapping
from src.motion_controller import MotionController
from src.safety import PredictionSmoother, SafetyState
from src.wifi_client import RobotWifiClient
from src.yolo_gesture_recognition import YoloGestureRecognizer


ROOT = Path(__file__).resolve().parents[1]


def load_settings(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def draw_status(frame, lines: list[str]) -> None:
    y = 28
    for line in lines:
        cv2.putText(frame, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 240, 20), 2, cv2.LINE_AA)
        y += 30


def main() -> None:
    settings = load_settings(ROOT / "config" / "settings.json")
    mapping = GestureMapping.from_file(ROOT / "config" / "gesture_mapping.json")
    if settings.get("model_type") != "yolo":
        raise RuntimeError("This runtime is configured for YOLO. Set model_type to 'yolo'.")
    recognizer = YoloGestureRecognizer(ROOT / settings["model_path"], settings["confidence_threshold"])
    smoother = PredictionSmoother(settings["consecutive_frames"])
    safety = SafetyState(settings["no_detection_stop_seconds"])

    wifi = None if settings["dry_run"] else RobotWifiClient(
        settings["robot_base_url"],
        timeout_seconds=settings["request_timeout_seconds"],
    )
    controller = MotionController(wifi, dry_run=settings["dry_run"], heartbeat_seconds=settings["heartbeat_seconds"])
    if not settings["dry_run"] and not controller.stop(force=True):
        raise RuntimeError(
            f"Cannot reach the ESP32 at {settings['robot_base_url']}: {controller.last_error}. "
            "Connect this laptop to the robot's Wi-Fi and make sure the ESP32 is powered on."
        )

    camera = open_camera(settings["camera_index"], settings["image_width"], settings["image_height"])
    window = settings.get("display_window", "Gesture Cleaning Robot")

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                controller.stop(force=True)
                raise RuntimeError("Camera frame capture failed")

            label, confidence, detection_result = recognizer.predict_frame(frame)
            recognizer.draw_detections(frame, detection_result)

            stable_label = smoother.update(label)
            if stable_label:
                safety.mark_valid_prediction()
                command = mapping.command_for(stable_label)
                controller.send(command)
            elif safety.should_stop_for_stale_prediction():
                controller.stop(force=False)

            connection = "DRY RUN" if settings["dry_run"] else ("OK" if controller.connected else "ERROR")
            draw_status(
                frame,
                [
                    f"Detected: {label or 'none'}",
                    f"Confidence: {confidence:.2f}",
                    f"Control gesture: {stable_label or 'waiting for stable gesture'}",
                    f"Command: {controller.current_command}",
                    f"Wi-Fi: {connection}",
                    *([f"Wi-Fi error: {controller.last_error}"] if controller.last_error else []),
                    "ESC or Q: emergency stop",
                ],
            )
            cv2.imshow(window, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q"), ord("Q")):
                controller.stop(force=True)
                time.sleep(0.1)
                break
    finally:
        controller.stop(force=True)
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
