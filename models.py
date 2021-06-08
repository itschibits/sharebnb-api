from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Listing(db.Model):
    """Information about a listing"""

    __tablename__ = 'listings'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    price = db.Column(
        db.Numeric(9, 2),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    location = db.Column(
        db.Text,
        nullable=False,
    )


class User(db.Model):
    """User in the system"""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    messages = db.relationship('Message', order_by='Message.timestamp.desc()')


class Booking(db.Model):
    """Information on one booking"""

    __tablename__ = 'bookings'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    listing_id = db.Column(
        db.Integer,
        db.ForeignKey('listings.id', ondelete='CASCADE'),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    start_date = db.Column(
        db.DateTime,
        nullable=False,
    )

    end_date = db.Column(
        db.DateTime,
        nullable=False,
    )

    user = db.relationship('User')

    listing = db.relationship('Listing')


class Message(db.Model):
    """Individual message between users"""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String,
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    to_user = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    from_user = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
