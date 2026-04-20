REMOTE CONTROL APP - SHARE PACKAGE

Files in this folder:
- app-debug.apk
- RemoteControlReceiver.exe

How to use:

1. On the friend's laptop:
   - Run RemoteControlReceiver.exe
   - Set Server URL to your running relay server, for example:
     ws://YOUR_SERVER_IP:8000
   - Enter the PIN/Token
   - Keep or generate the device ID
   - Click Connect

2. On the friend's Android phone:
   - Install app-debug.apk
   - Open the app
   - Enter the same device ID shown on the laptop app
   - Make sure the Android app is configured to use:
     ws://YOUR_SERVER_IP:8000/ws/android-controller
   - Use the same PIN/Token as the laptop app
   - Tap Connect

Important:
- The FastAPI server must be running and reachable.
- The token must match on both Android and laptop.
- For same-Wi-Fi use, replace YOUR_SERVER_IP with the laptop/server local IP.
- For internet use, deploy the FastAPI server to a public server and use its public IP or domain.
