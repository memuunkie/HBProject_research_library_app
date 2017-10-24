from jinja2 import StrictUndefined

from flask import jsonify
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)

from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import and_, or_

from model import Book, User, Visit, VisitItem, Appt
from model import connect_to_db, db

from integrate import show_events_python, get_credentials

from datetime import datetime

import os


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABCItseasyas123orsimpleasDo-Re-MiABC123babyyouandmegirl"

app.jinja_env.undefined = StrictUndefined

ADMIN = int(os.environ['LIBRAY_ADMIN_CODE'])
USER = int(os.environ['LIBRAY_USER_CODE'])


@app.route('/')
def index():
    """Home"""

    # print session
    # print type(session['type']), type(session['user'])

    if session.get('user'):
        if session['type'] == ADMIN:
            return redirect('/library')
        else:
            return redirect('/user')
    else:
        return render_template("home.html")


@app.route('/library')
def library_view():
    """render the librarian view"""

    if session.get('user'):
        if session['type'] == ADMIN:
            return render_template('library_view.html')
        else:
            return redirect('/user')            
    else:
        return redirect('/')


@app.route('/user')
def user_view():
    """render the user view"""

    if session.get('user'):
        if session['type'] == USER:
            user_id = session['user']
            user = User.query.filter_by(user_id=user_id).first()
            visits = Visit.query.filter(Visit.user_id == user_id).order_by(Visit.visit_timeout.desc()).all()
            return render_template('user_detail.html', user=user,
                                    visits=visits)
        else:
            return redirect('/library')
    else:
        return redirect('/')


@app.route('/library_events')
def render_events():
    """render the calendar page"""

    events = get_event_data()

    user_type = session['type']

    if user_type == ADMIN:
        user = 'ADMIN'
    else:
        user = 'USER'

    return render_template('library_events.html', events=events, user=user) 


@app.route('/log-out', methods=['GET'])
def log_out():
    """Log out user"""

    if session.get('user'):
        del session['user']
        del session['type']
        print session
        return redirect('/')


@app.route('/create-event', methods=['GET'])
def add_event_to_calendar():
    """Add new event to calendar"""

    return redirect('/library_events')


#Everything below are for AJAX calls 
###############################################################
@app.route('/display-visitors')
def display_visitors():
    """List of current visitors"""
    # used on JS getCurrentVistors
    # library html btn "display-visits"

    visits = db.session.query(Visit).filter(Visit.visit_timeout==None).all()

    all_visits = []

    for visit in visits:
        x = visit.user.serialize()
        x.update(visit.serialize())
        all_visits.append(x)

    return jsonify(all_visits)


@app.route('/display-appts')
def get_appt_requests():

    confirm_appts()

    appts = Appt.query.filter(Appt.is_confirmed == False).all()

    all_appts = []

    if len(appts) > 0:
        for appt in appts:
            x = appt.user.serialize()
            x.update(appt.serialize())
            all_appts.append(x)
        print jsonify(all_appts)
        return jsonify(all_appts)
    else:
        return "No appointment requests"


@app.route('/find-users.json', methods=['GET'])
def find_user():
    """Do a search of user and return a list of possible matches"""
    # used on JS showUserResults
    # library html form "user-search"

    email = get_return_wildcard('email')
    fname = get_return_wildcard('fname')
    lname = get_return_wildcard('lname')

    users = User.query.filter(or_(User.email.ilike(email), 
                                    User.fname.ilike(fname), 
                                    User.lname.ilike(lname))).all()

    if email == '' and fname == '' and lname == '':

        return jsonify([])

    elif len(users) == 0:

        return "No such user is registered."

    else:
        users = [u.serialize() for u in users]

        return jsonify(users)


@app.route('/add-user.json', methods=['POST'])
def add_user():
    """Add a new user"""
    # used on JS registerUser
    # library html form "add-user"

    email = request.form.get('email')
    fname = (request.form.get('fname')).capitalize()
    lname = (request.form.get('lname')).capitalize()
    usertype = request.form.get('type')

    user = User.query.filter(User.email.ilike(email)).first()

    my_test = User.query.filter(User.user_id == 1001).first()

    if user is None:
        if usertype == 'admin':
            type_id = 2
            new_user = User(email=email, fname=fname, lname=lname,
                            password='chang3@dminCHSpswd', type_id=type_id,
                            create_date=datetime.now())
        else:
            new_user = User(email=email, fname=fname, lname=lname,
                            password='1234abc', 
                            create_date=datetime.now())
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter(User.email == email).first()
        return jsonify(user.serialize())
        print user
    else:
        return "This email is already registered."


@app.route('/new-visit.json', methods=['POST'])
def add_new_visit():
    """Add a Visit to the database"""
    # sub-AJAX on addUserResults
    # library - rendered with results

    user = request.form.get('user-id')
    admin = session['user']

    has_visit = db.session.query(Visit).filter(Visit.user_id == user,
                                               Visit.visit_timeout == None).first()

    if has_visit is None:
        visit = Visit(user_id=user, admin_id=admin, 
                      visit_timein=datetime.now())

        db.session.add(visit)
        db.session.commit()

        return "User has been checked in"
    else:
        return "USER ALREADY CHECKED IN"


