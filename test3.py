import tkinter as tk
from tkinter import ttk, messagebox
from customtkinter import set_appearance_mode, set_default_color_theme, CTkFont
import widget
from mysql.connector import ProgrammingError
import os
import random
import time
import threading
import database
import environHandler
import cipher
import hasher
from typing import Optional, Self, Type

set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
set_default_color_theme("blue")

ENV_FILE = "environVars.csv"
SALT1 = "sd98u9b893hgb09ufb89n120u98sbu-jauisfh9usdgnsf"
SALT2 = "12b0g9bud8b98sjboi019j98h98b2ugioer8u89dbu0"
SALTED_STR = SALT1 + ENV_FILE + SALT2

ciph = cipher.Cipher(SALTED_STR)

environHandler.load_env_from_csv(ENV_FILE)


class Window:

    active_window: Optional[Self] = None
    main_connection: Optional[database.Database] = None

    def __init__(self, root_):
        self.root: tk.Tk = root_
        self.root.iconbitmap(None)
        if Window.main_connection:
            self.db = Window.main_connection.root_connect()
        else:
            self.db = None

        if Window.active_window:
            Window.active_window.destroy()

        Window.active_window = self

        self.setup()

    def setup(self, *args, **kwargs):
        """
        Define the layout for the window. Override in subclasses.
        """
        label = tk.Label(self.root, text="Base Window", font=("Helvetica", 16))
        label.pack(pady=20)

    def destroy(self):
        for child in self.root.winfo_children():
            child.destroy()
        if self.db:
            self.db.disconnect()

    def load_new(self, new_window: Type[Self], *args, **kwargs):
        new_window(self.root, *args, **kwargs)

    @classmethod
    def open_connection(cls, database_name, root_username, root_password, host):
        cls.main_connection = database.Database(
            database_name=database_name,
            root_username=root_username,
            root_password=root_password,
            host=host
        ).root_connect()

    @classmethod
    def close_connection(cls):
        cls.main_connection.disconnect()


class Init(Window):

    def setup(self):

        self.root.title("Setup")
        self.root.geometry("600x475")
        self.root.minsize(400, 350)
        self.root.iconbitmap("assets/cogs.ico")

        def submit():
            if database_ent.get() == "" or root_username_ent.get() == "" or root_password_ent.get() == "":
                messagebox.showerror("Entry Error", "Please enter the required details to continue")
            else:
                data = {
                    "DBDatabaseName": database_ent.get(),
                    "DBRootUsername": ciph.encrypt(root_username_ent.get()),
                    "DBRootPassword": ciph.encrypt(root_password_ent.get())
                }
                for key in data.keys():
                    environHandler.update_env(ENV_FILE, key, data[key], revert_to_add=True)
                self.load_new(InitConnect)

        main_lbl = widget.Label.StandardLabel(self.root, text="Database Setup")
        main_lbl.pack(pady=20)

        database_ent = widget.Entry.UsernameEntry(self.root, placeholder_text="Database name").space_delete()
        database_ent.pack(pady=10)

        root_username_ent = widget.Entry.UsernameEntry(self.root, placeholder_text="Root username").space_delete()
        root_username_ent.pack(pady=10)

        root_password_ent = widget.Entry.PasswordEntry(self.root, placeholder_text="Root password").space_delete()
        root_password_ent.pack(pady=10)

        submit_btn = widget.Button.LoginButton(self.root, text="Submit", command=lambda: submit())
        submit_btn.pack(pady=15)
        self.root.bind("<Return>", lambda event: submit())


class InitConnect(Window):

    def setup(self):

        self.root.iconbitmap("assets/cogs.ico")

        try:
            Window.open_connection(os.getenv("DBDatabaseName"),
                                   ciph.decrypt(os.getenv("DBRootUsername")),
                                   ciph.decrypt(os.getenv("DBRootPassword")),
                                   os.getenv("DBHost"))
            self.db = Window.main_connection

            # Function to simulate loading in a separate thread
            def simulate_loading():
                progress['value'] = 0  # Start at 0%
                max_progress = 100
                progress_speed = 0.5  # Base speed for increments

                while progress['value'] < max_progress:
                    increment = random.uniform(3, 6)
                    progress['value'] += increment
                    if progress['value'] > max_progress:
                        progress['value'] = max_progress

                    self.root.update_idletasks()  # Update progress bar
                    time.sleep(progress_speed * random.uniform(0.2, 0.5))  # Add delay for realism

                progress_label.config(text="Connected!")

            progress = ttk.Progressbar(self.root, orient='horizontal', length=250, mode='determinate')
            progress.pack(pady=20)

            progress_label = widget.Label.StandardLabel(self.root, text="Connecting to database, please wait...",
                                                        font=("Courier", 12))
            progress_label.pack(pady=10)

            # Start the loading simulation in a new thread
            loading_thread = threading.Thread(target=simulate_loading, daemon=True)
            loading_thread.start()

            # Poll for the thread completion using after()
            def check_loading_thread():
                if loading_thread.is_alive():
                    self.root.after(300, check_loading_thread)  # Check again after 300ms
                else:
                    on_load_complete()  # Run this once the thread is finished

            check_loading_thread()
        except ProgrammingError as e:
            print(e)
            messagebox.showerror(title="Database Error",
                                 message=f"Failed to connect to database:"
                                         f"\nDatabase: {os.getenv("DBDatabaseName")}"
                                         f"\nRoot username: {ciph.decrypt(os.getenv("DBRootUsername"))}"
                                         f"\n\nMake sure the username and password is correct, and that you are "
                                         f"connecting to the right database")
            self.load_new(Init)

        environHandler.update_env(ENV_FILE, "SETUP_COMPLETE", "True")

        def on_load_complete():
            self.db.create_users_table()
            self.db.disconnect()
            self.load_new(SignUp)


