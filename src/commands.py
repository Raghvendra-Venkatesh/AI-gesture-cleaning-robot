from __future__ import annotations

VALID_COMMANDS = {"FORWARD", "BACKWARD", "LEFT", "RIGHT", "STOP"}


def normalize_command(command: str | None) -> str:
    if command is None:
        return "STOP"
    normalized = command.strip().upper()
    if normalized not in VALID_COMMANDS:
        raise ValueError(f"Invalid robot command: {command}")
    return normalized


def is_valid_command(command: str | None) -> bool:
    try:
        normalize_command(command)
    except ValueError:
        return False
    return True
