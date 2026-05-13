import os
import random
import threading
import customtkinter as ctk
from pathlib import Path
from dotenv import load_dotenv, set_key
from tkdial import Meter
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.framer import FramerType
import asyncio
from queue import Queue

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
        self.geometry("700x500")

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

        # Update gauge theme
        self.controller.frames["MonitorFrame"].update_gauge_theme()
        

class MonitorFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.data_queue = Queue()
        self.start_async_bridge()
        self.check_mailbox()

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
        self.oxygen_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.oxygen_frame.grid(row=1, column=0, rowspan=2, sticky="nesw")

        current_theme = ctk.get_appearance_mode()

        if current_theme == "Dark":
            bg_color = "#2b2b2b"
            text_color = "white"
        else:
            bg_color = "#ebebeb"
            text_color = "black"
        
        # Oxygen Gauge Meter
        self.o2_gauge = Meter(
            self.oxygen_frame,
            radius=260,
            start=0,
            end=25,
            major_divisions=5,
            border_width=5,
            needle_color="#ff4c4c",
            fg=bg_color,
            bg=bg_color,
            text_color=text_color,
            scale_color=text_color,
        )
        self.o2_gauge.pack(expand=True)

        btn_back = ctk.CTkButton(self, text="Back to Menu", command=lambda: controller.show_frame("MainMenuFrame"))
        btn_back.grid(row=3, column=0, columnspan=2, pady=20)

        btn_test_data = ctk.CTkButton(self, text="Test Data", command=self.simulate_sensor_data)
        btn_test_data.grid(row=4, column=0, columnspan=2, pady=20)

    def update_gauge_theme(self):
        """Helper function to maintain theme responsiveness in the gauge."""
        current_val = self.o2_gauge.get()

        self.o2_gauge.destroy()

        current_theme = ctk.get_appearance_mode()

        if current_theme == "Dark":
            bg_color = "#2b2b2b"
            text_color = "white"
        else:
            bg_color = "#ebebeb"
            text_color = "black"
        
        self.o2_gauge = Meter(
            self.oxygen_frame,
            radius=260,
            start=0,
            end=25,
            major_divisions=5,
            border_width=5,
            needle_color="#ff4c4c",
            fg=bg_color,
            bg=bg_color,
            text_color=text_color,
            scale_color=text_color,
        )
        self.o2_gauge.pack(expand=True)

        # Weird voodoo stuff here to force theme
        self.o2_gauge.set(current_val)
    
    def update_dashboard(self, o2, temp, press):
        """Receives live data and updates the UI components"""
        self.o2_gauge.set(o2)
        self.lbl_temp_val.configure(text=f"{temp:.1f}")
        self.lbl_press_val.configure(text=f"{press:.0f}")
    
    def simulate_sensor_data(self):
        fake_o2 = random.uniform(18.0, 22.0)
        fake_temp = random.uniform(22.0, 26.0)
        fake_press = random.uniform(990.0, 1010.0)
        self.update_dashboard(fake_o2, fake_temp, fake_press)
    
    def start_async_bridge(self):
        """Creates the background thread that onws the asyncio loop."""
        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.async_modbus_worker())

        threading.Thread(target=run_loop, daemon=True).start()

    async def async_modbus_worker(self):
        """Runs in a separate thread. Never touches the UI directly."""
        env_path = Path(".env")
        load_dotenv(env_path)

        sensor_ip = os.getenv("SENSOR_IP")
        sensor_port = int(os.getenv("SENSOR_PORT"))
        device_id = int(os.getenv("DEVICE_ID"))

        #TODO Add alarm popups, if these verifications fail
        if not sensor_ip:
            return
        
        if not sensor_port:
            return
        
        if not device_id:
            return
    
        client = AsyncModbusTcpClient(host=sensor_ip, port=sensor_port, framer=FramerType.RTU, timeout=2)

        while True:
            try:
                if not client.connected:
                    await client.connect()

                if client.connected:
                    result = await client.read_holding_registers(address=10, count=6, device_id=device_id)

                if result.isError():
                    print("Error reading the data.")
                    client.close()
                else:
                    o2 = client.convert_from_registers(
                        result.registers[0:2],
                        client.DATATYPE.FLOAT32,
                        word_order="big",
                    )

                    temp = client.convert_from_registers(
                        result.registers[2:4],
                        client.DATATYPE.FLOAT32,
                        word_order="big",
                    )

                    press = client.convert_from_registers(
                        result.registers[4:6],
                        client.DATATYPE.FLOAT32,
                        word_order="big",
                    )

                    self.data_queue.put({
                        "o2": o2,
                        "temp": temp,
                        "press": press,
                    })
        
            except Exception as exc:
                print(f"Error: {exc}")
                client.close()
            
            await asyncio.sleep(1)

        
    def check_mailbox(self):
        """Runs on the main UI thread. Checks for data and updated the screen."""
        while not self.data_queue.empty():
            data = self.data_queue.get()
            self.update_dashboard(data["o2"], data["temp"], data["press"])
        
        self.after(1000, self.check_mailbox)

if __name__ == "__main__":
    app = O2DashboardApp()
    app.mainloop()
