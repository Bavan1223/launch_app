# FastAPI Relay Server

## Run locally

```bash
cd remote-control-app/server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## WebSocket endpoint

`ws://YOUR_SERVER_IP:8000/ws/{client_id}`

## Auth handshake

Each client must send a JSON message right after connecting:

```json
{
  "type": "laptop",
  "token": "1234"
}
```

The first token used by a `client_id` becomes the stored token for that device ID.
