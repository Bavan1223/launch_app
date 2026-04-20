# Remote Control App

This project contains a beginner-friendly MVP for controlling a laptop from an Android phone over the internet using a cloud relay server.

## Architecture

1. Android app sends commands to the FastAPI relay server.
2. FastAPI server keeps track of connected devices by `client_id`.
3. Laptop client receives commands and executes them with `pyautogui`.

## Folder structure

```text
remote-control-app/
  server/
  laptop-client/
  android-app/
```

## Message protocol

The mobile app sends messages to the server in this format:

```text
target_id|COMMAND
```

Examples:

```text
laptop123|NEXT_SLIDE
laptop123|PREVIOUS_SLIDE
laptop123|CLICK
laptop123|KEY_PRESS:enter
laptop123|MOUSE_MOVE:100,200
```

The server relays commands to the target device as:

```text
FROM|sender_id|COMMAND
```

## End-to-end setup

### 1. Start the FastAPI server

```bash
cd remote-control-app/server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start the laptop app

Run the desktop receiver app:

```bash
cd remote-control-app/laptop-client
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python desktop_app.py
```

Then in the laptop app:

- keep or generate a device ID
- enter the same token/PIN used by the phone
- set the relay server URL, for example `ws://192.168.1.25:8000`
- click `Connect`

### 3. Run the Android app

1. Open `remote-control-app/android-app` in Android Studio
2. Let Gradle sync
3. Update `serverUrl` in `MainActivity.kt`
4. Keep the `token` in the Android app the same as the laptop app
5. Build and run on your emulator or Android device
6. Enter the laptop device ID shown by the laptop app, for example `laptop-A1B2C3`
7. Tap buttons to send commands

## Deploying over the internet

For real internet control:

- Deploy the FastAPI server to a cloud VM or platform that supports WebSockets
- Use a public IP or domain name
- Prefer `wss://` instead of `ws://` in production
- Open the server port in your firewall

## Basic authentication

- Both laptop and mobile send a JSON auth message right after connecting
- The laptop app saves its `device_id`, `token`, and `server_base_url` in `laptop-client/config.json`
- The first token used for a device ID is stored on the server
- Future connections for that same ID must use the same token

This is intentionally simple for an MVP. For production, use stronger authentication and encryption.

## Optional next improvements

- Add QR pairing for device ID + server URL
- Add heartbeat/ping handling
- Add reconnect UI on Android
- Add rate limiting and command validation
- Add TLS and signed tokens
