import customtkinter
from PIL import Image
import subprocess
import json

customtkinter.set_appearance_mode("dark")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.config_window()
        self.create_sidebar()
        self.create_logo()
        self.create_add_app_button()
        self.create_main_content()
        self.create_app_buttons()

    def config_window(self):
        self.title("Quick-launcher")
        self.geometry("1100x700")
        self.minsize(800, 500)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def create_sidebar(self):
        self.side_bar = customtkinter.CTkFrame(master=self, width=220, height=700)
        self.side_bar.grid_propagate(False)
        self.side_bar.grid(row=0, column=0, sticky="nsew")
        self.side_bar.grid_columnconfigure(0, weight=1)
        self.side_bar.grid_rowconfigure(1, weight=1)

    def create_app_buttons(self):
        self.apps_dict = {}
        with open(file="config.json", mode="r") as file:
            self.app_name = json.load(file)
            self.apps_dict = self.app_name["apps"]

        for index, app in enumerate(self.apps_dict.keys()):
            self.app_button = customtkinter.CTkButton(master=self.main_content, font=("Arial", 18, "bold"), text=app, width=300, height=50, command=lambda app=app: self.launch_app(self.apps_dict[app]))
            self.app_button.grid(row=index, column=0, pady=7, padx=5)

    def launch_app(self, command):
        try:
            subprocess.Popen([command])
        except FileNotFoundError:
            self.error_msg = customtkinter.CTkToplevel(master=self)
            self.error_msg.title("error")
            self.error_msg.geometry("200x70")

            self.error_msg_label = customtkinter.CTkLabel(master=self.error_msg, text="No program found", font=("Arial", 17, "bold"))
            self.error_msg_label.pack(pady=20)

    def create_logo(self):
        self.logo_image = Image.open("assets/icons/Quick-launcher-logo.png")
        self.logo = customtkinter.CTkImage(dark_image=self.logo_image, light_image=self.logo_image, size=(100, 100))

        self.logo_label = customtkinter.CTkLabel(
            master=self.side_bar,
            image=self.logo,
            text=""
        )
        self.logo_label.grid(row=1, column=0, sticky="ws")

    def create_add_app_button(self):
        self.sidebar_button = customtkinter.CTkButton(
        master=self.side_bar,
        text="Add app/command",
        width=250,
        height=80,
        font=("Arial", 17, "bold"),
        command=self.create_add_app_window
        )
        self.sidebar_button.grid(row=0, column=0, pady=5, padx=5)

    def create_add_app_window(self):
        self.add_app = customtkinter.CTkToplevel(master=self)
        self.add_app.title("")
        self.add_app.geometry("600x325")

        self.add_app_name = customtkinter.CTkEntry(master=self.add_app, placeholder_text="Title", font=("Arial", 18, "bold"), width=450, height=60)
        self.add_app_name.pack(pady=20)

        self.add_app_cmd = customtkinter.CTkEntry(master=self.add_app, placeholder_text="Command", font=("Arial", 18, "bold"), width=450, height=60)
        self.add_app_cmd.pack(pady=20)

        self.save_add_app_button = customtkinter.CTkButton(master=self.add_app, text="Save", font=("Arial", 18, "bold"), command=self.save_app, width=450, height=60)
        self.save_add_app_button.pack(pady=20)

    def save_app(self):
        self.added_app_name = self.add_app_name.get().strip()
        self.added_app_cmd = self.add_app_cmd.get().strip()
        if not self.added_app_name or not self.added_app_cmd:
            self.error_msg = customtkinter.CTkToplevel(master=self)
            self.error_msg.title("error")
            self.error_msg.geometry("200x70")
            
            self.error_msg_label = customtkinter.CTkLabel(master=self.error_msg, text="Empty fields", font=("Arial", 17, "bold"))
            self.error_msg_label.pack(pady=20)
            return

        if self.added_app_name in self.apps_dict:
            self.error_msg = customtkinter.CTkToplevel(master=self)
            self.error_msg.title("error")
            self.error_msg.geometry("200x70")
                        
            self.error_msg_label = customtkinter.CTkLabel(master=self.error_msg, text="Duplicate title", font=("Arial", 17, "bold"))
            self.error_msg_label.pack(pady=20)
            return
                
        with open(file="config.json", mode="w") as file:
            self.apps_dict[self.added_app_name] = self.added_app_cmd
            json.dump(obj=self.app_name, fp=file)

        for widget in self.main_content.winfo_children():
            widget.destroy()
        self.create_app_buttons()

    def create_main_content(self):
        self.main_content = customtkinter.CTkFrame(master=self)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=(30, 0))

app = App()
app.mainloop()
