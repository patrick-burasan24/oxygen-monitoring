import os
import customtkinter as ctk
from pathlib import Path
from dotenv import load_dotenv, set_key
from tkdial import Meter

ctk.set_default_color_theme("dark-blue")


def valid_parameter(parameter: str):
    return parameter and parameter != "" and parameter.strip() !=  ""


class O2DashboardApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        env_path = Path(".env")
        load_dotenv(env_path)

        theme_preference = os.getenv("THEME_PREFERENCE", "System")
        ctk.set_appearance_mode(theme_preference)

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
        """If essential .env variables are missing, forward them to Settings."""
        env_path = Path(".env")
        load_dotenv(dotenv_path=env_path)
        
        sensor_ip = os.getenv("SENSOR_IP")
        sensor_port = os.getenv("SENSOR_PORT")
        device_id = os.getenv("DEVICE_ID")

        if not valid_parameter(sensor_ip) or not valid_parameter(sensor_port) or not valid_parameter(device_id):
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

        btn_exit = ctk.CTkButton(self, text="Exit", command=lambda: parent.quit())
        btn_exit.pack(pady=10)


class SettingsFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        env_path = Path(".env")
        load_dotenv(env_path)

        sensor_ip = os.getenv("SENSOR_IP")
        sensor_port = os.getenv("SENSOR_PORT")
        device_id = os.getenv("DEVICE_ID")
        theme_preference = os.getenv("THEME_PREFERENCE", "System")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=1)
        
        # Sensor connection details
        lbl_title = ctk.CTkLabel(self, text="Settings & Configurations", font=("Arial", 24, "bold"))
        lbl_title.grid(row=0, column=1, pady=40, columnspan=2)

        lbl_sensor_ip = ctk.CTkLabel(self, text="Sensor IP ")
        lbl_sensor_ip.grid(row=1, column=1, pady=10)

        self.entry_ip = ctk.CTkEntry(self, placeholder_text="(e.g. 192.168.0.7)", width=350)
        if sensor_ip:
            self.entry_ip.insert(0, sensor_ip)
        self.entry_ip.grid(row=1, column=2, pady=10)

        lbl_sensor_port = ctk.CTkLabel(self, text="Sensor Port ")
        lbl_sensor_port.grid(row=2, column=1, pady=10)

        self.entry_port = ctk.CTkEntry(self, placeholder_text="(e.g. 502)", width=350)
        if sensor_port:
            self.entry_port.insert(0, sensor_port)
        self.entry_port.grid(row=2, column=2, pady=10)

        lbl_device_id = ctk.CTkLabel(self, text="Device ID ")
        lbl_device_id.grid(row=3, column=1, pady=10)

        self.device_id = ctk.CTkEntry(self, placeholder_text="(e.g. 1)", width=350)
        if device_id:
            self.device_id.insert(0, device_id)
        self.device_id.grid(row=3, column=2, pady=10)

        # Theme toggler (Light, Dark, System)
        segmented_button = ctk.CTkSegmentedButton(self, values=["Light", "Dark", "System"], command=self.change_theme)
        segmented_button.grid(row=4, column=1, pady=10, columnspan=2)
        segmented_button.set(theme_preference)

        # Action buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=5, column=1, pady=10, columnspan=2)

        btn_save = ctk.CTkButton(button_frame, text="Save Preferences", command=self.save_settings)
        btn_save.grid(row=5, column=1, padx=10, sticky="e")

        btn_cancel = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel)
        btn_cancel.grid(row=5, column=2, padx=10, sticky="w")

        # Custom button bindings
        self.entry_ip.bind("<FocusIn>", self.reset_ip_error)
        self.entry_ip.bind("<Return>", self.save_settings)

        self.entry_port.bind("<FocusIn>", self.reset_pord_error)
        self.entry_port.bind("<Return>", self.save_settings)

        self.device_id.bind("<FocusIn>", self.reset_id_error)
        self.device_id.bind("<Return>", self.save_settings)


    def save_settings(self, event=None):
        """Save settings for new session. Cannot save unless all fields are populated."""
        entry_ip = self.entry_ip.get()
        entry_port = self.entry_port.get()
        device_id = self.device_id.get()

        has_errors = False

        if not valid_parameter(entry_ip):
            self.entry_ip.delete(0, "end")
            self.focus_set()
            self.entry_ip.configure(placeholder_text="MISSING: Enter Sensor IP (e.g. 192.168.0.7)", placeholder_text_color="#ff4c4c")
            has_errors = True
    
        if not valid_parameter(entry_port):
            self.entry_port.delete(0, "end")
            self.focus_set()
            self.entry_port.configure(placeholder_text="MISSING: Enter Sensor Port (e.g. 502)", placeholder_text_color="#ff4c4c")
            has_errors = True
        
        if not valid_parameter(device_id):
            self.device_id.delete(0, "end")
            self.focus_set()
            self.device_id.configure(placeholder_text="MISSING: Enter Device ID (e.g. 1)", placeholder_text_color="#ff4c4c")
            has_errors = True
        
        if has_errors:
            return
        
        env_path = Path(".env")
        set_key(dotenv_path=env_path, key_to_set="SENSOR_IP", value_to_set=entry_ip)
        set_key(dotenv_path=env_path, key_to_set="SENSOR_PORT", value_to_set=entry_port)
        set_key(dotenv_path=env_path, key_to_set="DEVICE_ID", value_to_set=device_id)
        self.controller.show_frame("MainMenuFrame")
    
    def cancel(self):
        """Returns user to the MainMenuFrame."""
        self.controller.show_frame("MainMenuFrame")

    def reset_ip_error(self, event):
        """Resets the entry_ip placeholder_text property after an error."""
        self.entry_ip.configure(placeholder_text="(e.g. 192.168.0.7)", placeholder_text_color="gray")
        self.entry_ip._deactivate_placeholder()

    def reset_pord_error(self, event):
        """Resets the entry_port placeholder_text property after an error."""
        self.entry_port.configure(placeholder_text="(e.g. 502)", placeholder_text_color="gray")
        self.entry_port._deactivate_placeholder()

    def reset_id_error(self, event):
        """Resets the device_id placeholder_text property after an error."""
        self.device_id.configure(placeholder_text="(e.g. 1)", placeholder_text_color="gray")
        self.device_id._deactivate_placeholder()
    
    def change_theme(self, new_theme):
        """Modifies the .env key to reflect the new theme preference."""
        if not valid_parameter(new_theme):
            return

        curtain_frame = ctk.CTkFrame(self)
        curtain_frame.place(relwidth=1, relheight=1)
        self.update_idletasks()
        ctk.set_appearance_mode(new_theme)
        self.after(200, curtain_frame.destroy)

        env_path = Path(".env")
        set_key(dotenv_path=env_path, key_to_set="THEME_PREFERENCE", value_to_set=new_theme)
        

class MonitorFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1, uniform="group1")
        self.rowconfigure(2, weight=1, uniform="group1")
        self.rowconfigure(3, weight=0)

        lbl_title = ctk.CTkLabel(self, text="Live O2 Monitor Dashboard", font=("Arial", 24, "bold"))
        lbl_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Temperature frame
        temp_frame = ctk.CTkFrame(self, corner_radius=15)
        temp_frame.grid(row=1, column=1, sticky="nesw", padx=20, ipady=20)
        
        # Temperature labels
        lbl_temp_title = ctk.CTkLabel(temp_frame, text="TEMPERATURE", font=("Arial", 14, "bold"))
        lbl_temp_title.pack(pady=(20, 0), side="top")

        self.lbl_temp_val = ctk.CTkLabel(temp_frame, text="--.-", font=("Arial", 48, "bold"))
        self.lbl_temp_val.pack(expand=True) # expand=True centers the value vertically
        
        lbl_temp_unit = ctk.CTkLabel(temp_frame, text="˚C", font=("Arial", 20))
        lbl_temp_unit.pack(pady=(0, 20), side="bottom")

        # Pressure frame
        press_frame = ctk.CTkFrame(self, corner_radius=15)
        press_frame.grid(row=2, column=1, sticky="nesw", padx=20, ipady=20)

        # Pressure labels
        lbl_press_title = ctk.CTkLabel(press_frame, text="PRESSURE", font=("Arial", 14, "bold"))
        lbl_press_title.pack(pady=(20, 0), side="top")

        self.lbl_press_val = ctk.CTkLabel(press_frame, text="----", font=("Arial", 48, "bold"))
        self.lbl_press_val.pack(expand=True) # expand=True centers the value vertically
        
        lbl_press_unit = ctk.CTkLabel(press_frame, text="mbar", font=("Arial", 20))
        lbl_press_unit.pack(pady=(0, 20), side="bottom")

        # Oxygen Gauge Meter Wrapper
        oxygen_frame = ctk.CTkFrame(self)
        oxygen_frame.grid(row=1, column=0, rowspan=2, sticky="nesw")
        
        # Oxygen Gauge Meter
        self.o2_gauge = Meter(
            oxygen_frame,
            radius=260,
            start=0,
            end=25,
            major_divisions=5,
            border_width=0,
            fg="#f0f0f0",
            text_color="black",
            needle_color="#ff4c4c",
            scale_color="black",
        )
        self.o2_gauge.pack(expand=True)

        btn_back = ctk.CTkButton(self, text="Back to Menu", command=lambda: controller.show_frame("MainMenuFrame"))
        btn_back.grid(row=3, column=0, columnspan=2, pady=20)

if __name__ == "__main__":
    app = O2DashboardApp()
    app.mainloop()
