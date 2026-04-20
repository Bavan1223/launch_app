import asyncio
import threading
import tkinter as tk
from tkinter import ttk

from core import (
    ClientSettings,
    generate_device_id,
    listen_forever,
    load_settings,
    save_settings,
)


class LaptopReceiverApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Remote Control Receiver")
        self.root.geometry("520x360")
        self.root.resizable(False, False)

        self.settings = load_settings()
        self.worker_thread: threading.Thread | None = None
        self.stop_event: threading.Event | None = None
        self.is_connected = False

        self.device_id_var = tk.StringVar(value=self.settings.device_id)
        self.token_var = tk.StringVar(value=self.settings.token)
        self.server_url_var = tk.StringVar(value=self.settings.server_base_url)
        self.status_var = tk.StringVar(value="Ready")

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=20)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Laptop Receiver", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="Pair this laptop with your Android app using the device ID below.",
        ).pack(anchor="w", pady=(4, 18))

        form = ttk.Frame(outer)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Device ID").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.device_id_var).grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(form, text="Generate", command=self.regenerate_device_id).grid(row=0, column=2, padx=(10, 0))

        ttk.Label(form, text="PIN / Token").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.token_var).grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(form, text="Server URL").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.server_url_var).grid(row=2, column=1, columnspan=2, sticky="ew", pady=6)

        button_row = ttk.Frame(outer)
        button_row.pack(fill="x", pady=(18, 10))

        self.connect_button = ttk.Button(button_row, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side="left")

        ttk.Button(button_row, text="Save Settings", command=self.save_current_settings).pack(side="left", padx=(10, 0))

        ttk.Label(outer, text="Status").pack(anchor="w", pady=(8, 4))
        self.status_label = ttk.Label(
            outer,
            textvariable=self.status_var,
            relief="solid",
            padding=10,
            anchor="w",
        )
        self.status_label.pack(fill="x")

        tips = (
            "Tips:\n"
            "- Use the same token in the Android app.\n"
            "- For same-Wi-Fi testing, enter the laptop IP in the Android server URL.\n"
            "- Keep this window open while receiving commands."
        )
        ttk.Label(outer, text=tips, justify="left").pack(anchor="w", pady=(16, 0))

    def regenerate_device_id(self) -> None:
        self.device_id_var.set(generate_device_id())
        self.status_var.set("Generated a new device ID. Save before sharing it.")

    def save_current_settings(self) -> ClientSettings:
        settings = ClientSettings(
            device_id=self.device_id_var.get().strip(),
            token=self.token_var.get().strip(),
            server_base_url=self.server_url_var.get().strip().rstrip("/"),
        )
        save_settings(settings)
        self.settings = settings
        self.status_var.set(f"Saved settings for {settings.device_id}")
        return settings

    def toggle_connection(self) -> None:
        if self.is_connected:
            self.disconnect()
            return

        settings = self.save_current_settings()
        if not settings.device_id or not settings.token or not settings.server_base_url:
            self.status_var.set("Device ID, token, and server URL are required.")
            return

        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(
            target=self.run_background_client,
            args=(settings, self.stop_event),
            daemon=True,
        )
        self.worker_thread.start()
        self.is_connected = True
        self.connect_button.configure(text="Disconnect")

    def disconnect(self) -> None:
        if self.stop_event:
            self.stop_event.set()
        self.is_connected = False
        self.connect_button.configure(text="Connect")
        self.status_var.set("Disconnecting...")

    def run_background_client(self, settings: ClientSettings, stop_event: threading.Event) -> None:
        asyncio.run(
            listen_forever(
                settings=settings,
                status_callback=self.threadsafe_status_update,
                stop_event=stop_event,
            )
        )
        self.root.after(0, self.mark_disconnected)

    def threadsafe_status_update(self, message: str) -> None:
        self.root.after(0, lambda: self.status_var.set(message))

    def mark_disconnected(self) -> None:
        self.is_connected = False
        self.connect_button.configure(text="Connect")

    def on_close(self) -> None:
        if self.stop_event:
            self.stop_event.set()
        self.root.destroy()


if __name__ == "__main__":
    app_root = tk.Tk()
    app = LaptopReceiverApp(app_root)
    app_root.mainloop()
