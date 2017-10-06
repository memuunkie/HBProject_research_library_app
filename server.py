from jinja2 import StrictUndefined

from flask import jsonify
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)

from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import and_, or_

from model import Book, User, Visit, VisitItem
from model import connect_to_db, db

from datetime import datetime


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABCItseasyas123orsimpleasDo-Re-MiABC123babyyouandmegirl"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Home"""
    return render_template("home.html")


@app.route('/library')
def library_view():
    """render the librarian view"""

    return render_template('library_view.html')


@app.route('/add-visit', methods=['GET'])
def visit_form():
    """Show visit form"""

    return render_template('visit_results.html')


@app.route('/add-visit', methods=['POST'])
def add_visit():
    """Add a Visit to the database"""

    print "Got to the POST"

    user = request.form.get('user-id')
    admin = request.form.get('admin-id')
    
    visit = Visit(user_id=user, admin_id=admin, 
                  visit_timein=datetime.now())

    db.session.add(visit)
    db.session.commit()

    return redirect('/visit')


@app.route('/visit')
def show_visits():
    """Lisit of all visitors"""

    today = datetime.now()

    visits = Visit.query.all()

    return render_template('visit_results.html', visits=visits)


@app.route('/visit/<int:visit_id>', methods=['GET'])
def show_visit(visit_id):
    """Show the visit details"""

    visit_items = VisitItem.query.filter_by(visit_id=visit_id).all()
    visit_deets = Visit.query.filter_by(visit_id=visit_id).one()

    return render_template('visit_detail.html', visit_deets=visit_deets,
                            visit_items=visit_items)


@app.route('/visit/<int:visit_id>', methods=['POST'])
def add_items(visit_id):
    """Add a book to a visit"""

    book_id = int(request.form['book-id'])

    book = VisitItem.query.filter_by(book_id=book_id).first()

    if book:
        flash("Book already in use.")
    else:
        visit_item = VisitItem(visit_id=visit_id, book_id=book_id,
                               checkout_time=datetime.now())
        flash("Book added.")
        db.session.add(visit_item)

    db.session.commit()

    return redirect('/visit/%s' % visit_id)

@app.route('/search-books', methods=['GET'])
def search_books():
    """Do a search on books and return a list of matches"""

    title = get_return_wildcard('title')
    author = get_return_wildcard('author')
    call_num = get_return_wildcard('call-num')

    books = Book.query.filter(or_(Book.title.ilike(title), 
                                 Book.author.ilike(author),
                                 Book.call_num.ilike(call_num))).all()

    return render_template('book_results.html', books=books)


@app.route('/search-users', methods=['GET'])
def search_users():
    """Do a search of user and return a list of possible matches"""

    email = get_return_wildcard('email')
    fname = get_return_wildcard('fname')
    lname = get_return_wildcard('lname')

    users = User.query.filter(or_(User.email.ilike(email), 
                                    User.fname.ilike(fname), 
                                    User.lname.ilike(lname))).all()

    return render_template('user_results.html', users=users)


#Everything below are for AJAX calls and rendering only on home.html
###############################################################
@app.route('/display-visitors')
def display_visitors():
    """List of current visitors"""

    visits = db.session.query(Visit).filter(Visit.visit_timeout==None).all()

    all_visits = []

    for visit in visits:
        x = visit.user.serialize()
        x.update(visit.serialize())
        all_visits.append(x)

    print jsonify(all_visits)
    return jsonify(all_visits)


@app.route('/find-users.json', methods=['GET'])
def find_user():
    """Do a search of user and return a list of possible matches"""

    email = get_return_wildcard('email')
    fname = get_return_wildcard('fname')
    lname = get_return_wildcard('lname')

    users = User.query.filter(or_(User.email.ilike(email), 
                                    User.fname.ilike(fname), 
                                    User.lname.ilike(lname))).all()

    users = [u.serialize() for u in users]

    return jsonify(users)


@app.route('/new-visit.json', methods=['POST'])
def add_new_visit():
    """Add a Visit to the database"""

    print "Adding via AJAX"

    user = request.form.get('user-id')
    admin = session['user']

    has_visit = db.session.query(Visit).filter(Visit.user_id == user,
                                               Visit.visit_timeout == None).first()

    if has_visit is None:
        visit = Visit(user_id=user, admin_id=admin, 
                      visit_timein=datetime.now())

        db.session.add(visit)
        db.session.commit()

        return "Success to post"
    else:
        return "None"