class SignUp(Window):

    def setup(self):

        self.root.iconbitmap("assets/writing.ico")

        database_name = os.getenv("DBDatabaseName")
        root_username = ciph.decrypt(os.getenv("DBRootUsername"))
        root_password = ciph.decrypt(os.getenv("DBRootPassword"))

        def verify():
            if username_ent.get() is None or username_ent.get() == "":
                messagebox.showerror(title="Signup failed", message="Enter a username to sign up")
            elif password_ent.get() is None or password_ent.get() == "":
                messagebox.showerror(title="Signup failed", message="You must enter a password to continue")
            elif len(password_ent.get()) < 8 or len(password_ent.get()) > 32:
                messagebox.showerror(title="Signup failed", message="Password must be between 8 and 32 characters")
            else:
                if password_ent.get() == password_2_ent.get():
                    if username_ent.get() == "admin":
                        try:
                            if Window.main_connection:
                                self.db = Window.main_connection.root_connect()
                            else:
                                self.db = database.Database(
                                    database_name=database_name,
                                    root_username=root_username,
                                    root_password=root_password,
                                    host=os.getenv("DBHost")
                                ).root_connect()

                            try:
                                self.db.insert_user((username_ent.get(), password_ent.get()))
                                messagebox.showinfo("Signup successful", "Admin user has been successfully added")
                            except database.DuplicateUserError as e:
                                print(e)
                                messagebox.showerror("Signup Error", "Admin user has already been created")
                                self.load_new(SignUp)
                            except Exception as e:
                                messagebox.showerror("ERROR", str(e))
                            return
                        except ProgrammingError as e:
                            print(e)
                            messagebox.showerror(title="Database Error",
                                                 message=f"Failed to connect to database:"
                                                         f"\nDatabase: {root_password}"
                                                         f"\nRoot username: {root_username}")
                    else:
                        messagebox.showinfo(title="Signup successful", message=f"Username: {username_ent.get()}")
                else:
                    messagebox.showerror(title="Signup failed", message="Passwords did not match, try again")

        self.root.title("Sign Up")
        self.root.geometry("600x475")
        self.root.minsize(400, 350)

        login_frm = ttk.Frame(self.root)
        login_frm.columnconfigure(0, weight=1)
        login_frm.columnconfigure((1, 2), weight=0)
        login_frm.rowconfigure(0, weight=0)
        login_lbl = ttk.Label(login_frm, text="Already got an account?")
        login_btn = widget.Button.LoginButton(login_frm, text="Login", fg_color="#ff451d", hover_color="#f33c14",
                                              font=("Helvetica", 13), height=30, width=60, corner_radius=12,
                                              command=lambda: self.load_new(LogIn))
        login_lbl.grid(row=0, column=1, padx=5, pady=5)
        login_btn.grid(row=0, column=2, padx=5, pady=5)
        login_frm.pack(expand=False, fill="x")

        main_lbl = ttk.Label(self.root, text="Sign Up", font=("Helvetica", 35))
        main_lbl.pack(pady=10)

        username_ent = widget.Entry.UsernameEntry(self.root)
        password_ent = widget.Entry.PasswordEntry(self.root)
        password_2_ent = widget.Entry.PasswordEntry(self.root, placeholder_text="Re-enter Password")
        username_ent.pack(pady=10)
        password_ent.pack(pady=10)
        password_2_ent.pack(pady=10)

        enter_btn = widget.Button.LoginButton(self.root, text="Signup", command=verify)
        enter_btn.pack()

        self.root.bind("<Return>", lambda event: verify())


