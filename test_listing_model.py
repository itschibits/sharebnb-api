# run tests: python -m unittest test_listing_model.py

# import os
from unittest import TestCase
from models import db, User, Booking, Listing

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


class ListingModelTestCase(TestCase):
    """Test model for listings."""

    def setUp(self):
        """Create test client, add sample data."""

        Booking.query.delete()
        Listing.query.delete()
        User.query.delete()

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

        listing1 = Listing(price="50.00",
                           description="test",
                           location="test",
                           listing_owner=user1.username)

        db.session.add(listing1)
        db.session.commit()

        self.user1 = user1
        self.user1.username = user1.username
        self.user2 = user2
        self.user2.username = user2.username
        self.listing1 = listing1
        self.listing1.id = listing1.id

        self.client = app.test_client()

    def tearDown(self):
        """clean up any fouled transaction"""
        db.session.rollback()

    def test_listing_model(self):
        """Does basic model work?"""

        listing = Listing(price="45.50",
                          description="test2",
                          location="test2",
                          listing_owner=self.user2.username)

        db.session.add(listing)
        db.session.commit()

        self.assertEqual(len(self.user2.listings), 1)
        self.assertIsInstance(listing, Listing)
        self.assertEqual(listing.location, "test2")
        self.assertEqual(len(listing.bookings), 0)