@app.route('/log-in.json', methods=['POST'])
def log_in_user():
    """Login an existing user"""
    """Right now, just admin to test adding visits"""

    email = request.form.get('email')
    password = request.form.get('password')

    user = db.session.query(User).filter(User.email == email,
                                         User.password == password).first()

    if user is None:
        print 'No such user'
        return 'None'
    else:
        session['user'] = user.user_id
        return 'True'
    # if user.type_id == 2 render_template("user page")
    # if user.type_id == 1 render_template("library page")


@app.route('/checkout.json', methods=['POST'])
def checkout_user():
    """Checkout user"""
    """Does not account for visit items"""

    user_id = request.form.get('user-id')

    visit = db.session.query(Visit).filter(Visit.user_id==user_id,
                                        Visit.visit_timeout == None).first()

    visit.visit_timeout = datetime.now()

    db.session.commit()

    print "User", user_id, "has been checked out"
    return jsonify(visit.serialize())


@app.route('/find-books.json', methods=['GET'])
def find_book():
    """Do a search on books and return a list of matches"""

    title = get_return_wildcard('title')
    author = get_return_wildcard('author')
    call_num = get_return_wildcard('call-num')

    books = Book.query.filter(or_(Book.title.ilike(title), 
                                 Book.author.ilike(author),
                                 Book.call_num.ilike(call_num))).all()

    books = [b.serialize() for b in books]

    return jsonify(books)


@app.route('/add-book.json', methods=['POST'])
def add_book():
    """Add a book to a visit"""

    book_id = request.form.get('book-id')
    visit_id = request.form.get('visit-id')

    check_book = VisitItem.query.filter(VisitItem.book_id == book_id,
                                        VisitItem.is_returned == False).first()

    if check_book is None:
        visit_item = VisitItem(visit_id=visit_id, book_id=book_id,
                               checkout_time=datetime.now())
        db.session.add(visit_item)
        db.session.commit()

    else:
        return "This book is currently checked out"

    return "This book has been added to the user's record."


@app.route('/book-search', methods=['GET'])
def find_visit_books():
    """render the book search page"""

    user = request.args.get('user-id')

    visit = Visit.query.filter(Visit.user_id == user,
                               Visit.visit_timeout == None).first()

    return render_template('book_search.html', visit=visit)


@app.route('/return-book', methods=['GET'])
def checked_books():
    """outstanding books from user"""

    user = request.args.get('user-id')

    visit = Visit.query.filter(Visit.user_id == user,
                               Visit.visit_timeout == None).first()

    visit_items = VisitItem.query.filter(VisitItem.visit_id == visit.visit_id,
                                         VisitItem.is_returned == False).all()

    return render_template('return_books.html', visit=visit, visit_items=visit_items)


@app.route('/show-books.json', methods=['GET'])
def show_outstanding():
    """show all the outstanding books"""

    visit = request.args.get('visit-id')

    if visit is None:
        return []
    else:
        books = VisitItem.query.filter(VisitItem.visit_id == visit,
                                       VisitItem.is_returned == False).all()

        books = [b.serialize() for b in books]

        return jsonify(books)


@app.route('/book-return.json', methods=['POST'])
def return_books():
    """return books from user"""

    book = request.form.get('book-id')

    return_book = VisitItem.query.filter(VisitItem.book_id == book,
                                         VisitItem.is_returned == False).first()

    if return_book is None:
        return "This book has already been returned."

    else:
        return_book.is_returned = True
        db.session.commit()
        return "Book has been returned."



#################################################################
#Helper functions

def make_wildcard(name):
    """Formats request.args result to be wildcard-able"""

    return '%' + name + '%'


def get_return_wildcard(name):
    """Checks to see if there is a request.args and returns string"""

    if request.args.get(name):
        return make_wildcard(request.args.get(name))
    else:
        return ''

    return


def post_return_wildcard(name):
    """Checks to see if there is a request.form and returns string"""

    if request.form.get(name):
        return make_wildcard(request.form.get(name))
    else:
        return ''


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=3000, host='0.0.0.0')