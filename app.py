from flask import Flask, request, redirect, render_template
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from hashids import Hashids, _hash
from models import URL
from db import db
from dotenv import load_dotenv
import os

load_dotenv()
HASHID_SALT = os.getenv("HASHID_SALT")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "my-secret-key"
db.init_app(app)
hashids = Hashids(min_length = 6, salt = HASHID_SALT)

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        original_url = request.form.get("original_url")
        existing_url = URL.query.filter_by(original_url = original_url).first()
        if existing_url:
            short_url = hashids.encode(existing_url.id)
            flash("URL already exists","info")
            return render_template("index.html", short_url=request.host_url+short_url)
        if original_url:
            new_url = URL(original_url = original_url)
            db.session.add(new_url)
            db.session.commit()
            short_url = hashids.encode(new_url.id)
            return render_template("index.html", short_url=request.host_url+short_url)
    return render_template("index.html")

@app.route("/<short_url>")
def redirect_url(short_url):
    try:
        url_id = hashids.decode(short_url)[0]
        url = URL.query.get(url_id)
        if url:
            return redirect(url.original_url)
        else:
            return "URL not found", 404
    except IndexError:
        return "Invalid URL", 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
