import customtkinter as ctk
from tkcalendar import DateEntry
from pathlib import Path
from tkinter import filedialog
from dotenv import set_key, load_dotenv
import os
import reporter

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class O2Dashboard(ctk.CTk):

    def __init__(self):
        super().__init__()
        
        # Window settings
        self.title("O2 Sensor Control Panel")
        self.geometry("400x300")
        self.grid_columnconfigure(0, weight=1)

        # UI elements
        self.lbl_title = ctk.CTkLabel(self, text="Oxygen Reporter", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=20)
        
        # Calendar plug-in for generating dates
        self.entry_date = DateEntry(
            self,
            width=20,
            background="#1f538d",
            foreground="white",
            bordercolor="#2b2b2b",
            headersbackground="#2b2b2b", 
            headersforeground="white",
            selectbackground="#1f538d",
            selectforeground="white",
            normalbackground="#343638",
            normalforeground="white",
            bottombackground="#343638",
            date_pattern='yyyy-mm-dd'
        )
        self.entry_date.grid(row=1, column=0, padx=20, pady=10)

        self.btn_generate = ctk.CTkButton(self, text="Generate PDF", command=self.trigger_report)
        self.btn_generate.grid(row=2, column=0, padx=20, pady=20)

        self.lbl_status = ctk.CTkLabel(self, text="Ready.", text_color="gray")
        self.lbl_status.grid(row=3, column=0, padx=20, pady=20)

        self.btn_settings = ctk.CTkButton(
            self,
            text="Change Save Folder",
            fg_color="transparent",
            command=self.set_default_directory,
            border_width=1,
            text_color="gray",
        )
        self.btn_settings.grid(row=4, column=0, padx=20, pady=(0,20))

    def trigger_report(self):
        target_date = self.entry_date.get()

        if not target_date:
            self.lbl_status.configure(text="Error: Date field cannot be empty.", text_color="#d32f2f")
            return

        load_dotenv(override=True)
        saved_dir = os.getenv("DEFAULT_OUTPUT_DIR")

        if not saved_dir:
            self.lbl_status.configure(text="First run: Please choose a save folder...", text_color="#fbc02d")
            saved_dir = filedialog.askdirectory(title="First Time Setup: Choose Default Save Directory")

            if not saved_dir:
                self.lbl_status.configure(text="Report cancelled.", text_color="gray")
                return
            
            set_key(".env", "DEFAULT_OUTPUT_DIR", saved_dir)

        print(saved_dir)

        final_path = filedialog.asksaveasfilename(
            initialdir=saved_dir,
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")],
            initialfile=f"Sensor_Parameter_Report_{target_date}.pdf",
            title="Choose where to save your report",
        )

        if not final_path:
            self.lbl_status.configure(text="Report cancelled.", text_color="gray")
            return

        self.lbl_status.configure(text=f"Generating report for {target_date} to {saved_dir}...")
        
        # Reporter logic here...

        self.after(2000, lambda: self.lbl_status.configure(text="Report saved successfully!", text_color="#388e3c"))

    def set_default_directory(self):
        chosen_folder = filedialog.askdirectory(title="Choose Default Save Folder")

        if not chosen_folder:
            return
        
        set_key(".env", "DEFAULT_OUTPUT_DIR", chosen_folder)

        self.lbl_status.configure(text=f"Default changed to: {chosen_folder}")

if __name__ == "__main__":
    app = O2Dashboard()
    app.mainloop()
