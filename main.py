from flask import Flask,render_template
from flask_login import LoginManager, UserMixin, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()



app = Flask(__name__, static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SECRET_KEY"] = "flask server for movies"

DEBUG=os.getenv('DEBUG')

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view= 'login'

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    comments = db.relationship("Comment", back_populates="user", lazy=True)
    favourite_movies = db.relationship("FavouriteMovies", back_populates="user", lazy=True)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), unique=False, nullable=False)
    movie_id=db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user= db.relationship("User", back_populates="comments")

class FavouriteMovies(db.Model):
    __tablename__ = "favourite_movies"
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="favourite_movies")
    created_at = db.Column(db.DateTime, default=datetime.now)    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

with app.app_context():
    db.create_all()

users=[]

@app.route("/")
def index():
    from data import get_popular_movies, get_toprated_movies
    popular_movies = get_popular_movies()
    top_rated_movies= get_toprated_movies()

    fav_movies = []
    if current_user.is_authenticated:
        fav_movies = [movie.movie_id for movie in current_user.favourite_movies]
        print("User favourite movies: ", fav_movies)
    return render_template('index.html', popular_movies=popular_movies,top_rated_movies=top_rated_movies, fav_movies=fav_movies)

@app.route("/movies/<movies_type>")
def movies_list(movies_type):
    from data import get_popular_movies, get_toprated_movies
    from flask import request

    page = request.args.get('page',1)

    if movies_type=='popular':
        movies = get_popular_movies(page)
    elif movies_type =='toprated':
        movies = get_toprated_movies(page)
    else:
        movies = get_popular_movies(page)

    fav_movies = []
    if current_user.is_authenticated:
        fav_movies = [movie.movie_id for movie in current_user.favourite_movies]
        print("User favourite movies: ", fav_movies)
    
    return render_template('movies_list.html',movies=movies, fav_movies=fav_movies)

@app.route('/movies/search')
def search_movies():
    from flask import request
    args=request.args
    print('Url args:', args)
    return 'search'

def search_movies():
    from flask import request

    query = request.args.get("query", "")
    print("Search query:", query)
    movies = search_movies(query)
    return render_template("movies_list.html", movies=movies)

@app.route("/comments/<comment_id>/delete")
@login_required
def delete_comment(comment_id):
    from flask import redirect, request

    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        return "Comment not found. Try again!", 400

    db.session.delete(comment)
    db.session.commit()

    return redirect(request.referrer or "/")

@app.route("/movies/<movie_id>/details",methods=["GET", "POST"] )
def movie_details(movie_id):
    from data import get_movie_details, get_movie_videos, get_recomendation
    from flask import request

    data = get_movie_details(movie_id)
    videos= get_movie_videos(movie_id)
    recomendation= get_recomendation(movie_id)
    video_key=videos[0].get('key')
    from data import get_images_detail
    filtered_videos = [
        video
        for video in videos
        if video.get("type", "") == "Trailer" and video.get("official", False)
    ]
    video_key = filtered_videos[0].get("key")

    images = get_images_detail(movie_id)

    if request.method == "POST":
        content = request.form.get("content")
        comment = Comment(content=content,movie_id=movie_id, user=current_user)
        db.session.add(comment)
        db.session.commit()
        print("Comment conmtent: ", content)

    comments = Comment.query.filter_by(movie_id=movie_id).all()
    return render_template('details.html',movie=data, images=images, video_key=video_key, recomendation=recomendation, comments=comments)




@app.route("/movies/like/<movie_id>")
@login_required
def toggle_favourite_movie(movie_id):
    from flask_login import current_user
    from flask import redirect, request

    fav_movie = FavouriteMovies.query.filter_by(
        movie_id=movie_id, user=current_user
    ).first()
    if fav_movie:
        db.session.delete(fav_movie)
    else:
        fav_movie = FavouriteMovies(movie_id=movie_id, user=current_user)
        db.session.add(fav_movie)

    db.session.commit()
    return redirect(request.referrer or "/")

@app.route("/registration", methods=["GET", "POST"])
def registration():
    from flask import request, redirect
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        email=request.form.get("email")
        if len(password.strip()) < 8:
            return render_template(
                "registration.html",error="Password must be at least 8 characters long"
            )
        if len(username.strip()) < 3:
            return render_template(
                "registration.html",error="Username must be at least 3 characters long"
            )
        

        
        

        if User.query.filter_by(username=username).first():
            return render_template(
                "registration.html", error="Username already exists"
            )
        
        if User.query.filter_by(email=email).first():
            return render_template(
                "registration.html", error="Email already exists"
            )
        
        user=User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("registration.html")
    

@app.route("/login",methods=["GET", "POST"]) 
def login():
    from flask import request, redirect
    from flask_login import login_user

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('login.html', error='User not found')
        if user.password != password:
            return render_template('login.html', error='Incorrect password')
        
        login_user(user)
        return redirect("/")
    

        

        
    return render_template("login.html")


@app.route("/profile")
@login_required
def profile():
    from flask_login import current_user
    from data import get_movie_details

    favourite_movies = [
        get_movie_details(m.movie_id) for m in current_user.favourite_movies
    ]
    return render_template("profile.html", favourite_movies=favourite_movies)


# app.run(debug=DEBUG)