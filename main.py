import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import widget
from mysql.connector import ProgrammingError
import os
import random
import time
import threading
import database
import environHandler
import cipher

ENV_FILE = "environVars.csv"
SALT1 = "sd98u9b893hgb09ufb89n120u98sbu-jauisfh9usdgnsf"
SALT2 = "12b0g9bud8b98sjboi019j98h98b2ugioer8u89dbu0"
SALTED_STR = SALT1 + ENV_FILE + SALT2

ciph = cipher.Cipher(SALTED_STR)

environHandler.load_env_from_csv(ENV_FILE)

root = tk.Tk()
root.geometry("600x400")


def clear_screen(master):
    for child in master.winfo_children():
        child.destroy()


def init():

    clear_screen(root)

    root.title("Setup")
    root.minsize(400, 350)

    main_lbl = widget.Label.StandardLabel(root, text="Database Setup")
    main_lbl.pack(pady=20)

    database_ent = widget.Entry.UsernameEntry(root, placeholder_text="Database name")
    database_ent.pack(pady=10)

    root_username_ent = widget.Entry.UsernameEntry(root, placeholder_text="Root username")
    root_username_ent.pack(pady=10)

    root_password_ent = widget.Entry.PasswordEntry(root, placeholder_text="Root password")
    root_password_ent.pack(pady=10)

    def submit():
        if database_ent.get() == "" or root_username_ent.get() == "" or root_password_ent.get() == "":
            messagebox.showerror("Entry Error", "Please enter the required details to continue")
        else:
            init_connect(database_ent.get(), root_username_ent.get(), root_password_ent.get())

    submit_btn = widget.Button.LoginButton(root, text="Submit", command=lambda: submit())
    submit_btn.pack(pady=15)

    root.bind("<Return>", lambda event: submit())


def init_connect(database_name, root_username, root_password):
    clear_screen(root)
    data = {
        "DatabaseName": database_name,
        "RootUsername": ciph.encrypt(root_username),
        "RootPassword": ciph.encrypt(root_password)
    }
    for key in data.keys():
        environHandler.update_env(ENV_FILE, key, data[key], revert_to_add=True)
    try:
        db = database.Database(database_name=os.getenv("DatabaseName"),
                               root_username=ciph.decrypt(os.getenv("RootUsername")),
                               root_password=ciph.decrypt(os.getenv("RootPassword")),
                               host=os.getenv("HOST"))
        db.root_connect()

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

                root.update_idletasks()  # Update progress bar
                time.sleep(progress_speed * random.uniform(0.2, 0.5))  # Add delay for realism

            progress_label.config(text="Connected!")

        progress = ttk.Progressbar(root, orient='horizontal', length=250, mode='determinate')
        progress.pack(pady=20)

        progress_label = widget.Label.StandardLabel(root, text="Connecting to database, please wait...",
                                                    font=("Courier", 12))
        progress_label.pack(pady=10)

        # Start the loading simulation in a new thread
        loading_thread = threading.Thread(target=simulate_loading, daemon=True)
        loading_thread.start()

        # Poll for the thread completion using after()
        def check_loading_thread():
            if loading_thread.is_alive():
                root.after(300, check_loading_thread)  # Check again after 300ms
            else:
                on_load_complete()  # Run this once the thread is finished

        check_loading_thread()
    except ProgrammingError as e:
        print(e)
        messagebox.showerror(title="Database Error", message=f"Failed to connect to database:"
                                                             f"\nDatabase: {database_name}"
                                                             f"\nRoot username: {root_username}")
        init()

    environHandler.update_env(ENV_FILE, "SETUP_COMPLETE", "True")

    def on_load_complete():
        db.create_users_table()
        db.disconnect()
        signup()


