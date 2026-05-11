from pathlib import Path

import customtkinter as ctk
from dotenv import load_dotenv, set_key
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class O2DashboardApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        
        self.title("Oxygen Monitoring System")
        self.geometry("650x400")

        self.frames = {}

        for PageClass in (MainMenuFrame, MonitorFrame, SettingsFrame):
            page_name = PageClass.__name__
            frame = PageClass(parent=self, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.check_initial_setup()
    
    def show_frame(self, page_name):
        """Brings the requested page to the top."""
        frame = self.frames[page_name]
        frame.tkraise()
    
    def check_initial_setup(self):
        """If essential .env variables are missing, for them to Settings."""
        env_path = Path(".env")
        load_dotenv(dotenv_path=env_path)
        sensor_ip = os.getenv("SENSOR_IP")
        print(sensor_ip)
        if not sensor_ip:
            self.show_frame("SettingsFrame")
        else:
            self.show_frame("MainMenuFrame")


class MainMenuFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        lbl_title = ctk.CTkLabel(self, text="Main Dashboard", font=("Arial", 24, "bold"))
        lbl_title.pack(pady=40)

        btn_monitor = ctk.CTkButton(self, text="Watch Monitor", command=lambda: controller.show_frame("MonitorFrame"))
        btn_monitor.pack(pady=10)

        btn_logger = ctk.CTkButton(self, text="Start Logging")
        btn_logger.pack(pady=10)

        # Reporter logic will go here

        btn_settings = ctk.CTkButton(self, text="Settings", command=lambda: controller.show_frame("SettingsFrame"))
        btn_settings.pack(pady=10)


class SettingsFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=1)
        
        lbl_title = ctk.CTkLabel(self, text="Settings & Configurations", font=("Arial", 24, "bold"))
        lbl_title.grid(row=0, column=1, pady=40, columnspan=2)

        lbl_sensor_ip = ctk.CTkLabel(self, text="Sensor IP ")
        lbl_sensor_ip.grid(row=1, column=1, pady=10)

        self.entry_ip = ctk.CTkEntry(self, placeholder_text="(e.g. 192.168.0.7)", width=250)
        self.entry_ip.grid(row=1, column=2, pady=10)

        lbl_sensor_port = ctk.CTkLabel(self, text="Sensor Port ")
        lbl_sensor_port.grid(row=2, column=1, pady=10)

        self.entry_port = ctk.CTkEntry(self, placeholder_text="(e.g. 502)", width=250)
        self.entry_port.grid(row=2, column=2, pady=10)

        lbl_device_id = ctk.CTkLabel(self, text="Device ID ")
        lbl_device_id.grid(row=3, column=1, pady=10)

        self.device_id = ctk.CTkEntry(self, placeholder_text="(e.g. 1)", width=250)
        self.device_id.grid(row=3, column=2, pady=10)

        btn_save = ctk.CTkButton(self, text="Save Preferences", command=self.save_settings)
        btn_save.grid(row=5, column=1, pady=10, columnspan=2)

    def save_settings(self):
        """Save settings for new session. Cannot save unless all fields are populated."""
        entry_ip = self.entry_ip.get()
        entry_port = self.entry_port.get()
        device_id = self.device_id.get()

        # TODO Enforce not empty fields
        if not entry_ip:
            return
    
        if not entry_port:
            return
        
        if not device_id:
            return

        env_path = Path(".env")
        set_key(dotenv_path=env_path, key_to_set="SENSOR_IP", value_to_set=entry_ip)
        set_key(dotenv_path=env_path, key_to_set="SENSOR_PORT", value_to_set=entry_port)
        set_key(dotenv_path=env_path, key_to_set="DEVICE_ID", value_to_set=device_id)
        self.controller.show_frame("MainMenuFrame")


class MonitorFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        lbl_title = ctk.CTkLabel(self, text="Live O2 Monitor Dashboard", font=("Arial", 24, "bold"))
        lbl_title.pack(pady=40)

        btn_back = ctk.CTkButton(self, text="Back to Menu", command=lambda: controller.show_frame("MainMenuFrame"))
        btn_back.pack(pady=10)

if __name__ == "__main__":
    app = O2DashboardApp()
    app.mainloop()
