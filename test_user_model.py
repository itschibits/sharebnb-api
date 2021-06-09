"""User model tests"""

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

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Booking.query.delete()
        Listing.query.delete()

        user1 = User(
            email="testemail@test.com",
            username="testuser1",
            password="TEST_PASSWORD"
        )
        user2 = User(
            email="testemail2@test.com",
            username="testuser2",
            password="TEST_PASSWORD2"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.user1 = user1
        self.user1.username = user1.username
        self.user2 = user2
        self.user2.username = user2.username

        self.client = app.test_client()

    def tearDown(self):
        """clean up any fouled transaction"""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages, no bookings & no listings
        self.assertEqual(len(u.messages_sent), 0)
        self.assertEqual(len(u.messages_received), 0)
        self.assertEqual(len(u.bookings), 0)
        self.assertEqual(len(u.listings), 0)

    def test_repr_method(self):
        """tests that repr method outputs correct information """

        self.assertEqual(repr(self.user1),
                         f"<User #{self.user1.username}: {self.user1.email}>")

    def test_User_signup(self):
        """successfully detects if a unique user can create a new account"""
        new_user = User.signup(username="testuser",
                               email="test@test.com",
                               password="HASHED_PASSWORD",
                               image_url="",
                               bio="hi",
                               location="Mars")
        db.session.commit()

        User.signup(username="testuser",
                    email="test@test.com",
                    password="HASHED_PASSWORD",
                    image_url="",
                    bio="hi",
                    location="Mars")

        with self.assertRaises(IntegrityError):
            db.session.commit()
        self.assertIsInstance(new_user, User)

    def test_User_authenticate(self):
        """successfully detects if an exisiting user can log into Sharebnb"""

        User.signup(username="testuser",
                    email="test@test.com",
                    password="HASHED_PASSWORD",
                    image_url="",
                    bio="hello",
                    location="Norway")

        db.session.commit()

        with self.assertRaises(ValueError):
            User.authenticate(username="testuser1",
                              password="BAD_TEST_PASSWORD")

        self.assertFalse(User.authenticate(username="baduser",
                                           password="TEST_PASSWORD"))

        self.assertTrue(User.authenticate(username="testuser",
                                          password="HASHED_PASSWORD"))
