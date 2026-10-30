from __future__ import annotations

import json
from pathlib import Path

from src.commands import normalize_command


class GestureMapping:
    @staticmethod
    def _normalize_gesture_name(gesture: str | None) -> str:
        if gesture is None:
            return ""
        return "".join(ch.lower() for ch in gesture if not ch.isspace())

    def __init__(self, mapping: dict[str, str]):
        self.mapping = {
            self._normalize_gesture_name(gesture): normalize_command(command)
            for gesture, command in mapping.items()
        }

    @classmethod
    def from_file(cls, path: str | Path) -> "GestureMapping":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(data.get("mapping", {}))

    def command_for(self, gesture: str | None) -> str:
        if not gesture:
            return "STOP"
        return self.mapping.get(self._normalize_gesture_name(gesture), "STOP")
