from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sqla_intro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

app.config['SECRET_KEY'] = "meow"

debug = DebugToolbarExtension(app)
