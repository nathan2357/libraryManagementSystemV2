import tkinter as tk
from tkinter import ttk
import widget

# setup
root = tk.Tk()
root.title("Main Page")
root.geometry("450x300")
root.minsize(200, 200)
root.config(bg="white")

main_lbl = widget.Label.HeadingLabel(root, text="Main Menu", foreground="#459aff",
                                     font=("Helvetica", 50, "bold", "italic"),  background="white")
main_lbl.pack(pady=30)

add_books_btn = widget.Button.StandardButton(root, text="Add Books")
add_books_btn.pack(pady=10)

root.mainloop()
