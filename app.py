from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Listing, Booking, Message

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sharebnb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "meow"

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

	#use schema validator and return error if invalid

	new_user = User.signup({signup_data})