def login():

    def verify():
        if username_ent.get() is None or username_ent.get() == "":
            messagebox.showerror(title="Login failed", message="Enter a username to sign up")
        elif password_ent.get() is None or password_ent.get() == "":
            messagebox.showerror(title="Login failed", message="You must enter a password to continue")
        else:
            db = database.Database(
                database_name=os.getenv("DatabaseName"),
                root_username=ciph.decrypt(os.getenv("RootUsername")),
                root_password=ciph.decrypt(os.getenv("RootPassword"))
            )
            user = db.get_user(username_ent.get())
            print(user)
            # if password_ent.get() == password_2_ent.get():
            #     if username_ent.get() == "admin":
            #         db.insert_user((username_ent.get(), password_ent.get()))
            #         messagebox.showinfo(title="Login successful", message="Welcome admin")
            #     else:
            #         messagebox.showinfo(title="Login successful", message=f"Welcome {username_ent.get()}")
            # else:
            #     messagebox.showerror(title="Login failed", message="Passwords did not match, try again")

    clear_screen(root)

    root.title("Login")
    root.minsize(400, 300)

    signup_frm = ttk.Frame(root)
    signup_frm.columnconfigure(0, weight=1)
    signup_frm.columnconfigure((1, 2), weight=0)
    signup_frm.rowconfigure(0, weight=0)
    signup_lbl = ttk.Label(signup_frm, text="Not got an account?")
    signup_btn = widget.Button.LoginButton(signup_frm, fg_color="#ff451d", hover_color="#f33c14", text="Signup",
                                           font=("Helvetica", 13), height=30, width=60, corner_radius=12,
                                           command=signup)
    signup_lbl.grid(row=0, column=1, padx=5, pady=5)
    signup_btn.grid(row=0, column=2, padx=5, pady=5)
    signup_frm.pack(expand=False, fill="x")

    main_lbl = ttk.Label(root, text="Login", font=("Helvetica", 35))
    main_lbl.pack(pady=10)

    username_ent = widget.Entry.UsernameEntry(root)
    password_ent = widget.Entry.PasswordEntry(root)
    username_ent.pack(pady=10)
    password_ent.pack(pady=10)

    enter_btn = widget.Button.LoginButton(root, command=verify)
    enter_btn.pack()

    root.bind("<Return>", lambda event: verify())


def signup():
    database_name = os.getenv("DatabaseName")
    root_username = ciph.decrypt(os.getenv("RootUsername"))
    root_password = ciph.decrypt(os.getenv("RootPassword"))

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
                        db = database.Database(
                            database_name=database_name,
                            root_username=root_username,
                            root_password=root_password,
                            host=os.getenv("HOST")
                        )
                        db.root_connect()
                        db.insert_user((username_ent.get(), password_ent.get()))
                        return
                    except ProgrammingError as e:
                        print(e)
                        messagebox.showerror(title="Database Error",
                                             message=f"Failed to connect to database:"
                                                     f"\nDatabase: {root_password}"
                                                     f"\nRoot username: {root_username}")
                    messagebox.showinfo(title="Signup successful", message="Welcome admin")
                else:
                    messagebox.showinfo(title="Signup successful", message=f"Welcome {username_ent.get()}")
            else:
                messagebox.showerror(title="Signup failed", message="Passwords did not match, try again")
    clear_screen(root)

    root.title("Sign Up")
    root.minsize(400, 350)

    login_frm = ttk.Frame(root)
    login_frm.columnconfigure(0, weight=1)
    login_frm.columnconfigure((1, 2), weight=0)
    login_frm.rowconfigure(0, weight=0)
    login_lbl = ttk.Label(login_frm, text="Already got an account?")
    login_btn = widget.Button.LoginButton(login_frm, text="Login", fg_color="#ff451d", hover_color="#f33c14",
                                          font=("Helvetica", 13), height=30, width=60, corner_radius=12,
                                          command=login)
    login_lbl.grid(row=0, column=1, padx=5, pady=5)
    login_btn.grid(row=0, column=2, padx=5, pady=5)
    login_frm.pack(expand=False, fill="x")

    main_lbl = ttk.Label(root, text="Sign Up", font=("Helvetica", 35))
    main_lbl.pack(pady=10)

    username_ent = widget.Entry.UsernameEntry(root)
    password_ent = widget.Entry.PasswordEntry(root)
    password_2_ent = widget.Entry.PasswordEntry(root, placeholder_text="Re-enter Password")
    username_ent.pack(pady=10)
    password_ent.pack(pady=10)
    password_2_ent.pack(pady=10)

    enter_btn = widget.Button.LoginButton(root, text="Signup", command=verify)
    enter_btn.pack()

    root.bind("<Return>", lambda event: verify())


def main_page():
    pass


if not os.getenv("SETUP_COMPLETE") == "True":
    init()
else:
    login()


root.mainloop()
