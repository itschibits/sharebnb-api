"""Message model tests"""

# run tests: python -m unittest test_message_model.py

import os
from unittest import TestCase
from models import db, User, Message

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


class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

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

        message1 = Message(text="test",
                           to_user=user1.username,
                           from_user=user2.username)
        db.session.add(message1)
        db.session.commit()

        self.user1 = user1
        self.user1.username = user1.username
        self.user2 = user2
        self.user2.username = user2.username
        self.message1 = message1
        self.message1.id = message1.id

        self.client = app.test_client()

    def tearDown(self):
        """clean up any fouled transaction"""
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        message = Message(text="test2", to_user=self.user2.username, from_user=self.user1.username)

        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.user2.messages), 2)
        self.assertIsInstance(message, Message)
        self.assertEqual(message.text, "test2")
