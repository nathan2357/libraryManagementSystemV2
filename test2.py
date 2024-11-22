import tkinter as tk
from tkinter import ttk
from tkinter import ttk, Label, PhotoImage
import requests
from PIL import Image, ImageTk  # Install Pillow library


class LibrarySystemMainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Library System")

        # Configure the root window
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        # Main heading
        heading_label = tk.Label(
            root,
            text="Home Library System",
            font=("Helvetica", 20, "bold"),
            pady=20
        )
        heading_label.pack()

        # Menu bar
        menu_bar = tk.Menu(root)
        self.root.config(menu=menu_bar)

        # "Manage Books" menu
        books_menu = tk.Menu(menu_bar, tearoff=0)
        books_menu.add_command(label="Search Books", command=self.open_search_books_page)
        menu_bar.add_cascade(label="Manage Books", menu=books_menu)

        # Quit Button
        quit_button = tk.Button(
            root,
            text="Quit",
            font=("Helvetica", 14),
            bg="red",
            fg="white",
            command=self.root.quit
        )
        quit_button.pack(pady=20)

    def open_search_books_page(self):
        # Hide the main window
        self.root.withdraw()

        # Open the search books window
        search_window = tk.Toplevel(self.root)
        SearchBooksPage(search_window, self.root)


class SearchBooksPage:
    def __init__(self, root, main_root):
        self.root = root
        self.main_root = main_root
        self.root.title("Search Books")
        self.root.geometry("900x500")

        # Dummy data with image URLs
        self.books = [
            {"Title": "Book 1", "Author": "Author A", "ISBN": "123456", "Date": "2023-01-01",
             "Image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRxZYeqBNbv7SJ03D1_R5yEnMeDZbX_0CIlCQ&s"},
            {"Title": "Book 2", "Author": "Author B", "ISBN": "789012", "Date": "2022-05-15",
             "Image": "https://upload.wikimedia.org/wikipedia/en/thumb/b/b1/Portrait_placeholder.png/400px-Portrait_placeholder.png"}
        ]

        # Table for search results
        table_frame = tk.Frame(root)
        table_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        columns = ("Title", "Author", "ISBN", "Date")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="w", width=150)
        self.table.pack(fill="both", expand=True)

        # Add data to the table
        for book in self.books:
            self.table.insert("", "end", values=(book["Title"], book["Author"], book["ISBN"], book["Date"]))

        # Bind selection event to show image
        self.table.bind("<<TreeviewSelect>>", self.show_book_image)

        # Image display area
        self.image_label = Label(root, text="Select a book to see its image", font=("Helvetica", 12))
        self.image_label.pack(side="right", padx=20, pady=10)

    def show_book_image(self, event):
        selected_item = self.table.selection()
        if selected_item:
            # Get selected book data
            book_index = int(self.table.index(selected_item[0]))
            book = self.books[book_index]

            # Load image from URL
            try:
                image = Image.open(requests.get(book["Image"], stream=True).raw)
                image = image.resize((150, 150))  # Resize for display
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo, text="")  # Clear text, show image
                self.image_label.image = photo
            except Exception as e:
                self.image_label.config(text=f"Error loading image: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LibrarySystemMainMenu(root)
    root.mainloop()
