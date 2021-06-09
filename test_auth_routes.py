"""Auth routes tests"""

# run tests: python -m unittest test_user_model.py

# import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Booking, Listing

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
# os.environ['DATABASE_URL'] = "postgresql:///sharebnb-test"

from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sharebnb-test'

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users."""

    def test_registration(self):
        """ Test for user registration """
        with self.client:
            response = self.client.post(
                '/signup',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)
