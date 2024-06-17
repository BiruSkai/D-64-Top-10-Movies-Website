from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.numeric import FloatField
from wtforms.validators import DataRequired, NumberRange
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

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-movie-list.db"
Bootstrap5(app)

ALL_MOVIES = None


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
    rating = FloatField(label="Your Rating out of 10, e.g 7.5", validators=[DataRequired(), NumberRange(min=0, max=10)])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Updating")

@app.route("/")
def home():
    global ALL_MOVIES
    movies = db.session.execute(db.select(Movie).order_by(Movie.title)).scalars().all()
    ALL_MOVIES = movies
    return render_template("index.html", movies=movies)


@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    global ALL_MOVIES
    edit_form = EditForm()
    if request.method == "POST":
        updated_dict = Movie(
            rating = edit_form.rating.data,
            review = request.form["review"],


        )
        print("updated dict: ", updated_dict.review, updated_dict.rating)
        db.session.add(updated_dict)
        db.session.commit()
        return redirect(url_for('home'))

    if request.method == "GET":
        for movie in ALL_MOVIES:
            if movie.id == index:
                return render_template("edit.html", form=edit_form, movie=movie)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
