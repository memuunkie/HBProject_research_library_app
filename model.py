""" Models and database functions for CHS database """

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update

db = SQLAlchemy()

####################################################################

class TypeUser(db.Model):
    """Types of users system can accept"""

    __tablename__ = 'types'

    type_id = db.Column(db.Integer,autoincrement=True,
                        primary_key=True)
    type_name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(50), nullable=True)


class User(db.Model):
    """User model for both patrons and admins"""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, 
                        primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)
    checkin_date = db.Column(db.DateTime, nullable=True)
    type_id = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    # user_type = db.relationship('TypeUser', backref='users')


class Book(db.Model):
    """Book model for library items"""

    __tablename__ = 'books'

    book_id = db.Column(db.Integer,autoincrement=True,
                        primary_key=True)
    call_num = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(300), nullable=False)
    title = db.Column(db.String(1000), nullable=True)
    edition = db.Column(db.String(100), nullable=True)
    pub_info = db.Column(db.String(400), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Book book_id=%s call_num=%s>" % (self.book_id, self.call_num)


# class Visit(db.Model):
#     """Visit model for patron time in and time out"""

#     __tablename__ = 'visits'

#     visit_id = db.Column(db.Integer,autoincrement=True,
#                          primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
#     admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'))



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///chs'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    #db.create_all()
    print "Connected to DB."
