import json
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse


app = FastAPI(title="Remote Control Relay Server")

# device_id -> websocket connection
connected_clients: Dict[str, WebSocket] = {}
# device_id -> simple shared secret
device_tokens: Dict[str, str] = {}


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse(
        {
            "message": "Remote control relay server is running.",
            "connected_clients": list(connected_clients.keys()),
        }
    )


async def register_client(client_id: str, websocket: WebSocket) -> None:
    connected_clients[client_id] = websocket


def unregister_client(client_id: str) -> None:
    connected_clients.pop(client_id, None)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str) -> None:
    await websocket.accept()

    try:
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)

        token = auth_data.get("token")
        supplied_type = auth_data.get("type", "unknown")

        if not token:
            await websocket.send_text("ERROR|Missing token")
            await websocket.close()
            return

        existing_token = device_tokens.get(client_id)
        if existing_token and existing_token != token:
            await websocket.send_text("ERROR|Invalid token")
            await websocket.close()
            return

        device_tokens[client_id] = token
        await register_client(client_id, websocket)
        await websocket.send_text(f"REGISTERED|{client_id}|{supplied_type}")

        while True:
            raw_message = await websocket.receive_text()
            parts = raw_message.split("|", 1)

            if len(parts) != 2:
                await websocket.send_text("ERROR|Invalid message format")
                continue

            target_id, payload = parts
            target_socket = connected_clients.get(target_id)

            if not target_socket:
                await websocket.send_text(f"ERROR|Target {target_id} is not connected")
                continue

            target_token = device_tokens.get(target_id)
            if target_token != token:
                await websocket.send_text("ERROR|Token does not match target device")
                continue

            await target_socket.send_text(f"FROM|{client_id}|{payload}")
            await websocket.send_text(f"SENT|{target_id}|{payload}")

    except WebSocketDisconnect:
        unregister_client(client_id)
    except json.JSONDecodeError:
        await websocket.send_text("ERROR|Auth payload must be JSON")
        unregister_client(client_id)
        await websocket.close()
    except Exception as exc:
        unregister_client(client_id)
        try:
            await websocket.send_text(f"ERROR|{exc}")
            await websocket.close()
        except RuntimeError:
            pass
