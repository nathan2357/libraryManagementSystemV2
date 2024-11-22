import mysql.connector
from typing import Self, Optional
import hasher


class DuplicateUserError(mysql.connector.Error):

    def __init__(self, username: str, message: str = "Duplicate user entry detected."):
        self.username = username
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} Username: {self.username}"


class DatabaseConnectionError(AttributeError):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ParserError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class Database:

    def __init__(self, database_name=None, root_username=None, root_password=None, host=None):
        self.database_name = database_name
        self.root_username = root_username
        self.root_password = root_password
        self.host = host
        self.last_fetch = None
        self.Db = None
        self.Cursor = None

    def __repr__(self) -> str:
        output_str = ""
        try:
            for row in self.last_fetch:
                output_str += f"{row}\n"
            return output_str
        except TypeError:
            return "None"

    def root_connect(self) -> Self:
        self.Db = mysql.connector.connect(
            user=self.root_username,
            password=self.root_password,
            database=self.database_name,
            host=self.host
        )
        self.Cursor = self.Db.cursor()
        return self

    def user_connect(self, user_name, user_password):
        if self.Db:
            self.disconnect()
        self.Db = mysql.connector.connect(
            user=user_name,
            password=user_password,
            database=self.database_name,
            host=self.host
        )
        self.Cursor = self.Db.cursor()
        return

    def disconnect(self) -> Self:
        if self.Cursor:
            self.Cursor.close()
        if self.Db:
            self.Db.close()
        self.Db = None
        self.Cursor = None
        return self

    def execute(self, query, params: tuple = None, commit: bool = True) -> str:
        if self.Cursor:
            self.Cursor.close()
        self.Cursor = self.Db.cursor()
        self.Cursor.execute(query, params=params if params is not None else None)
        if self.Cursor.description:
            self.last_fetch = self.Cursor.fetchall()
        else:
            self.last_fetch = None
        if commit:
            self.Db.commit()
        self.Cursor.close()
        return self.last_fetch

    def list_output(self) -> Optional[list]:
        output_list = []
        try:
            for row in self.last_fetch:
                output_list.append(*row)
            return output_list
        except IndexError:
            return None

    def get_query_dict(self, table_name: str, where_statement: str, args: tuple) -> dict:
        query_dict = {}
        for arg in args:
            print(f"SELECT {arg} FROM {table_name} WHERE {where_statement}")
            self.execute(f"SELECT {arg} FROM {table_name} WHERE {where_statement}")
            query_dict[arg] = self.list_output()
        return query_dict

    def create_books_table(self, table_name) -> str:
        query = (f"CREATE TABLE IF NOT EXISTS {table_name} ("
                 f"book_id SMALLINT AUTO_INCREMENT PRIMARY KEY,"
                 f"isbn VARCHAR(20),"
                 f"isbn_13 VARCHAR(20),"
                 f"title VARCHAR(255),"
                 f"authors VARCHAR(255),"
                 f"subjects TEXT,"
                 f"publishers TEXT,"
                 f"image VARCHAR(255),"
                 f"date_published YEAR,"
                 f"pages SMALLINT,"
                 f"bookcase_number TINYINT,"
                 f"shelf_number TINYINT);")
        self.execute(query)
        return query

    def create_users_table(self) -> str:
        query = f"""
                CREATE TABLE IF NOT EXISTS users (
                user_id SMALLINT AUTO_INCREMENT PRIMARY KEY,
                username varchar(255),
                password VARCHAR(255));
                """
        self.execute(query)
        return query

    @staticmethod
    def get_user_insert_query() -> str:
        return """
                INSERT INTO users (
                username,
                password) VALUES
                (%s, %s));
                """

    def insert_user(self, data: tuple) -> None:
        username = data[0]
        password = hasher.hash_str(data[1])
        try:
            if not self.check_for_existence(username):
                # self.execute(self.get_user_insert_query(), (username, password))
                self.execute(
                    f"INSERT INTO users ("
                    f"username,"
                    f"password) VALUES "
                    f"(%s, %s);", (username, password))
            else:
                raise DuplicateUserError(username)
        except mysql.connector.errors.InternalError as e:
            print("Error:", e)
            raise
        return None

    def get_user(self, username: str) -> str:
        try:
            self.execute(f"SELECT * FROM users WHERE username = %s", (username,))
            return self.last_fetch[0]
        # except AttributeError:
        #     raise DatabaseConnectionError("Cursor not initialised")
        except Exception as e:
            print(e)

    def check_for_existence(self, username) -> bool:
        self.execute(f"SELECT * FROM users WHERE username = %s", (username,))
        if self.last_fetch:
            return True
        else:
            return False

    @staticmethod
    def get_book_insert_query(table_name) -> str:
        return f"""
                INSERT INTO {table_name} (
                isbn,
                isbn_13,
                title,
                authors,
                subjects,
                publishers,
                image,
                date_published,
                pages,
                bookcase_number,
                shelf_number) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """

    def insert_book(self, table_name: str, data: tuple) -> None:
        self.execute(self.get_book_insert_query(table_name), data)
        return None


class Parser:

    def __init__(self):
        pass

    @staticmethod
    def parse_user(user: str) -> Optional[dict]:
        try:
            return {
                "user_id": user[0],
                "username": user[1],
                "password": user[2]
            }
        except TypeError:
            return None


if __name__ == "__main__":
    my_db = Database("library", "nathan_h", '49"/N{U8pvQwzPG+£j{^', 'localhost')
    my_db.root_connect()
    my_db.execute("DELETE FROM users WHERE user_id = 4")
    my_db.disconnect()
