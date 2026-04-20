# Laptop Client

You now have two ways to run the laptop receiver:

- `desktop_app.py` for a simple desktop UI
- `client.py` for the original terminal version

## Recommended: desktop app

```bash
cd remote-control-app/laptop-client
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python desktop_app.py
```

### Desktop app flow

1. Open the app
2. Keep the generated device ID or click `Generate`
3. Enter your token/PIN
4. Enter the relay server URL, for example:
   `ws://192.168.1.25:8000`
5. Click `Save Settings`
6. Click `Connect`
7. Enter the shown device ID in the Android app

The app saves its settings in:

`remote-control-app/laptop-client/config.json`

## Terminal version

```bash
cd remote-control-app/laptop-client
python client.py
```

The terminal version reads the same saved `config.json` file.

## Notes

- The laptop must stay connected to the FastAPI server.
- Use the same token in both the Android app and the laptop app.
- `pyautogui.FAILSAFE = True` means moving the mouse to the top-left corner can stop unsafe mouse loops.
- Later, you can package `desktop_app.py` as an `.exe` with PyInstaller if you want a sharable laptop installer.
