import customtkinter
import tkinter as tk


app = tk.Tk()


def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)


optionmenu = customtkinter.CTkOptionMenu(app, values=["option 1", "option 2"],
                                         command=optionmenu_callback)
optionmenu.set("option 2")

optionmenu.pack()

app.mainloop()
