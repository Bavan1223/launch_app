import asyncio
import json
import sys
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Tuple

import pyautogui
import websockets


DEFAULT_SERVER_BASE_URL = "ws://127.0.0.1:8000"
DEFAULT_TOKEN = "1234"


pyautogui.FAILSAFE = True


def get_app_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


CONFIG_PATH = get_app_directory() / "config.json"


@dataclass
class ClientSettings:
    device_id: str
    token: str
    server_base_url: str


def generate_device_id() -> str:
    short_id = uuid.uuid4().hex[:6].upper()
    return f"laptop-{short_id}"


def load_settings() -> ClientSettings:
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return ClientSettings(
            device_id=data.get("device_id", generate_device_id()),
            token=data.get("token", DEFAULT_TOKEN),
            server_base_url=data.get("server_base_url", DEFAULT_SERVER_BASE_URL),
        )

    settings = ClientSettings(
        device_id=generate_device_id(),
        token=DEFAULT_TOKEN,
        server_base_url=DEFAULT_SERVER_BASE_URL,
    )
    save_settings(settings)
    return settings


def save_settings(settings: ClientSettings) -> None:
    payload = {
        "device_id": settings.device_id,
        "token": settings.token,
        "server_base_url": settings.server_base_url,
    }
    CONFIG_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_mouse_payload(payload: str) -> Optional[Tuple[int, int]]:
    try:
        raw_x, raw_y = payload.split(",")
        return int(raw_x), int(raw_y)
    except ValueError:
        return None


def execute_command(command: str) -> None:
    if command in {"NEXT", "NEXT_SLIDE"}:
        pyautogui.press("right")
    elif command in {"PREVIOUS", "PREVIOUS_SLIDE"}:
        pyautogui.press("left")
    elif command == "CLICK":
        pyautogui.click()
    elif command.startswith("MOUSE_MOVE:") or command.startswith("MOUSE:"):
        cleaned_command = command.replace("MOUSE_MOVE:", "", 1).replace("MOUSE:", "", 1)
        coords = parse_mouse_payload(cleaned_command)
        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0)
    elif command.startswith("KEY_PRESS:") or command.startswith("KEY:"):
        key_name = command.replace("KEY_PRESS:", "", 1).replace("KEY:", "", 1).strip()
        if key_name:
            pyautogui.press(key_name)


async def listen_forever(
    settings: ClientSettings,
    status_callback: Optional[Callable[[str], None]] = None,
    stop_event: Optional[threading.Event] = None,
) -> None:
    while True:
        if stop_event and stop_event.is_set():
            if status_callback:
                status_callback("Disconnected")
            return

        try:
            server_url = f"{settings.server_base_url}/ws/{settings.device_id}"
            if status_callback:
                status_callback(f"Connecting to {server_url}")

            async with websockets.connect(server_url) as websocket:
                auth_payload = {
                    "type": "laptop",
                    "token": settings.token,
                }
                await websocket.send(json.dumps(auth_payload))

                welcome = await websocket.recv()
                if status_callback:
                    status_callback(f"Connected: {welcome}")

                while True:
                    if stop_event and stop_event.is_set():
                        await websocket.close()
                        if status_callback:
                            status_callback("Disconnected")
                        return

                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1)
                    except asyncio.TimeoutError:
                        continue

                    if status_callback:
                        status_callback(f"Received: {message}")

                    parts = message.split("|", 2)
                    if len(parts) != 3 or parts[0] != "FROM":
                        continue

                    _, sender_id, command = parts
                    if status_callback:
                        status_callback(f"Executing {command} from {sender_id}")
                    execute_command(command)

        except Exception as exc:
            if status_callback:
                status_callback(f"Reconnect in 3s: {exc}")

            if stop_event and stop_event.wait(3):
                if status_callback:
                    status_callback("Disconnected")
                return


def run_terminal_client() -> None:
    settings = load_settings()
    asyncio.run(listen_forever(settings, print))
