import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Self

FONT = ("Helvetica", 20)


def prevent_spaces(new_text):
    # This function is called whenever the user types into the Entry
    if " " in new_text:
        messagebox.showerror(message="This field cannot contain spaces")
        return False  # Reject the input if it contains a space
    return True  # Accept the input otherwise


class Label:

    class StandardLabel(ttk.Label):

        def __init__(self, master, text="text", font=FONT, *args, **kwargs):
            self.master = master
            self.text = text
            self.font = font
            # self.init_size = font[1]
            self.args = args
            self.kwargs = kwargs
            self.scale_factor = 1
            super().__init__(master=self.master, text=self.text, font=self.font,
                             *self.args, **self.kwargs)

        def resize(self, scale_factor: float) -> Self:
            self.scale_factor = scale_factor
            self.font = (self.font[0], round(self.init_size * self.scale_factor), *self.font[2:])
            self.config(font=self.font)
            return self

    class HeadingLabel(StandardLabel):

        def __init__(self, master, font=("Helvetica", 35), *args, **kwargs):
            super().__init__(master=master, font=font, *args, **kwargs)


class Entry:

    class StandardEntry(ctk.CTkEntry):

        def __init__(self, master, font=FONT, width=250, height=40,
                     fg_color="white", text_color="black", border_width=2, corner_radius=10,
                     *args, **kwargs):
            self.master = master
            self.font = font
            self.width = width
            self.height = height
            self.fg_color = fg_color
            self.text_color = text_color
            self.border_width = border_width
            self.corner_radius = corner_radius
            self.args = args
            self.kwargs = kwargs
            self.scale_factor = 1
            super().__init__(master=self.master, font=self.font, width=self.width, height=self.height,
                             fg_color=self.fg_color, text_color=self.text_color,
                             border_width=self.border_width, corner_radius=self.corner_radius,
                             *self.args, **self.kwargs)

        def resize(self, scale_factor: float) -> Self:
            self.scale_factor = scale_factor
            width = round(self.width * self.scale_factor)
            height = round(self.height * self.scale_factor)
            corner_radius = round(self.corner_radius * self.scale_factor)
            font = (self.font[0], round(self.font[1] * self.scale_factor), *self.font[2:])
            self.configure(width=width, height=height, corner_radius=corner_radius,
                           font=font)
            # super().__init__(master=self.master, width=self.width, height=self.height, font=self.font,
            #                  corner_radius=self.corner_radius, fg_color=self.fg_color,
            #                  text_color=self.text_color, border_width=self.border_width, *self.args, **self.kwargs)
            return self

    class UsernameEntry(StandardEntry):

        def __init__(self, master: tk.Tk, placeholder_text: str = "Username",
                     placeholder_text_color: str = "grey", *args, **kwargs):
            super().__init__(master, placeholder_text=placeholder_text,
                             placeholder_text_color=placeholder_text_color, *args, **kwargs)

        def space_delete(self) -> Self:
            self.configure(validate="key", validatecommand=(self.master.register(prevent_spaces), "%P"))
            return self

    class PasswordEntry(UsernameEntry):

        def __init__(self, master, show="*", placeholder_text="Password",
                     *args, **kwargs):
            super().__init__(master=master, show=show, placeholder_text=placeholder_text,
                             *args, **kwargs)


class Button:

    class StandardButton(ctk.CTkButton):

        def __init__(self, master, width=75, height=40, text="button", font=("Helvetica", 16), corner_radius=18,
                     cursor="hand2", *args, **kwargs):
            self.master = master
            self.width = width
            self.height = height
            self.text = text
            self.font = font
            self.corner_radius = corner_radius
            self.cursor = cursor
            self.args = args
            self.kwargs = kwargs
            self.scale_factor = 1
            super().__init__(master=self.master, width=self.width, height=self.height, text=self.text, font=self.font,
                             corner_radius=self.corner_radius, cursor=self.cursor, *self.args, **self.kwargs)

        def resize(self, scale_factor: float) -> Self:
            self.scale_factor = scale_factor
            self.width = round(self.width * self.scale_factor)
            self.height = round(self.height * self.scale_factor)
            self.corner_radius = round(self.corner_radius * self.scale_factor)
            self.font = (self.font[0], round(self.font[1] * self.scale_factor))
            super().__init__(master=self.master, width=self.width, height=self.height, text=self.text, font=self.font,
                             corner_radius=self.corner_radius, cursor=self.cursor, *self.args, **self.kwargs)
            return self

    class LoginButton(StandardButton):

        def __init__(self, master, text="Log in", *args, **kwargs):
            super().__init__(master=master, text=text, *args, **kwargs)


if __name__ == "__main__":
    pass