class LogIn(Window):

    def setup(self):

        self.root.iconbitmap("assets/writing.ico")

        def verify():
            if username_ent.get() is None or username_ent.get() == "":
                messagebox.showerror(title="Login failed", message="Enter a username to sign up")
            elif password_ent.get() is None or password_ent.get() == "":
                messagebox.showerror(title="Login failed", message="You must enter a password to continue")
            else:
                if Window.main_connection:
                    self.db = Window.main_connection.root_connect()
                else:
                    self.db = database.Database(
                        database_name=os.getenv("DBDatabaseName"),
                        root_username=ciph.decrypt(os.getenv("DBRootUsername")),
                        root_password=ciph.decrypt(os.getenv("DBRootPassword")),
                        host=os.getenv("DBHost")
                    ).root_connect()

                user = database.Parser.parse_user(self.db.get_user(username_ent.get()))
                if user:
                    if hasher.check_hash(password_ent.get(), user["password"]):
                        messagebox.showinfo("Login successful", "Welcome, admin")
                        self.load_new(AdminMainPage)
                    else:
                        messagebox.showerror(title="Login failed", message="Username or password incorrect")
                else:
                    messagebox.showerror(title="Login failed", message="Username or password incorrect")

        self.root.title("Login")
        self.root.geometry("600x475")
        self.root.minsize(400, 300)

        signup_frm = ttk.Frame(self.root)
        signup_frm.columnconfigure(0, weight=1)
        signup_frm.columnconfigure((1, 2), weight=0)
        signup_frm.rowconfigure(0, weight=0)
        signup_lbl = ttk.Label(signup_frm, text="Not got an account?")
        signup_btn = widget.Button.LoginButton(signup_frm, fg_color="#ff451d", hover_color="#f33c14", text="Signup",
                                               font=("Helvetica", 13), height=30, width=60, corner_radius=12,
                                               command=lambda: self.load_new(SignUp))
        signup_lbl.grid(row=0, column=1, padx=5, pady=5)
        signup_btn.grid(row=0, column=2, padx=5, pady=5)
        signup_frm.pack(expand=False, fill="x")

        main_lbl = ttk.Label(self.root, text="Login", font=("Helvetica", 35))
        main_lbl.pack(pady=10)

        username_ent = widget.Entry.UsernameEntry(self.root)
        password_ent = widget.Entry.PasswordEntry(self.root)
        username_ent.pack(pady=10)
        password_ent.pack(pady=10)

        enter_btn = widget.Button.LoginButton(self.root, command=verify)
        enter_btn.pack()

        self.root.bind("<Return>", lambda event: verify())


class AdminMainPage(Window):

    def setup(self):

        self.root.title("Main Page")
        self.root.minsize(400, 300)
        self.root.iconbitmap("assets/book.ico")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=4)

        font = ("Helvetica", 10)
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Search books", font=font)
        file_menu.add_separator()
        file_menu.add_command(label="Add books", font=font)
        file_menu.add_command(label="Edit books", font=font)

        menu_bar.add_cascade(label="Books", menu=file_menu, font=font)

        edit_menu = tk.Menu(menu_bar, tearoff=False)
        edit_menu.add_command(label="Search users", font=font)
        edit_menu.add_separator()
        edit_menu.add_command(label="Add users", font=font)
        edit_menu.add_command(label="Edit users", font=font)

        menu_bar.add_cascade(label="Users", menu=edit_menu, font=font)

        # Attach Menu to App
        self.root.config(menu=menu_bar)

        heading_frm = ttk.Frame(self.root)
        main_menu_lbl = widget.Label.HeadingLabel(heading_frm, text="Main Menu", foreground="#288aff",
                                                  font=CTkFont("Helvetica", 45, "bold", "italic"))
        main_menu_lbl.grid(row=0, column=0)
        heading_frm.grid()

        search_frm = ttk.Frame(self.root)
        search_frm.grid_rowconfigure((0, 2), weight=0)
        search_frm.grid_rowconfigure(1, weight=1)

        search_frm.grid_columnconfigure(0, weight=1)
        search_frm.grid_columnconfigure((1, 2), weight=0)

        search_bar_ent = widget.Entry.StandardEntry(search_frm, corner_radius=3)
        search_bar_ent.grid(row=0, column=0, sticky="nesw", pady=1, padx=1)

        new_ent = widget.Entry.StandardEntry(search_frm, corner_radius=3)
        new_ent.grid(row=1, column=0, sticky="nesw", pady=1, padx=1)

        new2_ent = widget.Entry.StandardEntry(search_frm, corner_radius=3)
        new2_ent.grid(row=0, column=1, rowspan=2, sticky="nesw", pady=1, padx=1)

        search_frm.grid(row=1, column=0, sticky="nesw", padx=5, pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    SignUp(root)
    root.mainloop()
