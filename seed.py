from sqlalchemy import func
from model import Book, User

from model import connect_to_db, db
from server import app
from datetime import datetime

from csv import reader
import json
import datetime

def load_books():
    """Create library of books"""

    Book.query.delete()

    seed_data = reader(open('seed_data/test_data.csv'))

    for call_num, author, title, edition, pub_info in seed_data:
        
        book = Book(call_num=call_num,
                    author=author,
                    title=title,
                    edition=edition,
                    pub_info=pub_info)

        db.session.add(book)

    db.session.commit()


def load_users():
    """Create users in database"""

    User.query.delete()

    seed_data = json.loads(open('seed_data/MOCK_DATA.json').read())

    for row in seed_data:
        user = User(fname=row['fullname']['fname'],
                    lname=row['fullname']['lname'],
                    email=row['login']['email'],
                    password=row['login']['password'],
                    create_date=datetime.datetime.now()
                    )
        db.session.add(user)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_books()
    load_users()
    # set_val_user_id()