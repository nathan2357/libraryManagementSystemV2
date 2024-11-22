import csv
import os
from dotenv import load_dotenv


DELIMITER = ","


class CSVError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


def load_env_from_csv(csv_file: str) -> None:
    with open(csv_file, mode="r", newline="") as file:
        reader = csv.reader(file, delimiter=DELIMITER)
        # skip the header
        next(reader)
        for row in reader:
            if len(row) == 2:
                var, value = row
                os.environ[var] = value
    load_dotenv()
    return None


def update_env(csv_file: str, variable: str, new_value: str, revert_to_add: bool = False) -> None:
    with open(csv_file, mode="r", newline="") as file:
        reader = csv.DictReader(file, delimiter=DELIMITER)
        data = [row for row in reader]
        for row in data:
            if row["VARIABLE"] == variable:
                row["VALUE"] = new_value
                break
        else:
            if revert_to_add:
                add_env(csv_file, variable, new_value)
                return None
            else:
                raise CSVError(f"Variable '{variable}' not found, define it with 'add_env' first")

    with open(csv_file, mode="w", newline="") as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=DELIMITER)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    load_env_from_csv(csv_file)

    return None


def add_env(csv_file: str, variable: str, value: str, revert_to_update: bool = False) -> None:
    with open(csv_file, mode="r", newline="") as file:
        reader = csv.DictReader(file, delimiter=DELIMITER)
        data = [row for row in reader]
        for row in data:
            if row["VARIABLE"] == variable:
                if revert_to_update:
                    update_env(csv_file, variable, value)
                    return None
                else:
                    raise CSVError(f"Variable '{variable}' already defined, user 'update_env' instead")

    # Ensure there's a newline at the end of the file before appending
    if os.path.exists(csv_file):
        with open(csv_file, mode="rb") as file:
            file.seek(-1, os.SEEK_END)  # Go to the last byte
            last_byte = file.read(1)
            # If the last byte isn't a newline (b'\n'), add one
            if last_byte != b'\n':
                with open(csv_file, mode="ab") as file:
                    file.write(b'\n')

    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=DELIMITER)
        writer.writerow((variable, value))

    load_env_from_csv(csv_file)

    return None


if __name__ == "__main__":
    try:
        add_env("environVars.csv", "hello", "False")
    except CSVError as e:
        print(e)
    finally:
        update_env("environVars.csv", "hello", "123")

