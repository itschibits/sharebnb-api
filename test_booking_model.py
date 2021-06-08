# run tests: python -m unittest test_booking_model.py

import os
from unittest import TestCase
from datetime import datetime
from models import db, User, Booking, Listing

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///sharebnb-test"

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class BookingModelTestCase(TestCase):
    """Test model for bookings."""

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
                           owner=user1.username)

        db.session.add(listing1)
        db.session.commit()

        self.user1 = user1
        self.user1.username = user1.username
        self.user2 = user2
        self.user2.username = user2.username
        self.listing1 = listing1
        self.listing1.id = listing1.id

        booking1 = Booking(renter_username="testuser1",
                           listing_id=listing1.id,
                           start_date=datetime(2021, 10, 31),
                           end_date=datetime(2021, 11, 5),
                           total_price="400.00")

        db.session.add(booking1)
        db.session.commit()

        self.booking1 = booking1
        self.booking1.id = booking1.id

        self.client = app.test_client()

    def tearDown(self):
        """clean up any fouled transaction"""
        db.session.rollback()

    def test_booking_model(self):
        """Does basic model work?"""

        booking = Booking(renter_username="testuser2",
                          listing_id=self.listing1.id,
                          start_date=datetime(2025, 10, 31),
                          end_date=datetime(2026, 11, 5),
                          total_price="40000.00")

        db.session.add(booking)
        db.session.commit()

        self.assertEqual(len(self.user2.bookings), 1)
        self.assertIsInstance(booking, Booking)
        self.assertEqual(booking.total_price, "40000.00")
        self.assertEqual(booking.renter, "testuser2")
        self.assertEqual(booking.listing.id, self.listing1.id)
