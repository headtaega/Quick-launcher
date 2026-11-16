import customtkinter
from PIL import Image

customtkinter.set_appearance_mode("dark")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.config_window()
        self.create_sidebar()
        self.create_logo()
        self.create_sidebar_button()
        self.create_main_content()

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
        self.side_bar.grid_columnconfigure(1, weight=1)

    def create_logo(self):
        self.logo_image = Image.open("assets/icons/Quick-launcher-logo.png")
        self.logo = customtkinter.CTkImage(dark_image=self.logo_image, light_image=self.logo_image, size=(64, 64))
        self.logo_label = customtkinter.CTkLabel(
            master=self.side_bar,
            image=self.logo,
            text=""
        )
        self.logo_label.grid(row=0, column=0, sticky="nw")

    def create_sidebar_button(self):
        self.sidebar_button = customtkinter.CTkButton(master=self.side_bar, text="Button", command=self.button_event)
        self.sidebar_button.grid(row=0, column=1, sticky="nsew")

    def button_event(self):
        print("button pressed")

    def create_main_content(self):
        self.main_content = customtkinter.CTkFrame(master=self)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=(30, 0))

app = App()
app.mainloop()
