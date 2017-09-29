from jinja2 import StrictUndefined

from flask import jsonify
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)
from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import and_, or_

from model import Book, User, connect_to_db, db
from model import connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

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


@app.route('/search-users.json')
def find_user():
    """Do a search of user and return a list of possible matches"""

    if request.args.get('email'):
        email = '%' + request.args.get('email') + '%'
    else:
        email = ''

    if request.args.get('fname'):
        fname = '%' + request.args.get('fname') + '%'
    else:
        fname = ''

    if request.args.get('lname'):
        lname = '%' + request.args.get('lname') + '%'
    else:
        fname = ''

    user_search = User.query.filter(or_(User.email.ilike(email), 
                                    User.fname.ilike(fname), 
                                    User.lname.ilike(lname))).all()

    print user_search


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')