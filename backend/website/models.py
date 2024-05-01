
from sqlalchemy.sql import func
from datetime import datetime

from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=False)
    fs_uniquifier = db.Column(db.String(64), unique=True)
    playlists = db.relationship('Playlist', backref='user', lazy=True)
    flags = db.relationship('Flag', backref='user', lazy=True)
    history = db.relationship('UserHistory', backref='user', lazy=True)
    logins = db.relationship('UserLogin', backref='user', lazy=True)
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

# Artist Model
# ArtistAlbumAssociation Table for Many-to-Many relationship between Artist and Album
artist_album_association = db.Table(
    'artist_album_association',
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
    db.Column('album_id', db.Integer, db.ForeignKey('album.id'), primary_key=True)
)

# ArtistTrackAssociation Table for Many-to-Many relationship between Artist and Track
artist_track_association = db.Table(
    'artist_track_association',
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
    db.Column('track_id', db.Integer, db.ForeignKey('track.id'), primary_key=True)
)

# Artist Model
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    albums = db.relationship('Album', secondary=artist_album_association, backref='artists', lazy=True)
    tracks = db.relationship('Track', secondary=artist_track_association, backref='artists', lazy=True)

# Album Model
# Album Model
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    tracks = db.relationship('Track', backref='album', lazy=True, order_by='Track.track_number', cascade="all, delete-orphan")
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_flagged = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    

# Track Model
class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(50))
    language = db.Column(db.String(50))
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    track_number = db.Column(db.Integer, nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_flagged = db.Column(db.Boolean, default=False)
    stream_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float)
    lyrics = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)
    ratings = db.relationship('UserRating', backref='track', lazy=True, cascade="all, delete-orphan")


# Like Model
class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=False)
    flagged_time = db.Column(db.DateTime, default=datetime.utcnow)

# Playlist Model
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    tracks = db.relationship('PlaylistTrack', backref='playlist', lazy=True, order_by='PlaylistTrack.track_order')

# Association Table for Many-to-Many relationship between Playlist and Track
class PlaylistTrack(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'), primary_key=True)
    track_order = db.Column(db.Integer, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

class UserHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class UserLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)

# UserRating Model
class UserRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

