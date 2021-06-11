import jwt
# from app import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
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

    title = db.Column(
        db.Text,
        nullable=False,
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

    listing_owner = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
    )

    bookings = db.relationship('Booking', order_by='Booking.timestamp.desc()')

    photos = db.relationship('Listing_Photo', order_by='Listing_Photo.id')

    def serialize(self):
        """serialize data, currently assuming only one photo"""
        return {
            "id": self.id,
            "title": self.title,
            "price": str(self.price),
            "description": self.description,
            "location": self.location,
            "listing_owner": self.listing_owner,
            "photos": [photo.serialize() for photo in self.photos],
        }


class Listing_Photo(db.Model):
    """store multiple photos per listing"""

    __tablename__ = 'listing_photos'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    listing_id = db.Column(
        db.Integer,
        db.ForeignKey('listings.id', ondelete='CASCADE'),
    )

    image_url = db.Column(
        db.Text,
        nullable=False
    )

    listing = db.relationship('Listing')

    def serialize(self):
        """serialize data"""
        return {
            "id": self.id,
            "listing_id": self.listing_id,
            "image_url": self.image_url,
        }


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
        default="No bio yet"
    )

    location = db.Column(
        db.Text,
        nullable=True,
        default="No location yet"
    )

    # TODO: add link to default image
    image_url = db.Column(
        db.Text,
        nullable=True,
    )

    messages_sent = db.relationship('Message',
                                    primaryjoin='User.username==Message.from_user_name',
                                    order_by='Message.timestamp.desc()')

    messages_received = db.relationship('Message',
                                        primaryjoin='User.username==Message.to_user_name',
                                        order_by='Message.timestamp.desc()')

    listings = db.relationship('Listing', order_by='Listing.id.desc()')

    bookings = db.relationship('Booking', order_by="Booking.timestamp.desc()")


    @classmethod
    def get_token(cls, username):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                # 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
                # 'iat': datetime.datetime.utcnow(),
                'username': username
            }
            return jwt.encode(
                payload,
                'meow',
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @classmethod
    def signup(cls, username, email, password, bio, location, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        try:
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

        except IntegrityError as e:
            return e

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
        return f'<User #{self.username}: {self.email}>'


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

    to_user_name = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False,
    )

    from_user_name = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False,
    )

    to_user = db.relationship('User', foreign_keys=[to_user_name])

    from_user = db.relationship('User', foreign_keys=[from_user_name])
