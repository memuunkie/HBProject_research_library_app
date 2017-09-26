from sqlalchemy import func
from model import Book

from model import connect_to_db, db
from server import app
from datetime import datetime

from csv import reader

def load_books():
    """Create library of books"""

    Book.query.delete()

    seed_data = reader(open('test_data.csv'))

    for call_num, author, title, edition, pub_info in seed_data:
        
        book = Book(call_num=call_num,
                    author=author,
                    title=title,
                    edition=edition,
                    pub_info=pub_info)

        db.session.add(book)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_books()
    # set_val_user_id()