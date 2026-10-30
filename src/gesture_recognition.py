from __future__ import annotations

from pathlib import Path

import cv2
import joblib
import numpy as np

from training.dataset import normalize_landmarks


class GestureRecognizer:
    def __init__(self, model_path: str | Path, confidence_threshold: float):
        artifact = joblib.load(model_path)
        self.model = artifact["model"]
        self.encoder = artifact["label_encoder"]
        self.classes = artifact["classes"]
        self.confidence_threshold = confidence_threshold
        self._hands = None
        self._mp_hands = None
        self._mp_drawing = None

    def _ensure_mediapipe(self):
        if self._hands is None:
            import mediapipe as mp

            self._mp_hands = mp.solutions.hands
            self._mp_drawing = mp.solutions.drawing_utils
            self._hands = self._mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.5,
            )

    def predict_features(self, features: np.ndarray) -> tuple[str, float]:
        features = features.reshape(1, -1)
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(features)[0]
            index = int(np.argmax(probabilities))
            confidence = float(probabilities[index])
        else:
            prediction = int(self.model.predict(features)[0])
            index = prediction
            confidence = 1.0
        label = str(self.encoder.inverse_transform([index])[0])
        return label, confidence

    def predict_frame(self, frame) -> tuple[str | None, float, object]:
        self._ensure_mediapipe()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self._hands.process(rgb)
        if not result.multi_hand_landmarks:
            return None, 0.0, result

        hand_landmarks = result.multi_hand_landmarks[0]
        coords = [[point.x, point.y] for point in hand_landmarks.landmark]
        features = normalize_landmarks(coords)
        label, confidence = self.predict_features(features)
        if confidence < self.confidence_threshold:
            return None, confidence, result
        return label, confidence, result

    def draw_landmarks(self, frame, result) -> None:
        if not result or not result.multi_hand_landmarks:
            return
        for hand_landmarks in result.multi_hand_landmarks:
            self._mp_drawing.draw_landmarks(frame, hand_landmarks, self._mp_hands.HAND_CONNECTIONS)
