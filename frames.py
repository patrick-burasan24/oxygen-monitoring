import random
from tkinter import filedialog
import customtkinter as ctk
from tkdial import Meter
import threading
import asyncio
from queue import Queue
from config import get_env, set_env, valid_parameter
from sensor_service import SensorService
from database import add_reading
import datetime as dt
import calendar
from reporter import generate_daily_report
from database import summary


def _create_gauge_meter(frame, fg, bg, text_color, scale_text):
    return Meter(
        frame,
        radius=260,
        start=0,
        end=25,
        major_divisions=5,
        border_width=5,
        needle_color="#ff4c4c",
        fg=fg,
        bg=bg,
        text_color=text_color,
        scale_color=scale_text,
        scroll=False,
    )


class MainMenuFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        lbl_title = ctk.CTkLabel(
            self, text="Main Dashboard", font=("Arial", 24, "bold"))
        lbl_title.pack(pady=40)

        btn_monitor = ctk.CTkButton(
            self, text="Watch Monitor", command=lambda: controller.show_frame("MonitorFrame"))
        btn_monitor.pack(pady=10)

        self.btn_logger = ctk.CTkButton(
            self, text="Start Logging", command=self.toggle_logging)
        self.btn_logger.pack(pady=10)

        self.btn_reporter = ctk.CTkButton(
            self, text="Generate Report", command=lambda: controller.show_frame("ReporterFrame"))
        self.btn_reporter.pack(pady=10)

        btn_settings = ctk.CTkButton(
            self, text="Settings", command=lambda: controller.show_frame("SettingsFrame"))
        btn_settings.pack(pady=10)

        btn_exit = ctk.CTkButton(
            self, text="Exit", command=lambda: parent.quit())
        btn_exit.pack(pady=10)

    def toggle_logging(self):
        """Flips the self.controller.is_logging value."""
        if not self.controller.is_logging:
            sensor_ip = get_env("SENSOR_IP")
            sensor_port = get_env("SENSOR_PORT")
            device_id = get_env("DEVICE_ID")

            if not valid_parameter(sensor_ip) or not valid_parameter(sensor_port) or not valid_parameter(device_id):
                self.controller.show_popup_error()
                return

        self.controller.is_logging = not self.controller.is_logging
        if self.controller.is_logging:
            self.btn_logger.configure(
                text="Stop Logging",
                fg_color="#ff4c4c",
                hover_color="#cc0000"
            )
        else:
            self.btn_logger.configure(
                text="Start Logging",
                fg_color=["#3B8ED0", "#1F6AA5"],
                hover_color=["#36719F", "#144870"]
            )


class SettingsFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        theme_preference = get_env("THEME_PREFERENCE", "System")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=1)

        # Sensor connection details
        lbl_title = ctk.CTkLabel(
            self, text="Settings & Configurations", font=("Arial", 24, "bold"))
        lbl_title.grid(row=0, column=1, pady=40, columnspan=2)

        lbl_sensor_ip = ctk.CTkLabel(self, text="Sensor IP ")
        lbl_sensor_ip.grid(row=1, column=1, pady=10)

        self.entry_ip = ctk.CTkEntry(
            self, placeholder_text="(e.g. 192.168.0.7)", width=350)
        self.entry_ip.insert(0, get_env("SENSOR_IP"))
        self.entry_ip.grid(row=1, column=2, pady=10)

        lbl_sensor_port = ctk.CTkLabel(self, text="Sensor Port ")
        lbl_sensor_port.grid(row=2, column=1, pady=10)

        self.entry_port = ctk.CTkEntry(
            self, placeholder_text="(e.g. 502)", width=350)
        self.entry_port.insert(0, get_env("SENSOR_PORT"))
        self.entry_port.grid(row=2, column=2, pady=10)

        lbl_device_id = ctk.CTkLabel(self, text="Device ID ")
        lbl_device_id.grid(row=3, column=1, pady=10)

        self.device_id = ctk.CTkEntry(
            self, placeholder_text="(e.g. 1)", width=350)
        self.device_id.insert(0, get_env("DEVICE_ID"))
        self.device_id.grid(row=3, column=2, pady=10)

        self.lbl_o2_min_threshold = ctk.CTkLabel(
            self, text="Min O2 Treshold: 19.5%")
        self.lbl_o2_min_threshold.grid(row=4, column=1, pady=10)

        self.o2_min_threshold = ctk.CTkSlider(
            self,
            from_=15.0,
            to=21.0,
            command=self.update_threshold_label
        )
        self.o2_min_threshold.grid(row=4, column=2, pady=10)

        saved_threshold = float(get_env("O2_MIN_TRESHOLD", "19.5"))
        self.o2_min_threshold.set(saved_threshold)
        self.lbl_o2_min_threshold.configure(
            text=f"Min O2 Treshold: {saved_threshold:.1f}%")

        lbl_register_start_address = ctk.CTkLabel(
            self, text="Register Start Address ")
        lbl_register_start_address.grid(row=5, column=1, pady=10)

        self.register_start_address = ctk.CTkEntry(
            self, placeholder_text="(e.g. 0)", width=350)
        self.register_start_address.insert(
            0, get_env("REGISTER_START_ADDRESS", "10"))
        self.register_start_address.grid(row=5, column=2, pady=10)

        lbl_register_count = ctk.CTkLabel(self, text="Register Count ")
        lbl_register_count.grid(row=6, column=1, pady=10)

        self.register_count = ctk.CTkEntry(
            self, placeholder_text="(e.g. 6)", width=350)
        self.register_count.insert(0, get_env("REGISTER_COUNT", "6"))
        self.register_count.grid(row=6, column=2, pady=10)

        # Theme toggler (Light, Dark, System)
        segmented_button = ctk.CTkSegmentedButton(
            self, values=["Light", "Dark", "System"], command=self.change_theme)
        segmented_button.grid(row=7, column=1, pady=10, columnspan=2)
        segmented_button.set(theme_preference)

        # Action buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=8, column=1, pady=10, columnspan=2)

        btn_save = ctk.CTkButton(
            button_frame, text="Save Preferences", command=self.save_settings)
        btn_save.grid(row=8, column=1, padx=10, sticky="e")

        btn_cancel = ctk.CTkButton(
            button_frame, text="Cancel", command=self.cancel)
        btn_cancel.grid(row=8, column=2, padx=10, sticky="w")

        # Custom button bindings
        self.entry_ip.bind("<FocusIn>", self.reset_ip_error)
        self.entry_ip.bind("<Return>", self.save_settings)

        self.entry_port.bind("<FocusIn>", self.reset_port_error)
        self.entry_port.bind("<Return>", self.save_settings)

        self.device_id.bind("<FocusIn>", self.reset_id_error)
        self.device_id.bind("<Return>", self.save_settings)

        self.register_start_address.bind(
            "<FocusIn>", self.reset_register_start_address_error)
        self.register_start_address.bind("<Return>", self.save_settings)

        self.register_count.bind("<FocusIn>", self.reset_register_count_error)
        self.register_count.bind("<Return>", self.save_settings)

    def save_settings(self, event=None):
        """Save settings for new session. Cannot save unless all fields are populated."""
        entry_ip = self.entry_ip.get()
        entry_port = self.entry_port.get()
        device_id = self.device_id.get()
        o2_min_threshold = self.o2_min_threshold.get()
        register_start_address = self.register_start_address.get()
        register_count = self.register_count.get()

        has_errors = False

        if not valid_parameter(entry_ip):
            self.entry_ip.delete(0, "end")
            self.focus_set()
            self.entry_ip.configure(
                placeholder_text="MISSING: Enter Sensor IP (e.g. 192.168.0.7)", placeholder_text_color="#ff4c4c")
            has_errors = True

        if not valid_parameter(entry_port):
            self.entry_port.delete(0, "end")
            self.focus_set()
            self.entry_port.configure(placeholder_text="MISSING: Enter Sensor Port (e.g. 502)",
                                      placeholder_text_color="#ff4c4c")
            has_errors = True

        if not valid_parameter(device_id):
            self.device_id.delete(0, "end")
            self.focus_set()
            self.device_id.configure(placeholder_text="MISSING: Enter Device ID (e.g. 1)",
                                     placeholder_text_color="#ff4c4c")
            has_errors = True

        if not valid_parameter(register_start_address):
            self.register_start_address.delete(0, "end")
            self.focus_set()
            self.register_start_address.configure(placeholder_text="MISSING: Enter Register Start Address (e.g. 0)",
                                                  placeholder_text_color="#ff4c4c")
            has_errors = True

        if not valid_parameter(register_count):
            self.register_count.delete(0, "end")
            self.focus_set()
            self.register_count.configure(
                placeholder_text="MISSING: Enter Register Count (e.g. 6)", placeholder_text_color="#ff4c4c")
            has_errors = True

        if has_errors:
            return

        set_env("SENSOR_IP", entry_ip)
        set_env("SENSOR_PORT", entry_port)
        set_env("DEVICE_ID", device_id)
        set_env("O2_MIN_TRESHOLD", f"{o2_min_threshold}")
        set_env("REGISTER_START_ADDRESS", register_start_address)
        set_env("REGISTER_COUNT", register_count)
        self.controller.show_frame("MainMenuFrame")

    def cancel(self):
        """Returns user to the MainMenuFrame."""
        self.controller.show_frame("MainMenuFrame")

    def reset_ip_error(self, event):
        """Resets the entry_ip placeholder_text property after an error."""
        self.entry_ip.configure(
            placeholder_text="(e.g. 192.168.0.7)", placeholder_text_color="gray")
        self.entry_ip._deactivate_placeholder()

    def reset_port_error(self, event):
        """Resets the entry_port placeholder_text property after an error."""
        self.entry_port.configure(
            placeholder_text="(e.g. 502)", placeholder_text_color="gray")
        self.entry_port._deactivate_placeholder()

    def reset_id_error(self, event):
        """Resets the device_id placeholder_text property after an error."""
        self.device_id.configure(
            placeholder_text="(e.g. 1)", placeholder_text_color="gray")
        self.device_id._deactivate_placeholder()

    def reset_register_start_address_error(self, event):
        """Resets the register_start_address placeholder_text property after an error."""
        self.register_start_address.configure(
            placeholder_text="(e.g. 0)", placeholder_text_color="gray")
        self.register_start_address._deactivate_placeholder()

    def reset_register_count_error(self, event):
        """Resets the register_count placeholder_text property after an error."""
        self.register_count.configure(
            placeholder_text="(e.g. 6)", placeholder_text_color="gray")
        self.register_count._deactivate_placeholder()

    def change_theme(self, new_theme):
        """Modifies the .env key to reflect the new theme preference."""
        if not valid_parameter(new_theme):
            return

        curtain_frame = ctk.CTkFrame(self)
        curtain_frame.place(relwidth=1, relheight=1)
        self.update_idletasks()
        ctk.set_appearance_mode(new_theme)
        self.after(200, curtain_frame.destroy)

        set_env("THEME_PREFERENCE", new_theme)

        # Update gauge theme
        self.controller.frames["MonitorFrame"].update_gauge_theme()

    def update_threshold_label(self, value):
        """Updates the threshold label."""
        self.lbl_o2_min_threshold.configure(
            text=f"Min O2 Treshold: {value:.1f}%")


class MonitorFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.data_queue = Queue()
        self.sensor_service = SensorService(self.data_queue)
        self.start_async_bridge()
        self.check_mailbox()

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1, uniform="group1")
        self.rowconfigure(2, weight=1, uniform="group1")
        self.rowconfigure(3, weight=0)

        lbl_title = ctk.CTkLabel(
            self, text="Live O2 Monitor Dashboard", font=("Arial", 24, "bold"))
        lbl_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Temperature frame
        temp_frame = ctk.CTkFrame(self, corner_radius=15)
        temp_frame.grid(row=1, column=1, sticky="nesw", padx=20, ipady=20)

        # Temperature labels
        lbl_temp_title = ctk.CTkLabel(
            temp_frame, text="TEMPERATURE", font=("Arial", 14, "bold"))
        lbl_temp_title.pack(pady=(20, 0), side="top")

        self.lbl_temp_val = ctk.CTkLabel(
            temp_frame, text="--.-", font=("Arial", 48, "bold"))
        # expand=True centers the value vertically
        self.lbl_temp_val.pack(expand=True)

        lbl_temp_unit = ctk.CTkLabel(temp_frame, text="˚C", font=("Arial", 20))
        lbl_temp_unit.pack(pady=(0, 20), side="bottom")

        # Pressure frame
        press_frame = ctk.CTkFrame(self, corner_radius=15)
        press_frame.grid(row=2, column=1, sticky="nesw", padx=20, ipady=20)

        # Pressure labels
        lbl_press_title = ctk.CTkLabel(
            press_frame, text="PRESSURE", font=("Arial", 14, "bold"))
        lbl_press_title.pack(pady=(20, 0), side="top")

        self.lbl_press_val = ctk.CTkLabel(
            press_frame, text="----", font=("Arial", 48, "bold"))
        # expand=True centers the value vertically
        self.lbl_press_val.pack(expand=True)

        lbl_press_unit = ctk.CTkLabel(
            press_frame, text="mbar", font=("Arial", 20))
        lbl_press_unit.pack(pady=(0, 20), side="bottom")

        # Oxygen Gauge Meter Wrapper
        self.oxygen_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.oxygen_frame.grid(row=1, column=0, rowspan=2, sticky="nesw")

        current_theme = ctk.get_appearance_mode()

        if current_theme == "Dark":
            bg_color = "#212121"
            text_color = "white"
        else:
            bg_color = "#e5e5e5"
            text_color = "black"

        # Oxygen Gauge Meter
        self.o2_gauge = _create_gauge_meter(
            self.oxygen_frame,
            bg_color,
            bg_color,
            text_color,
            text_color
        )
        self.o2_gauge.pack(expand=True)

        btn_back = ctk.CTkButton(
            self, text="Back to Menu", command=lambda: controller.show_frame("MainMenuFrame"))
        btn_back.grid(row=3, column=0, columnspan=2, pady=20)

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

        self.o2_gauge = _create_gauge_meter(
            self.oxygen_frame,
            bg_color,
            bg_color,
            text_color,
            text_color
        )
        self.o2_gauge.pack(expand=True)

        # Weird voodoo stuff here to force theme
        self.o2_gauge.set(current_val)

    def update_dashboard(self, o2, temp, press):
        """Receives live data and updates the UI components"""
        if isinstance(o2, list):
            o2 = o2[0] if len(o2) > 0 else 0.0
        if isinstance(temp, list):
            temp = temp[0] if len(temp) > 0 else 0.0
        if isinstance(press, list):
            press = press[0] if len(press) > 0 else 0.0

        self.o2_gauge.set(float(o2))
        self.lbl_temp_val.configure(text=f"{float(temp):.1f}")
        self.lbl_press_val.configure(text=f"{float(press):.0f}")

    def start_async_bridge(self):
        """Creates the background thread that onws the asyncio loop."""
        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.sensor_service.poll_sensor())

        threading.Thread(target=run_loop, daemon=True).start()

    def check_mailbox(self):
        """Runs on the main UI thread. Checks for data and updated the screen."""
        try:
            while not self.data_queue.empty():
                data = self.data_queue.get()

                if "status" in data and data["status"] == "error":
                    err_msg = data.get("message", "Live network connection lost.")
                    self.controller.show_popup_error(
                        message=err_msg)
                    continue

                self.update_dashboard(
                    data["o2_value"],
                    data["internal_temperature_value"],
                    data["internal_pressure_value"]
                )

                if self.controller.is_logging:
                    add_reading(
                        self.controller.db_con,
                        data["o2_value"],
                        data["internal_temperature_value"],
                        data["internal_pressure_value"]
                    )
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            self.after(1000, self.check_mailbox)


class ReporterFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        lbl_title = ctk.CTkLabel(
            self, text="Generate Daily PDF Report", font=("Arial", 24, "bold"))
        lbl_title.pack(pady=(40, 20))

        # Custom calendar logic
        self.data_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.data_frame.pack(pady=20)

        current_year = dt.datetime.now().year
        self.year_var = ctk.StringVar(value=str(current_year))
        self.month_var = ctk.StringVar(
            value=str(dt.datetime.now().strftime("%m")))
        self.day_var = ctk.StringVar(value=dt.datetime.now().strftime("%d"))

        years = [str(y) for y in range(current_year - 5, current_year + 1)]
        self.year_menu = ctk.CTkOptionMenu(
            self.data_frame, variable=self.year_var, values=years, width=80, command=self.update_days)
        self.year_menu.grid(row=0, column=0, padx=5)

        months = [f"{m:02d}" for m in range(1, 13)]
        self.month_menu = ctk.CTkOptionMenu(
            self.data_frame, variable=self.month_var, values=months, width=80, command=self.update_days)
        self.month_menu.grid(row=0, column=1, padx=5)

        days = [f"{d:02d}" for d in range(1, 32)]
        self.day_menu = ctk.CTkOptionMenu(
            self.data_frame, variable=self.day_var, values=days, width=80)
        self.day_menu.grid(row=0, column=2, padx=5)

        # MUST HAVE
        self.update_days()

        self.btn_generate = ctk.CTkButton(
            self, text="Generate Report", command=self.schedule_generation)
        self.btn_generate.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(self, text="", text_color="gray")
        self.lbl_status.pack(pady=10, fill="x")

        btn_back = ctk.CTkButton(self, text="Back to Menu", text_color="white", fg_color="gray",
                                 hover_color="#4d4d4d", command=lambda: self.controller.show_frame("MainMenuFrame"))
        btn_back.pack(pady=20)

        self.bind("<Configure>", self.update_wrap)

    def update_days(self, choice=None):
        """Dynamically updates the days dropdown based on the selected year and month."""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())

            # Helps us avoid impossible dates
            _, max_days = calendar.monthrange(year, month)

            valid_days = [f"{d:02d}" for d in range(1, max_days + 1)]

            self.day_menu.configure(values=valid_days)

            current_day = int(self.day_var.get())
            if current_day > max_days:
                self.day_var.set(f"{max_days:02d}")

        except ValueError:
            pass

    def schedule_generation(self):
        """Gives the UI time to release the mouse button."""
        self.lbl_status.configure(text="")
        self.btn_generate.configure(state="disabled")
        self.after(150, self._execute_save_dialog)

    def _execute_save_dialog(self):
        """Safely opens the file dialog after the UI has relaxed."""
        selected_date = f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"
        suggested_name = f"Sensor_Parameter_Report_{selected_date}"

        daily_stats = summary(self.controller.db_con, selected_date)
        if not daily_stats:
            self.lbl_status.configure(
                text=f"Failed. No data found for {selected_date}.", text_color="#ff4c4c")
            self.btn_generate.configure(state="normal")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=suggested_name,
            title="Save Daily Report As",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")]
        )

        if not save_path:
            self.btn_generate.configure(state="normal")
            return

        self.lbl_status.configure(
            text=f"Pulling data for {selected_date}...", text_color="gray")

        threading.Thread(target=self._run_engine, args=(
            selected_date, save_path), daemon=True).start()

    def _run_engine(self, target_date, save_path):
        success = generate_daily_report(target_date, save_path)

        self.after(0, self._finish_generation, success, target_date, save_path)

    def _finish_generation(self, success, target_date, save_path):
        """This helps us avoid threading issues."""
        if success:
            self.lbl_status.configure(
                text=f"Success! Report saved at {save_path}.", text_color="#28a745")
        else:
            self.lbl_status.configure(
                text=f"Failed. No data found for {target_date}.", text_color="#ff4c4c")

        self.btn_generate.configure(state="normal", text="Generate Report")

    def update_wrap(self, event):
        """Dynamically calculates the new width and applies it to the label."""
        new_width = self.winfo_width() - 40

        if new_width > 0:
            self.lbl_status.configure(wraplength=new_width)
