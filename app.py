from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS, cross_origin
from sqlalchemy.exc import IntegrityError
import boto3
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


######################################################################
# User signup/login/logout

"""
1st step: take in form data and hash password
2nd: try to create new user instance, if fail (duplicate username) return error
        if success, return username
3rd: take that username and create token and return token to React
4th:

backend has helper functions:
    createToken() calls User.authenticate, creates token and returns it
    User.authenticate() checks the database for a user with this username and password,
            returns user object (or maybe just True?)
"""


@app.route('/signup', methods=["POST"])
def signup():
    """Handle user signup

    Takes signup form data and creates new user in DB

    returns

    If the there already is a user with that username: return error message"""

    signup_data = request.get_json()
    print("signup_data===========>>>>", signup_data)
    #use schema validator and return error if invalid
    print("signupdata.username=====>", signup_data["username"])

    print("request.files==== ", request.files)
    # if "file" not in request.files:
    #     return "No file key in request.files"

    photo = signup_data["file"]
    photo.filename = secure_filename(photo.filename)
    output = upload_file_s3(photo)
    # maybe deal with MultiDict??
    new_user = User.signup(signup_data["username"],
                           signup_data["email"],
                           signup_data["password"],
                           signup_data["bio"],
                           signup_data["location"],
                           output
                           )
    print("new_user==========", new_user)
    token = User.get_token(new_user.username)
    print("token============", token)

    return jsonify({"token": token}), 201

# ###################################trying to upload files###################


def upload_file_s3(file, acl="public-read"):
    try:
        client.upload_fileobj(
            file,
            BUCKET_NAME,
            file.filename,
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


@app.route("/", methods=['POST'])
@cross_origin()
def upload_file():
    if "file" not in request.files:
        return "No file key in request.files"

    file = request.files["file"]

    if file.filename == "":
        return "Please select a file"

    file.filename = secure_filename(file.filename)
    output = upload_file_s3(file)

    return str(output)
