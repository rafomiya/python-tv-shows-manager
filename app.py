from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# TODO make a docker image for this application

# setting the database url
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)

db = SQLAlchemy(app)


class TvShow(db.Model):
    __tablename__ = "tv_show"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = db.Column(db.String(80), nullable=False)
    release_date = db.Column(db.Date(), nullable=False, default=db.func.now())
    genre = db.Column(db.String(30), nullable=False)
    is_deleted = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return "<TvShow %r>" % self.title


@app.route("/", methods=["GET"])
def index():
    tv_shows = TvShow.query.filter(TvShow.is_deleted == False).order_by(TvShow.release_date).all()

    return render_template("index.html", tv_shows=tv_shows)


@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        tv_show = TvShow(
            title=request.form["title"],
            release_date=request.form["release-date"],
            genre=request.form["genre"],
        )

        try:
            db.session.add(tv_show)
            db.session.commit()

            return redirect("/")

        except:
            return {"error": 'An error occurred while inserting the tv_show in route "/add"'}

    return render_template("add.html")


@app.route("/delete/<uuid:id>", methods=["GET"])
def delete(id):
    tv_show = db.session.query(TvShow).get(id)

    try:
        tv_show.is_deleted = True
        db.session.commit()

        return redirect("/")

    except:
        return {"error": 'An error occurred while deleting the tv_show in route "/delete/<uuid:id>"'}


@app.route("/update/<uuid:id>", methods=["GET", "POST"])
def update(id):
    tv_show = db.session.query(TvShow).get(id)

    if request.method == "POST":
        tv_show.title = request.form["title"]
        tv_show.release_date = request.form["release-date"]
        tv_show.genre = request.form["genre"]

        try:
            db.session.commit()

            return redirect("/")

        except:
            return {"error": 'An error occurred while updating the tv_show in route "/update/<uuid:id>"'}

    return render_template("update.html", tv_show=tv_show)


if __name__ == "__main__":
    app.run(debug=True)
