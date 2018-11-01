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

# Here, we are checking if the user is logged in (session has 'user' key)
    if 'user' in session:
        return render_template("log_in_homepage.html")
    else:
        return render_template("homepage.html")

@app.route('/register', methods = ['GET', 'POST'])
def register_form():
    """Email address, password registration form."""
    
    # Reg form is rendered when you go to page and when it is submitted a post request is 
    # made and if users emails is not in database then it gets added and redirected to the
    # homepage.  
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

    email = request.form.get("email")
    password = request.form.get("password")

    # Checking to see if this email exists in the database. Making a user object.
    user = User.query.filter(User.email == email).one()

    # Checking to see if the password matches for the email provided by the user. 
    user_check = User.query.filter(User.email == email, User.password == password).all()
    
    # If the check works for the email and matching password, user details page is rendered. 
    # Otherwise, the homepage is rendered. 
    if user_check:
        session['user'] = email
        # User id is saved in this varianble.
        user_id = int(user.user_id)
        flash("You have successfully logged in!")
        return redirect(f"user-details/{user_id}")
    else:
        return redirect ("/")

@app.route('/logout')
def logout():
    """Logged out and session cleared."""

# This is how you clear a session. Very important when logging out. 
    session.clear()
    flash("Logged out!")
    return redirect("/")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movies.html", movies=movies)






@app.route("/movie-details/<movie_id>")
def movie_details(movie_id):
    """ Show movie details: release date, imdb url, ratings"""


    #  We are creating a rating object that has a particular movie_id. 
    rating_objs = Rating.query.filter(Rating.movie_id == movie_id).all()
    #  Using relationship between Rating and Movie to create a movie object. 
    #  We use this for displaying movie title and other movie details. 
    rating_obj = Rating.query.filter(Rating.movie_id == movie_id).first()
    movie = rating_obj.movie


    # This info is only displayed if the user is logged in. That's why 
    #  we are checking if 'user' key is in session. 
    ratings = {}

    for rating in rating_objs:
        ratings[rating.user_id] = rating.score

    if 'user' in session:
        # This template says the user is logged in at the top. Different
        # from the template rendered in the else statement. 
        return render_template("log_in_movie_details.html",
                            movie = movie.movie_id,
                            title = movie.title,
                            year = movie.released_at,
                            url = movie.imdb_url,
                            ratings = ratings)
    else:

        return render_template("movie_details.html",
                            movie = movie.movie_id,
                            title = movie.title,
                            year = movie.released_at,
                            url = movie.imdb_url,
                            ratings = ratings)





@app.route('/rate-movie/<movie_id>', methods = ['POST'])
def movie_rated(movie_id):
    """Checks to see if movie already rated and updates the rating"""

    # The below rating is from the database. We are getting it by 
    # using the movie id and using the relationship between Movie 
    # and Rating classes. 
    rating = Rating.query.filter(Rating.movie_id == movie_id).first()
    
    user_rating = request.form.get("movie_rating")
   
    rating.score = user_rating
    
    # The rating obtained from the form on log_in_movie_details:

    # Checking if a rating already exists in the database: 
    db.session.add(rating)
    db.session.commit()

    return render_template("rating_confirmation.html")


@app.route('/user-details/<user_id>')
def user_details(user_id):
    """Get user details"""
    

    # Making a rating object using the user_id from the url.
    rating = Rating.query.filter(Rating.user_id == user_id).first()
    # Made a user object to access user details like age and zipcode. 
    user = rating.user
    # Made a movie object to access movie title.
    movie = rating.movie

    return render_template("user_details.html", 
                            age = user.age,
                            zipcode = user.zipcode,
                            movies = movie.title, 
                            movie_score = rating.score)
   



if __name__ == "__main__":


    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000)
