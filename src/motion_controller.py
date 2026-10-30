from __future__ import annotations

import time

from src.commands import normalize_command
from src.wifi_client import RobotWifiClient


class MotionController:
    def __init__(
        self,
        wifi_client: RobotWifiClient | None,
        dry_run: bool = True,
        heartbeat_seconds: float = 1.0,
    ):
        self.wifi_client = wifi_client
        self.dry_run = dry_run
        self.heartbeat_seconds = heartbeat_seconds
        self.current_command = "STOP"
        self.last_send_time = 0.0
        self.connected = dry_run
        self.last_error: str | None = None

    def send(self, command: str, force: bool = False) -> bool:
        command = normalize_command(command)
        now = time.monotonic()
        should_send = force or command != self.current_command or (now - self.last_send_time) >= self.heartbeat_seconds
        if not should_send:
            return self.connected

        self.current_command = command
        self.last_send_time = now

        if self.dry_run:
            self.connected = True
            self.last_error = None
            return True

        if self.wifi_client is None:
            self.connected = False
            self.last_error = "Wi-Fi client is not configured"
            return False

        ok = self.wifi_client.send_command(command)
        self.connected = ok
        self.last_error = self.wifi_client.last_error
        return ok

    def stop(self, force: bool = True) -> bool:
        return self.send("STOP", force=force)
