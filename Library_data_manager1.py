import json
import os
import logging
from typing import List, Optional, Dict

logging.basicConfig(
    filename='library_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

DATA_FILE = "library_data.json"

class Book:
    def __init__(self, title: str, author: str, isbn: str, status: str = "Available"):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.status = status

    def __str__(self):
        return f"[{self.isbn}] '{self.title}' by {self.author} - Status: {self.status}"

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "status": self.status
        }
   
    def from_dict(data: Dict):
        return Book(data["title"], data["author"], data["isbn"], data["status"])

    def is_available(self):
        return self.status == "Available"

    def issue(self):
        if self.is_available():
            self.status = "Issued"
            return True
        return False

    def return_book(self):
        self.status = "Available"


class LibraryInventory:
  
    def __init__(self, filename: str):
        self.filename = filename
        self.books: List[Book] = []
        self.load_books()

    def add_book(self, title: str, author: str, isbn: str):
        if any(b.isbn == isbn for b in self.books):
            print(f"Error: Book with ISBN {isbn} already exists.")
            logging.warning(f"Attempted to add duplicate ISBN: {isbn}")
            return

        new_book = Book(title, author, isbn)
        self.books.append(new_book)
        self.save_books()
        print(f"Book '{title}' added successfully.")
        logging.info(f"Book added: {title} ({isbn})")

    def search_by_title(self, title: str):
        results = [b for b in self.books if title.lower() in b.title.lower()]
        self._display_list(results)
        logging.info(f"Search by title performed: '{title}'. Found {len(results)} results.")

    def search_by_isbn(self, isbn: str):
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None

    def display_all(self):
        print("\n--- Current Library Inventory ---")
        self._display_list(self.books)

    def _display_list(self, book_list: List[Book]):
        if not book_list:
            print("No books found.")
        else:
            for book in book_list:
                print(book)

    def save_books(self):
        try:
            data = [book.to_dict() for book in self.books]
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
            logging.info("Inventory saved to file.")
        except IOError as e:
            print(f"Error saving data: {e}")
            logging.error(f"File save error: {e}")

    def load_books(self):
        if not os.path.exists(self.filename):
            logging.info("No data file found. Starting with empty inventory.")
            return

        file_handle = None
        try:
            file_handle = open(self.filename, 'r')
            data = json.load(file_handle)
            self.books = [Book.from_dict(item) for item in data]
            logging.info(f"Loaded {len(self.books)} books from file.")
        except json.JSONDecodeError:
            print("Error: Data file is corrupted. Starting with empty inventory.")
            logging.error("JSON Decode Error: File corrupted.")
        except IOError as e:
            print(f"Error reading file: {e}")
            logging.error(f"File read error: {e}")
        finally:
            if file_handle:
                file_handle.close()

  
library = LibraryInventory(DATA_FILE)
while True:
    print("\n=== Library Management System ===")
    print("1. Add Book")
    print("2. Issue Book")
    print("3. Return Book")
    print("4. View All Books")
    print("5. Search by Title")
    print("6. Search by ISBN")
    print("7. Exit")
    choice = input("Enter choice (1-7): ").strip()
    try:
        if choice == '1':
            t = input("Enter Title: ").strip()
            a = input("Enter Author: ").strip()
            i = input("Enter ISBN: ").strip()
            if t and a and i:
                library.add_book(t, a, i)
            else:
                print("Error: All fields are required.")
        elif choice == '2':
            isbn = input("Enter ISBN to issue: ").strip()
            book = library.search_by_isbn(isbn)
            if book:
                if book.issue():
                    print(f"Book '{book.title}' issued successfully.")
                    library.save_books()
                    logging.info(f"Book Issued: {isbn}")
                else:
                    print(f"Error: Book is currently {book.status}.")
            else:
                print("Error: Book not found.")
        elif choice == '3':
            isbn = input("Enter ISBN to return: ").strip()
            book = library.search_by_isbn(isbn)
            if book:
                if not book.is_available():
                    book.return_book()
                    print(f"Book '{book.title}' returned successfully.")
                    library.save_books()
                    logging.info(f"Book Returned: {isbn}")
                else:
                    print("Error: This book is already in the library.")
            else:
                print("Error: Book not found.")
        elif choice == '4':
            library.display_all()
        elif choice == '5':
            term = input("Enter title keyword: ").strip()
            library.search_by_title(term)
        elif choice == '6':
            isbn = input("Enter ISBN: ").strip()
            book = library.search_by_isbn(isbn)
            if book:
                print(book)
            else:
                print("No book found with that ISBN.")
        elif choice == '7':
            print("Exiting system. \nGoodbye!")
            logging.info("System exit.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.error(f"Runtime Exception: {e}")
