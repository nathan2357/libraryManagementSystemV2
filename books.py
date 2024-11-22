import requests
from dateutil import parser
from typing import Union


class BookNotFoundError(Exception):
    pass


class Book:

    def __init__(self, isbn: str = None, publishers: list[str] = None, image: str = None, date_published: str = None,
                 subjects: list[str] = None, authors: list[str] = None,
                 title: str = None, isbn13: str = None, pages: int = None,
                 bookcase_number: int = None, shelf_number: int = None, from_database: bool = False) -> None:
        if isbn and not from_database:
            self.isbn = isbn
            self.publishers = None
            self.image = None
            self.date_published = None
            self.subjects = None
            self.authors = None
            self.title = None
            self.isbn13 = None
            self.pages = None
            self.set_book_details()
            self.bookcase_number = None
            self.shelf_number = None
        else:
            self.isbn = isbn
            self.publishers = publishers
            self.image = image
            self.date_published = date_published
            self.subjects = subjects
            self.authors = authors
            self.title = title
            self.isbn13 = isbn13
            self.pages = pages
            self.bookcase_number = bookcase_number
            self.shelf_number = shelf_number

    def __repr__(self) -> str:

        def format_parameter(param) -> Union[str, None]:
            return f"'{param}'" if param is not None else None

        isbn_ = format_parameter(self.isbn)
        image_ = format_parameter(self.image)
        date_published_ = format_parameter(self.date_published)
        title_ = format_parameter(self.title)
        isbn13_ = format_parameter(self.isbn13)

        return (f"Book({isbn_}, {self.publishers}, {image_}, "
                f"{date_published_}, {self.subjects}, {self.authors}, {title_}, "
                f"{isbn13_}, {self.pages})")

    def set_book_details(self) -> None:

        def update_all_data(data) -> None:
            set_isbns(data)
            set_publisher(data)
            set_image(data)
            set_date_published(data)
            set_subjects(data)
            set_authors(data)
            set_title(data)
            set_pages(data)
            return None

        def set_isbns(data) -> None:
            self.isbn13 = data.get("data", {}).get("identifiers", {}).get("isbn_13", [None])[0]
            return None

        def set_publisher(data) -> None:
            publishers_dict_list = data.get("data", {}).get("publishers", [])
            publishers_list = []
            for dictionary in publishers_dict_list:
                publishers_list.append(dictionary.get("name", None))
            if None in publishers_list:
                publishers_list.remove(None)
            self.publishers = publishers_list
            return None

        def set_image(data) -> None:
            self.image = data.get("data", {}).get("cover", {}).get("large", None)
            return None

        def set_date_published(data) -> None:

            def extract_year(date_str) -> Union[str, None]:
                try:
                    # Parse the date using dateutil
                    date = parser.parse(date_str)
                    # Return just the year
                    return str(date.year)
                except (ValueError, TypeError):
                    # Handle cases where date_str is not a valid date
                    return None

            self.date_published = extract_year(data.get("data", {}).get("publish_date", None))
            return None

        def set_subjects(data) -> None:
            subjects_dict_list = data.get("data", {}).get("subjects", [])
            subjects_list = []
            for dictionary in subjects_dict_list:
                subjects_list.append(dictionary.get("name", None))
            if None in subjects_list:
                subjects_list.remove(None)
            self.subjects = subjects_list
            return None

        def set_authors(data) -> None:
            authors_dict_list = data.get("data", {}).get("authors", [])
            authors_list = []
            for dictionary in authors_dict_list:
                authors_list.append(dictionary.get("name", None))
            if None in authors_list:
                authors_list.remove(None)
            self.authors = authors_list
            return None

        def set_title(data) -> None:
            self.title = data.get("data", {}).get("title", None)
            return None

        def set_pages(data) -> None:
            self.pages = int(data.get("data", {}).get("number_of_pages", 0))
            return None

        h = {'User-Agent': 'NathanHendry/1.0 (nfooty32@gmail.com)'}
        url = f"http://openlibrary.org/api/volumes/brief/isbn/{self.isbn}.json"
        resp = requests.get(url, headers=h)
        if resp.status_code == 200:
            all_data = resp.json() if resp.json() != [] else {}
            book_data = list(all_data.get("records", {}).values())
            try:
                book_data = book_data[0]
                update_all_data(book_data)
            except IndexError:
                raise BookNotFoundError(f"Book with isbn '{self.isbn}' not found on database")
        else:
            raise BookNotFoundError(f"Book not found on database: recieved status code: {resp.status_code}"
                                    f"\n\tfor book with ISBN: {self.isbn}")

        return None

    def shelf(self, bookcase_number, shelf_number) -> None:
        self.bookcase_number = bookcase_number
        self.shelf_number = shelf_number


if __name__ == "__main__":
    myBook = Book(isbn="9780545069670")
    print(myBook)
