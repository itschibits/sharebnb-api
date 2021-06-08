from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
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

    owner = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
    )

    bookings = db.relationship('Booking', order_by='Booking.timestamp.desc()')


class User(db.Model):
    """User in the system"""

    __tablename__ = "users"

    username = db.Column(
        db.Text,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    bio = db.Column(
        db.Text,
        nullable=True,
    )

    location = db.Column(
        db.Text,
        nullable=True,
    )

    # TODO: add link to default image
    image_url = db.Column(
        db.Text,
        nullable=True,
    )

    messages = db.relationship('Message', order_by='Message.timestamp.desc()')

    listings = db.relationship('Listing', order_by='Listing.id.desc()')

    bookings = db.relationship('Booking', order_by="Booking.timestamp.desc()")

    @classmethod
    def signup(cls, username, email, password, bio, location, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            bio=bio,
            location=location,
            image_url=image_url,
        )

        db.session.add(user)
        # TODO: why not commit here?
        return user

    # TODO: find out what cls is and why we need it...
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    def __repr__(self):
        return f"<User #{self.username}: {self.email}>"


class Booking(db.Model):
    """Information on one booking"""

    __tablename__ = 'bookings'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    renter_username = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
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

    total_price = db.Column(
        db.Numeric(9, 2),
        nullable=False,
    )

    renter = db.relationship('User')

    listing = db.relationship('Listing')


class Message(db.Model):
    """Individual message between users"""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.Text,
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    to_user = db.Column(
        db.Integer,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False,
    )

    from_user = db.Column(
        db.Integer,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False,
    )
