import customtkinter as ctk
from config import get_env, valid_parameter
from frames import MainMenuFrame, SettingsFrame, MonitorFrame, ReporterFrame
from database import initialize_db

ctk.set_default_color_theme("dark-blue")


class O2DashboardApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        theme_preference = get_env("THEME_PREFERENCE", "System")
        ctk.set_appearance_mode(theme_preference)

        self.title("Oxygen Monitoring System")
        self.geometry("700x500")

        self.current_page = None
        self.frames = {}
        self.is_logging = False
        self.error_active = False
        database_path = get_env("DATABASE_PATH")
        self.db_con = initialize_db(database_path)

        for PageClass in (MainMenuFrame, MonitorFrame, SettingsFrame, ReporterFrame):
            page_name = PageClass.__name__
            frame = PageClass(parent=self, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.check_initial_setup()

    def show_frame(self, page_name):
        """Brings the requested page to the top."""
        self.current_page = page_name
        frame = self.frames[page_name]
        frame.tkraise()

    def check_initial_setup(self):
        """If essential .env variables are missing, forward them to Settings."""

        sensor_ip = get_env("SENSOR_IP")
        sensor_port = get_env("SENSOR_PORT")
        device_id = get_env("DEVICE_ID")

        if not valid_parameter(sensor_ip) or not valid_parameter(sensor_port) or not valid_parameter(device_id):
            self.show_frame("SettingsFrame")
        else:
            self.show_frame("MainMenuFrame")

    def show_popup_error(self, message="Connection failed."):
        """Creates a professional, modal error dialog."""
        if self.error_active or not self.is_logging:
            return

        self.error_active = True
        self.is_logging = False

        popup = ctk.CTkToplevel(self)
        popup.title("Configuration Error")

        pop_w = 350
        pop_h = 160
        popup.resizable(False, False)

        self.update_idletasks()
        main_x = self.winfo_rootx()
        main_y = self.winfo_rooty()
        main_w = self.winfo_width()
        main_h = self.winfo_height()

        pos_x = main_x + (main_w // 2) - (pop_w // 2)
        pos_y = main_y + (main_h // 2) - (pop_h // 2)
        popup.geometry(f"{pop_w}x{pop_h}+{pos_x}+{pos_y}")

        popup.grab_set()
        popup.focus()

        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_rowconfigure(1, weight=0)

        lbl_warning = ctk.CTkLabel(
            popup,
            text=message,
            font=("Arial", 14)
        )
        lbl_warning.grid(row=0, column=0, pady=(20, 10), padx=20)

        btn_ok = ctk.CTkButton(
            popup,
            text="Acknowledge",
            command=popup.destroy,
            fg_color="#ff4c4c",
            hover_color="#cc0000",
            width=140
        )
        btn_ok.grid(row=1, column=0, pady=(0, 20))

        def close_popup():
            self.error_active = False
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", close_popup)
        btn_ok.configure(command=close_popup)

        if "MainMenuFrame" in self.frames:
            self.frames["MainMenuFrame"].btn_logger.configure(
                text="Start Logging",
                fg_color=["#3B8ED0", "#1F6AA5"],
                hover_color=["#36719F", "#144870"]
            )


if __name__ == "__main__":
    app = O2DashboardApp()
    app.mainloop()
