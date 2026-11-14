import customtkinter

customtkinter.set_appearance_mode("dark")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Quick-launcher")
        self.geometry("1100x700")
        self.minsize(800, 500)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.side_bar = customtkinter.CTkFrame(master=self, width=220, height=700)
        self.side_bar.grid(row=0, column=0, sticky="nsew")

        self.main_content = customtkinter.CTkFrame(master=self)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=(30, 0))

app = App()
app.mainloop()
