from __future__ import annotations

from src.commands import normalize_command


class RobotWifiClient:
    def __init__(self, base_url: str, timeout_seconds: float = 0.4):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.last_error: str | None = None

    def send_command(self, command: str) -> bool:
        command = normalize_command(command)
        try:
            import requests

            response = requests.get(
                f"{self.base_url}/command",
                params={"cmd": command},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            ok = payload.get("ok") is True and payload.get("command") == command
            self.last_error = None if ok else f"Unexpected response: {payload}"
            return ok
        except Exception as exc:
            self.last_error = str(exc)
            return False

    def status(self) -> dict:
        try:
            import requests

            response = requests.get(f"{self.base_url}/status", timeout=self.timeout_seconds)
            response.raise_for_status()
            self.last_error = None
            return response.json()
        except Exception as exc:
            self.last_error = str(exc)
            return {"ok": False, "error": self.last_error}