@app.route('/log-in.json', methods=['POST'])
def log_in_user():
    """Login an existing user"""
    # used on JS loginUser
    # home html form "log-in"

    email = request.form.get('email')
    password = request.form.get('password')

    user = db.session.query(User).filter(User.email == email, 
                                         User.password == password).first()

    if user is None:
        print 'No such user'
        return 'None'
    else:
        session['user'] = user.user_id
        session['type'] = user.type_id

        print session
        return jsonify(user.serialize())


@app.route('/checkout.json', methods=['POST'])
def checkout_user():
    """Checkout user"""
    # sub-AJAX on displayCurrentVisitors
    # library - rendered with current visitors

    visit_id = request.form.get('visit-id')

    visit = db.session.query(Visit).filter(Visit.visit_id==visit_id,
                                        Visit.visit_timeout == None).first()

    items = db.session.query(VisitItem).filter(VisitItem.visit_id == visit_id,
                                               VisitItem.is_returned == False).all()

    if len(items) == 0:
        visit.visit_timeout = datetime.now()

        db.session.commit()

        print "User", visit.user_id, "has been checked out"
        return jsonify(visit.serialize())

    else:
        return 'None'


@app.route('/find-books.json', methods=['GET'])
def find_book():
    """Do a search on books and return a list of matches"""
    # used on JS displayBookResults
    # book_search html form "book-search"


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
    # sub-AJAX on displayBookResults
    # book_search - rendered with book results

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
    # sub-AJAX on displayCurrentVisitors
    # library - rendered with current visitors

    user = request.args.get('visit-id')

    visit = Visit.query.filter(Visit.visit_id == user,
                               Visit.visit_timeout == None).first()

    return render_template('book_search.html', visit=visit)


@app.route('/return-book', methods=['GET'])
def checked_books():
    """outstanding books from user"""
    # sub-AJAX on displayCurrentVisitors
    # library - rendered with current visitors

    user = request.args.get('visit-id')

    visit = Visit.query.filter(Visit.visit_id == user,
                               Visit.visit_timeout == None).first()

    visit_items = VisitItem.query.filter(VisitItem.visit_id == visit.visit_id,
                                         VisitItem.is_returned == False).all()

    return render_template('return_books.html', visit=visit, visit_items=visit_items)


@app.route('/show-books.json', methods=['GET'])
def show_outstanding():
    """show all the outstanding books"""
    # autocalled on JS getOutstandingBooks
    # book_search & return_books html

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
    # sub-AJAX on getOutstandingBooks
    # book_search & return_books html

    book = request.form.get('book-id')

    return_book = VisitItem.query.filter(VisitItem.book_id == book,
                                         VisitItem.is_returned == False).first()

    if return_book is None:
        return "This book has already been returned."

    else:
        return_book.is_returned = True
        db.session.commit()
        return "Book has been returned."


@app.route('/appointment.json', methods=['GET'])
def make_appt():
    """send an appointment request from user"""

    appt_link = request.args.get('appt')
    user = session['user']

    any_appts = Appt.query.filter(Appt.user_id == user, 
                                  Appt.is_confirmed == False).all()

    if len(any_appts) > 0:
        return "You already have a pending appointment request."
    else:
        new_appt = Appt(user_id=user, appt_link=appt_link)
        db.session.add(new_appt)
        db.session.commit()
        return "Your appointment request has been sent."



#################################################################
#Helper functions

def formatDatetime(value, format='%m/%d/%Y at %H:%M'):
    """Formats datetime on Jinja"""
    return value.strftime(format)


def formatUnicodeDatetime(date_string):
    """Format unicode to datetime"""
    date = date_string

    year, month, day, time, utc = date[:4], date[5:7], date[8:10], date[11:16], date[-6]


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


def get_event_data():
    """Returns a dictionary of the event data"""

    events = show_events_python()

    all_events = []

    if events:
        for event in events:
            if 'transparency' in event:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                title = event['summary']
                event_id = event['id']
                link = event['htmlLink']
                all_events.append({'event_id': event_id, 'title': title,
                                'start': start, 'end': end, 'htmlLink': link})
            else:
                title = event['summary']
                print title, "Is taken"

    return all_events


def confirm_appts():
    """Mark appt records as confirmed in DB"""

    events = show_events_python()

    if events:
        for event in events:
            appt = db.session.query(Appt).filter(Appt.appt_link == event['htmlLink']).first() 
            if 'transparency' not in event and appt:
                appt.is_confirmed = True
                db.session.commit()


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = False
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode
    # add formatDatetime to Jinja template
    app.jinja_env.filters['formatDatetime'] = formatDatetime


    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    app.run(port=5000, host='0.0.0.0')