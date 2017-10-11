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
    
    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<TypeUser type_id=%s type_name=%s>" % (self.type_id, 
                                                       self.type_name)

class User(db.Model):
    """User model for both patrons and admins"""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, 
                        primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)
    visit_timein = db.Column(db.DateTime, nullable=True) # delete
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('types.type_id'), default=2)

    user_type = db.relationship('TypeUser',
                                backref=db.backref('types', order_by=user_id))

    def serialize(self):
        """For User JSON info"""

        info = {
                'user_id': self.user_id,
                'fname': self.fname,
                'lname': self.lname,
                'create_date': str(self.create_date),
                'visit_timein': str(self.visit_timein),
                'type_id': self.user_type.type_id
        }

        return info

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<User user_id=%s type_id=%s>" % (self.user_id, self.type_id)


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

    def serialize(self):
        """For Book JSON info"""

        info = {
                'book_id': self.book_id,
                'call_num': self.call_num,
                'title': self.title,
                'author': self.author,
                'edition': self.edition,
                'pub_info': self.pub_info
        }

        return info


    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Book book_id=%s call_num=%s>" % (self.book_id, self.call_num)


class Visit(db.Model):
    """Visit model for patron time in and time out"""

    __tablename__ = 'visits'

    visit_id = db.Column(db.Integer,autoincrement=True,
                         primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    visit_timein = db.Column(db.DateTime, nullable=False)
    visit_timeout = db.Column(db.DateTime, nullable=True)

    #reference visit.user/visit.admin -- admin.admin_visit, user.user_visit
    user = db.relationship('User', foreign_keys='Visit.user_id', 
                            backref=db.backref('user_visit'))
    admin = db.relationship('User', foreign_keys='Visit.admin_id',
                            backref=db.backref('admin_visit'))

    def serialize(self):
        """For JSON info"""

        info = {
                'visit_id': self.visit_id,
                'user_id': self.user_id,
                'admin_id': self.admin_id,
                'visit_timein': str(self.visit_timein),
                'visit_timeout': str(self.visit_timeout)
        }

        return info

    
    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Visit visit_id=%s user_id=%s>" % (self.visit_id, self.user_id)


class VisitItem(db.Model):
    """Attach Books to a Visit"""

    __tablename__ = 'visit_items'

    item_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), 
                        nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.visit_id'), 
                        nullable=False)
    checkout_time = db.Column(db.DateTime, nullable=False)
    is_returned = db.Column(db.Boolean, nullable=False, default=False)

    book = db.relationship('Book', backref=db.backref('visit_book'))
    visit = db.relationship('Visit', backref=db.backref('visit_item'))

    def serialize(self):
        """For VisitItem JSON info"""

        info = {
                'book_id': self.book_id,
                'visit_id': self.visit_id,
                'title': self.book.title,
                'author': self.book.author,
                'call_num': self.book.call_num,
                'is_returned': self.is_returned
        }

        return info


    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Item visit_id=%s book_id=%s>" % (self.visit_id, self.book_id)


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
