import customtkinter as ctk
from config import get_env, valid_parameter
from frames import MainMenuFrame, SettingsFrame, MonitorFrame

ctk.set_appearance_mode("dark-blue")

class O2DashboardApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        theme_preference = get_env("THEME_PREFERENCE", "System")
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
        
        sensor_ip = get_env("SENSOR_IP")
        sensor_port = get_env("SENSOR_PORT")
        device_id = get_env("DEVICE_ID")

        if not valid_parameter(sensor_ip) or not valid_parameter(sensor_port) or not valid_parameter(device_id):
            self.show_frame("SettingsFrame")
        else:
            self.show_frame("MainMenuFrame")

if __name__ == "__main__":
    app = O2DashboardApp()
    app.mainloop()