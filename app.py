from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS, cross_origin
from sqlalchemy.exc import IntegrityError
# from flask_json_schema import JsonSchema, JsonValidationError
import boto3
import uuid
from models import db, connect_db, User, Listing, Booking, Message
from project_secrets import SECRET_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME


CURR_USER_KEY = "curr_user"

app = Flask(__name__)
CORS(app)

client = boto3.client(
                    's3',
                    aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY
                    )

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sharebnb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = SECRET_KEY

S3_LOCATION = f'https://{BUCKET_NAME}.s3.amazonaws.com/'

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


######################################################################
# User signup/login/logout

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
    login_data = dict(request.form)
    try:
        user = User.login(login_data["username"],
                          login_data["password"])
        token = User.get_token(user.username)
        return jsonify({"token": token}), 201
    except False:
        return jsonify({'error': 'Login unsuccessful'})


# ###################################file upload###################

# TODO: move this to helper file
def upload_file_s3(file, acl="public-read"):
    try:
        client.upload_fileobj(
            file,
            BUCKET_NAME,
            f'{uuid.uuid4()}_{file.filename}',
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("File upload didn't work", e)
        return e

    # should return the new img url
    return "{}{}".format(S3_LOCATION, file.filename)
