"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/register', methods = ['GET', 'POST'])
def register_form():
    """Email address, password registration form."""
    
    if request.method == 'GET':
        return render_template("registration_form.html")

    else:
        user_email = request.form.get("email")
        user_password = request.form.get("password")

        user_list = db.session.query(User.email).all()

        if user_email not in user_list:
            new_user = User(email = user_email, password = user_password)
            db.session.add(new_user)
            db.session.commit()
            
        return redirect("/")

@app.route('/login')
def login():
    """Login Page."""
    
    return render_template("login.html")

@app.route('/logged-in', methods = ['POST'])
def logged_in():
    """Logged in or not"""

    username = request.form.get("user_id")
    password = request.form.get("password")

    user_check = User.query.filter(User.email == username, User.password == password).all()
    
    if user_check:
        session['user'] = username
        print(session['user'])
        flash("You have successfully logged in!")
        return redirect("/user-details")


@app.route('/logout')
def logout():
    """Logged out"""

    session = {}
    flash("Logged out!")
    return redirect("/")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/user-details/<user_id>')
def user_details(user_id):
    """Get user details"""
    
    user_detail = Rating.query.get(user_id)
    person = user_detail.user
    person_movie = user_detail.movie

    return render_template("user_details.html", 
                            age = person.age,
                            zipcode = person.zipcode,
                            movies = person_movie.title)




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
