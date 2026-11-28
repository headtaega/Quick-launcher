import customtkinter
from PIL import Image
import subprocess
import json

# Set the application theme to dark mode
customtkinter.set_appearance_mode("dark")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Store the error window here.
        # This lets us check if an error window is already open.
        self.err_win = None

        # Checks if its safe to open the config file
        self.config_valid = True

        # Create all parts of the application
        self.config_window()
        self.create_sidebar()
        self.create_logo()
        self.create_add_button()
        self.create_content()
        self.create_buttons()

    # Set the size and basic layout of the main window
    def config_window(self):
        self.title("Quick-launcher")
        self.geometry("1100x700")
        self.minsize(800, 500)

        # Configure the grid layout:
        # Column 0 is the sidebar and keeps its set width.
        # Column 1 is the main area and expands when the window gets bigger.
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Row 0 expands to fill the available window height
        self.grid_rowconfigure(0, weight=1)

    # Create the sidebar on the left side of the window
    def create_sidebar(self):
        self.sidebar = customtkinter.CTkFrame(
            master=self,
            width=220,
            height=700
        )

        # Prevent the frame from changing its size
        # to match the widgets inside it
        self.sidebar.grid_propagate(False)

        # Place the sidebar in column 0
        # sticky="nsew" makes it fill the available space
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Allow widgets inside the sidebar to use its full width
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Give row 1 the remaining vertical space
        self.sidebar.grid_rowconfigure(1, weight=1)

    # Create a small window for displaying error messages
    def show_error(self, message):

        # Check if an error window is already open.
        # winfo_exists() returns True if the window still exists.
        if self.err_win is not None and self.err_win.winfo_exists():
            self.err_lbl.configure(text=message)
            self.err_win.lift()
            self.err_win.focus_force()
            return

        # Create a new error window
        self.err_win = customtkinter.CTkToplevel(master=self)
        self.err_win.title("Error")
        self.err_win.geometry("500x200")
        self.err_win.resizable(False, False)

        self.err_win.transient(self)
        self.err_win.lift()
        self.err_win.focus_force()

        # Display the error message inside the window.
        # The message comes from the function that called show_error().
        self.err_lbl = customtkinter.CTkLabel(
            master=self.err_win,
            text=message,
            font=("Arial", 17, "bold")
        )
        self.err_lbl.pack(expand=True, padx=10, pady=10)

        self.err_win.protocol("WM_DELETE_WINDOW", self.close_error)

        # Prevent the user from clicking the main window
        # until the error window is closed
        self.err_win.grab_set()

    def close_error(self):
        self.err_win.destroy()
        self.err_win = None

    # Confirm if you would like to reset the json file incase of accidential deletion or because of a bug 
    def confirm_reset(self):
        self.confirm_win = customtkinter.CTkToplevel(master=self)
        self.confirm_win.title("Warning")
        self.confirm_win.geometry("700x350")
        self.confirm_win.resizable(False, False)

        self.confirm_win.transient(self)
        self.confirm_win.lift()
        self.confirm_win.focus_force()
        self.confirm_win.grab_set()

        self.confirm_lbl = customtkinter.CTkLabel(
            master=self.confirm_win, 
            text="Config.json is invalid. Do you want to overwrite the existing data?",
            font=("Arial", 17, "bold")
        )
        self.confirm_lbl.pack(expand=False, padx=10, pady=10)

        self.yes_btn = customtkinter.CTkButton(
            master=self.confirm_win,
            text="Yes",
            font=("Arial", 18, "bold"),
            command=self.reset_config,
            fg_color="#416625",
            hover_color="#2A541B",
            width=450,
            height=60
        )
        self.yes_btn.pack(pady=20)

        self.no_btn = customtkinter.CTkButton(
            master=self.confirm_win,
            text="No",
            font=("Arial", 18, "bold"),
            hover_color="#662525",
            fg_color="#893838",
            command=self.cancel_reset,
            width=450,
            height=60
        )
        self.no_btn.pack(pady=20)

    def cancel_reset(self):
        self.confirm_win.destroy()

    def reset_config(self):
        self.data = {"apps": {}}

        try:

            with open(file="config.json", mode="w") as file:
                json.dump(self.data, file)

                self.apps = self.data["apps"]

        except OSError:
            self.confirm_win.grab_release()
            self.show_error("Could not reset config.json")
            self.confirm_win.grab_set()
            return

        self.config_valid = True

        for widget in self.content.winfo_children():
            widget.destroy()

        self.create_buttons()
        
        self.confirm_win.destroy()

    # Read the saved apps from config.json and create their buttons
    def create_buttons(self):
        # Create an empty dictionary for storing app names and commands.
        # Example: {"Notepad": "notepad.exe"}
        self.apps = {}

        # The JSON file stores the app dictionary under the key "apps".
        # self.data contains the complete information from the JSON file.
        self.data = {"apps": self.apps}

        try:
            # Open config.json in read mode ("r")
            # The "with" statement closes the file automatically afterwards
            with open(file="config.json", mode="r") as file:
                self.data = json.load(file)

            # Check if the JSON file has the expected structure.
            # The outer data must be a dictionary,
            # and the value under "apps" must also be a dictionary.
            if not isinstance(self.data, dict) or not isinstance(self.data.get("apps"), dict):
                raise ValueError

            # Stop loading apps if the configuration contains invalid data.
            for name, cmd in self.data["apps"].items():
                if not isinstance(name, str) or not isinstance(cmd, str):
                    self.show_error("App name or commmand must be text")
                    self.config_valid = False
                    return
                if not name.strip() or not cmd.strip():
                    self.show_error("App name or command cannot be empty")
                    self.config_valid = False
                    return
       
            # Get the dictionary containing all saved apps
            self.apps = self.data["apps"]

        except FileNotFoundError:
            try:
                # This happens when config.json does not exist
                with open(file="config.json", mode="w") as file:
                    json.dump(self.data, file)

            except OSError:
                self.show_error("Could not create config.json")
                return

        except (OSError, ValueError):
            # OSError means the file could not be opened or read.
            # ValueError means the file contains invalid JSON
            # or does not have the expected structure.
            self.config_valid = False
            self.data = {"apps": {}}
            self.apps = self.data["apps"]
            self.confirm_reset()

        # Go through every app stored in the dictionary.
        # enumerate() gives each app an index number as well as its name.
        for i, app in enumerate(self.apps):

            # Create the main button used to launch the app
            btn = customtkinter.CTkButton(
                master=self.content,
                font=("Arial", 18, "bold"),
                text=app,
                width=270,
                height=50,

                # lambda remembers the current app name for this button.
                # Without app=app, every button could use the last app name.
                command=lambda app=app: self.launch_app(self.apps[app])
            )

            # Place the button in column 0.
            # The index decides which row the button appears in.
            btn.grid(row=i, column=0, pady=7, padx=5)

            # Create the button used to remove the app
            del_btn = customtkinter.CTkButton(
                master=self.content,
                font=("Arial", 18, "bold"),
                fg_color="#893838",
                hover_color="#662525",
                text="Remove",
                width=270,
                height=50,

                # Remember which app should be removed
                command=lambda app=app: self.delete_app(app)
            )
            del_btn.grid(row=i, column=2, pady=7, padx=5)

            # Create the button used to edit the app
            edit_btn = customtkinter.CTkButton(
                master=self.content,
                font=("Arial", 18, "bold"),
                text="Edit",
                width=270,
                height=50,
                fg_color="#416625",
                hover_color="#2A541B",

                # Open the edit window for the selected app
                command=lambda app=app: self.edit_window(app)
            )
            edit_btn.grid(row=i, column=1, pady=7, padx=5)

    # Open a window where the user can change an app's name and command
    def edit_window(self, app):

        if not self.config_valid:
            return

        self.edit_win = customtkinter.CTkToplevel(master=self)
        self.edit_win.title("Edit app")
        self.edit_win.geometry("600x325")

        # Remember the original name and command.
        # These values are needed when saving the changes.
        self.old_name = app
        self.old_cmd = self.apps[app]

        # Create an entry field for the app's name
        self.edit_name = customtkinter.CTkEntry(
            master=self.edit_win,
            font=("Arial", 18, "bold"),
            width=450,
            height=60
        )
        self.edit_name.pack(pady=20)

        # Put the current app name into the entry field.
        # The user can edit or replace this text.
        self.edit_name.insert(0, self.old_name)

        # Create an entry field for the app's command
        self.edit_cmd = customtkinter.CTkEntry(
            master=self.edit_win,
            font=("Arial", 18, "bold"),
            width=450,
            height=60
        )
        self.edit_cmd.pack(pady=20)

        # Put the current command into the entry field
        self.edit_cmd.insert(0, self.old_cmd)

        # Create the button used to save the changes
        self.edit_save_btn = customtkinter.CTkButton(
            master=self.edit_win,
            text="Save",
            font=("Arial", 18, "bold"),
            command=self.save_edit,
            width=450,
            height=60
        )
        self.edit_save_btn.pack(pady=20)

    # Save the edited app information
    def save_edit(self):

        if not self.config_valid:
            return
        
        # .get() reads the text from an entry field.
        # .strip() removes unnecessary spaces from the beginning and end.
        name = self.edit_name.get().strip()
        cmd = self.edit_cmd.get().strip()

        # Check that neither entry field is empty
        if not name or not cmd:
            self.show_error("Empty fields")
            return

        # Check if another app already uses the new name.
        # The second condition allows the app to keep its current name.
        if name in self.apps and name != self.old_name:
            self.show_error("Name already exists")
            return

        # Save the old command in case writing to the file fails
        old_cmd = self.apps[self.old_name]

        # Remove the app using its old name
        self.apps.pop(self.old_name)

        # Add the app again using the new name and command
        self.apps[name] = cmd

        try:
            # Open config.json in write mode ("w").
            # This replaces the old file contents with the updated data.
            with open(file="config.json", mode="w") as file:
                json.dump(self.data, file)

        except OSError:
            # If saving fails, restore the original app information
            self.apps.pop(name)
            self.apps[self.old_name] = old_cmd

            self.show_error("Could not save config.json")
            return

        # Close the edit window after successful saving
        self.edit_win.destroy()

        # Remove all old app buttons from the main area.
        # winfo_children() gets all widgets inside the content frame.
        # destroy() removes each widget.
        for widget in self.content.winfo_children():
            widget.destroy()

        # Read the updated file and create the buttons again
        self.create_buttons()

    # Remove an app from the list
    def delete_app(self, app):

        if not self.config_valid:
            return

        # Remove the selected app from the dictionary.
        # Store its command so we can restore it if saving fails.
        old_cmd = self.apps.pop(app)

        try:
            # Save the updated dictionary to config.json
            with open(file="config.json", mode="w") as file:
                json.dump(self.data, file)

        except OSError:
            # Restore the removed app if the file could not be saved
            self.apps[app] = old_cmd
            self.show_error("Could not save config.json")
            return

        # Remove all buttons that are currently displayed
        for widget in self.content.winfo_children():
            widget.destroy()

        # Create new buttons without the deleted app
        self.create_buttons()

    # Start the selected program
    def launch_app(self, cmd):
        try:
            # Popen starts the program as a separate process.
            # This allows the launcher to stay open while the app runs.
            subprocess.Popen([cmd])

        except OSError:
            # Show an error if the program cannot be found or started
            self.show_error("Program not found or could not be opened")

    # Load and display the application logo
    def create_logo(self):
        try:
            # Open the image file using Pillow
            self.logo_img = Image.open("assets/icons/Quick-launcher-logo.png")

        except OSError:
            # Show an error if the image file is missing or cannot be opened
            self.show_error("Logo image could not be opened")
            return

        # Convert the Pillow image into a CustomTkinter image.
        # The size argument controls how large the logo appears.
        self.logo = customtkinter.CTkImage(
            dark_image=self.logo_img,
            light_image=self.logo_img,
            size=(100, 100)
        )

        # Create a label that displays the logo image
        self.logo_lbl = customtkinter.CTkLabel(
            master=self.sidebar,
            image=self.logo,
            text=""
        )

        # Place the logo near the bottom of the sidebar
        self.logo_lbl.grid(row=1, column=0, sticky="ws")

    # Create the button used to open the add-app window
    def create_add_button(self):
        self.add_btn = customtkinter.CTkButton(
            master=self.sidebar,
            text="Add app",
            width=250,
            height=80,
            font=("Arial", 17, "bold"),

            # Call add_window when the button is clicked
            command=self.add_window
        )
        self.add_btn.grid(row=0, column=0, pady=5, padx=5)

    # Open a window where the user can enter a new app
    def add_window(self):

        if not self.config_valid:
            return

        self.add_win = customtkinter.CTkToplevel(master=self)
        self.add_win.title("")
        self.add_win.geometry("600x325")

        # Entry field for the app name
        self.add_name = customtkinter.CTkEntry(
            master=self.add_win,
            placeholder_text="Title",
            font=("Arial", 18, "bold"),
            width=450,
            height=60
        )
        self.add_name.pack(pady=20)

        # Entry field for the program command
        self.add_cmd = customtkinter.CTkEntry(
            master=self.add_win,
            placeholder_text="Command",
            font=("Arial", 18, "bold"),
            width=450,
            height=60
        )
        self.add_cmd.pack(pady=20)

        # Button used to save the new app
        self.add_save_btn = customtkinter.CTkButton(
            master=self.add_win,
            text="Save",
            font=("Arial", 18, "bold"),
            command=self.save_add,
            width=450,
            height=60
        )
        self.add_save_btn.pack(pady=20)

    # Save a new app to the JSON file
    def save_add(self):
        # Stops the user form changing the config file when its broken
        if not self.config_valid:
            return
        
        # Get the name and command from the entry fields.
        # strip() removes spaces from the start and end of the text.
        name = self.add_name.get().strip()
        cmd = self.add_cmd.get().strip()

        # Do not continue if either field is empty
        if not name or not cmd:
            self.show_error("Empty fields")
            return

        # Do not allow two apps to have the same name
        if name in self.apps:
            self.show_error("Duplicate title")
            return

        # Add the new app name and command to the dictionary
        self.apps[name] = cmd

        try:
            # Save the updated app list to config.json
            with open(file="config.json", mode="w") as file:
                json.dump(self.data, file)

        except OSError:
            # Remove the app from the dictionary if saving fails.
            # This keeps the displayed data and saved data consistent.
            self.apps.pop(name)

            self.show_error("Could not save config.json")
            return

        # Close the add window after the app has been saved
        self.add_win.destroy()

        # Remove the old buttons from the main area
        for widget in self.content.winfo_children():
            widget.destroy()

        # Create the buttons again so the new app appears
        self.create_buttons()

    # Create the main area where the app buttons are displayed
    def create_content(self):
        self.content = customtkinter.CTkFrame(master=self)

        # Place the content area in column 1, next to the sidebar.
        # "nsew" makes the frame stretch in all four directions.
        # padx adds space on its left side.
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(30, 0)
        )


# Create the application object.
# This runs __init__() and creates the window and its contents.
app = App()

# Start the Tkinter event loop.
# The program waits for clicks, typing, and other user actions.
app.mainloop()