from datetime import time
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS, cross_origin
import json
from sqlalchemy.exc import IntegrityError
# from flask_json_schema import JsonSchema, JsonValidationError
from models import Listing_Photo, db, connect_db, User, Listing, Booking, Message
from project_secrets import SECRET_KEY
from aws import upload_file_s3


CURR_USER_KEY = "curr_user"

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sharebnb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = SECRET_KEY

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


######################################################################
# User signup/login endpoints

@app.route('/signup', methods=["POST"])
@cross_origin()
def signup():
    """Handle user signup
    Takes signup form data and creates new user in DB
    returns token or error message"""

    output = "no photo"
    if "file" not in request.files:
        print("No file key in request.files")

    signup_data = dict(request.form)
    # use schema validator and return error if invalid

    if "file" in request.files:
        photo = request.files["file"]
        photo.filename = secure_filename(photo.filename)
        output = upload_file_s3(photo)
    try:
        new_user = User.signup(signup_data["username"],
                               signup_data["email"],
                               signup_data["password"],
                               signup_data["bio"],
                               signup_data["location"],
                               output
                               )
        db.session.commit()
        token = User.get_token(new_user.username)
        return jsonify({"token": token}), 201
    except IntegrityError:
        # TODO: figure out how to only keep an image on s3 if signup successful
        # client.delete_object(Bucket=BUCKET_NAME, Key=output)
        return jsonify({'error': 'Same user exists'})


@app.route('/login', methods=["POST"])
@cross_origin()
def login():
    """Handle user login
    Takes login form data (username and password)
    returns token or error message"""
    username = request.json["username"]
    password = request.json["password"]
    user = User.authenticate(username,
                             password)
    if user:
        token = User.get_token(user.username)
        return jsonify({"token": token}), 201

    return jsonify({'error': 'Login unsuccessful'})

######################################################################
# Listing Endpoints


@app.route('/listings', methods=["GET"])
# Gets all listings, TODO: add query params
def send_listings():
    """gets all listings from database and returns it"""
    # max_price = request.args.get('max_price') or 0
    # location = request.args.get('location')

    listings = Listing.query.all()

    return jsonify(json.dumps(listings))


@app.route('/listings/new', methods=["POST"])
def add_listing():
    """add a new listing"""

    listing_data = dict(request.form)

    output = "no photo"

    if "photo" in request.files:
        photo = request.files["photo"]
        photo.filename = secure_filename(photo.filename)
        output = upload_file_s3(photo)

    new_listing = Listing(price=listing_data["price"],
                          title=listing_data["title"],
                          description=listing_data["description"],
                          location=listing_data["location"],
                          listing_owner=listing_data["username"])

    db.session.add(new_listing)
    db.session.commit()

    new_photo = Listing_Photo(listing_id=new_listing.id,
                              image_url=output)

    db.session.add(new_photo)
    db.session.commit()

    listing_info = Listing.query.get(new_listing.id)

    return jsonify(listing_info.serialize())
