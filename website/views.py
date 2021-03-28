from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import OMDB
from .models import Movie, User, Rating, db
import requests
import json

views = Blueprint('views', __name__)

@views.route('/')
def cover():
    return render_template("cover.html", user=current_user)

@views.route('/profile')
@login_required
def profile():
    first_name = current_user.first_name
    user_id = current_user.id
    user = User.query.filter_by(id=current_user.id).one()

    movie_ratings = {}
    for rating in user.ratings:
        title = rating.movie.title
        score = rating.score
        movie_ratings[title] = score
    
    print()


    return render_template("profile.html", user=current_user, name=first_name.capitalize(), user_id=user_id, movie_ratings = movie_ratings)

@views.route('/movie_list')
@login_required
def movie_list():
    movies = Movie.query.order_by('title').all()

    return render_template("movie_list.html", user=current_user, movies=movies)

@views.route("/moviedetails/<movie_id>", methods=['GET'])
@login_required
def movie_details(movie_id):
    """Display movie details and allow logged in users to rate"""
    movie = Movie.query.filter_by(movie_id=movie_id).one()
    print(movie.title)

    return render_template("movie_details.html", user=current_user, movie=movie)

@views.route("/moviedetails/<int:movie_id>", methods=['POST'])
@login_required
def rating_handler(movie_id):
    new_rating = int(request.form.get("rating"))
    curr_movie_id = movie_id
    user = User.query.filter_by(id=current_user.id).one()

    for item in user.ratings:
        if curr_movie_id == item.movie_id:
            item.score = new_rating
            flash("Your rating has been updated to %d" % new_rating, category='success')
            db.session.commit()
            print(curr_movie_id)
            return redirect("/moviedetails/%d" % curr_movie_id)

    rating = Rating(movie_id=curr_movie_id, user_id=user.id, score=new_rating)
    flash("Your rating of %d has been added" % new_rating, category='success')
    db.session.add(rating)
    db.session.commit()
    return redirect("/moviedetails/%d" % curr_movie_id)


@views.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        movie_name = request.form.get('search')
        querystring = {"s":movie_name,"r":"json"}
        try:
            response = requests.get(OMDB, params=querystring)
            movies = response.json()['Search']
            
            movie_ids = []
            movie_names = []
            movie_posters = []

            for movie in movies:
                movie_id = movie['imdbID']
                name = movie['Title']
                poster = movie['Poster']
                movie_ids.append(movie_id)
                movie_names.append(name)
                movie_posters.append(poster)
            
            movie_info = zip(movie_ids, movie_names, movie_posters)
            
            return render_template("search.html", user=current_user, movies=movie_info)

        except:
            flash('Movie not found', category='error')
            return render_template("search.html", user=current_user)

    return render_template("search.html", user=current_user)
