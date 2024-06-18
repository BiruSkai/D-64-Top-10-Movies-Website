from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired, NumberRange
import os
from dotenv import load_dotenv  # pip install python-dotenv
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

ERROR = False
secret = load_dotenv("D:\project coding 1.1.2024\.env.txt")
API_KEY_TMDB = os.getenv("API_KEY_TMDB")
GET_MOVIE_URL = "https://api.themoviedb.org/3/search/movie"


def data_add_movie(query, adult, language, page, release_year, region):
    global GET_MOVIE_URL

    params = {
        "query": query,
        "include_adult": adult,
        "language": language,
        "page": page,
        "primary_release_year": release_year,
        "region": region
    }

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwM2VkNDllYjZlNzIzZjFjNTk4YTM1MGQ4ZGM1MjVjNyIsInN1YiI6IjYzZjlkZjk0ODRmMjQ5MDBhOTQxMmQyOCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.oYCYmiQiyGXJaTP9tD-G8WzmGpMunzKWVZz55ilHi-0"
    }

    data = requests.get(GET_MOVIE_URL, headers=headers, params=params).json()
    fetch_movies = data["results"]
    return fetch_movies


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-movie-list.db"
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Create the extension
db = SQLAlchemy(model_class=Base)

# Initialize the app with the extension
db.init_app(app)


# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    year: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String)
    rating: Mapped[float] = mapped_column(Float)
    ranking: Mapped[int] = mapped_column(Integer)
    review: Mapped[str] = mapped_column(String)
    img_url: Mapped[str] = mapped_column(String)


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()

# Once run, it is commented out to avoid error
# with app.app_context():
#     new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )

    # second_movie = Movie(
    #     title="Avatar The Way of Water",
    #     year=2022,
    #     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
    #     rating=7.3,
    #     ranking=9,
    #     review="I liked the water.",
    #     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
    # )
    # db.session.add(second_movie)
    # db.session.commit()


class EditForm(FlaskForm):
    rating = FloatField(label="Your Rating out of 10, e.g 7.5", validators=[DataRequired(), NumberRange(min=0, max=10, message="Number 1 to 5")])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Updating")


class AddForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    include_adult = BooleanField(label="include_adult", validators=[DataRequired()])
    language = SelectField(label="language", choices=["en-US", "en-AU", "en-UK"], validators=[DataRequired()])
    release_year = StringField(label="release_year", validators=[DataRequired()])
    page = IntegerField(label="page", validators=[DataRequired(), NumberRange(min=1, max=5, message="Number 1 to 5")])
    region = SelectField(label="region", choices=["us", "uk", "au"], validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


@app.route("/")
def home():
    movies = db.session.execute(db.select(Movie).order_by(Movie.title)).scalars()
    return render_template("index.html", movies=movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    global ERROR
    edit_form = EditForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if request.method == "POST":
        if edit_form.validate_on_submit():
            rating = edit_form.rating.data
            review = edit_form.review.data
            with app.app_context():
                movie.rating = rating
                movie.review = review
                db.session.commit()
            return redirect(url_for('home'))
        else:
            ERROR = True
            return render_template("edit.html", form=edit_form, movie=movie, error=ERROR)

    elif request.method == "GET":
        ERROR = False
        return render_template("edit.html", form=edit_form, movie=movie, error=ERROR)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    global ERROR
    add_form = AddForm()
    if request.method == "POST":
        if add_form.validate_on_submit():
            ERROR = False
            title = add_form.title.data
            include_adult = add_form.include_adult.data
            release_year = add_form.release_year.data
            language = add_form.language.data
            page = add_form.page.data
            region = add_form.region.data

            searched_movies = data_add_movie(
                query=title,
                adult= include_adult,
                release_year=release_year,
                language=language,
                page=page,
                region=region
            )
            print(len(searched_movies))
            return render_template("select.html", movies=searched_movies)
        else:
            ERROR = True
            return render_template("add.html", form=add_form, error=ERROR)
    return render_template("add.html", form=add_form)


if __name__ == '__main__':
    app.run(debug=True)
