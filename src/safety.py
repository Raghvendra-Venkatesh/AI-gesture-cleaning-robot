from __future__ import annotations

import time
from collections import deque


class PredictionSmoother:
    def __init__(self, consecutive_frames: int):
        self.consecutive_frames = max(1, consecutive_frames)
        self._history: deque[str] = deque(maxlen=self.consecutive_frames)

    def update(self, label: str | None) -> str | None:
        if label is None:
            self._history.clear()
            return None
        self._history.append(label)
        if len(self._history) < self.consecutive_frames:
            return None
        if len(set(self._history)) == 1:
            return self._history[-1]
        return None


class SafetyState:
    def __init__(self, no_detection_stop_seconds: float):
        self.no_detection_stop_seconds = no_detection_stop_seconds
        self.last_valid_prediction_time = 0.0

    def mark_valid_prediction(self) -> None:
        self.last_valid_prediction_time = time.monotonic()

    def should_stop_for_stale_prediction(self) -> bool:
        if self.last_valid_prediction_time == 0:
            return True
        return (time.monotonic() - self.last_valid_prediction_time) >= self.no_detection_stop_seconds
