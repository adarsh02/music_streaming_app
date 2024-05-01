# website/auth.py
from flask_restful import Resource, Api
from flask import Blueprint, request, jsonify,make_response
from flask_security import login_user, logout_user, login_required, current_user, roles_accepted
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from website.models import User,Role,UserLogin,Track,Album,Artist,artist_track_association
from website.__init__ import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime,timedelta
from flask_security import auth_required, roles_required,SQLAlchemyUserDatastore
from functools import wraps
import jwt
from sqlalchemy import desc


auth = Blueprint("auth", __name__)
api = Api(auth)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authentication-Token')
        if not token:
            return {'message': 'Token is missing'}, 401

        try:
            data = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
            #current_user = User.query.get(data['user']['id'])
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

        return f(*args, **kwargs)

    return decorated


class CheckExpiry(Resource):
    def get(self):
        token = request.headers.get('Authentication-Token')
        if not token:
            return {'expired': False}, 401

        try:
            data = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {'expired': True}, 401
        except jwt.InvalidTokenError:
            return {'expired': True}, 401

        return {'expired': False}, 200

api.add_resource(CheckExpiry, '/check_expiry')

class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password) and 'user' in [role.name for role in user.roles]:
            user_login = UserLogin(user_id=user.id)
            db.session.add(user_login)
            user_login.login_time = datetime.utcnow()
            db.session.commit()

            # Convert User object to a serializable format
            user_data = {
                "id": user.id,
                "email": user.email,
                "role": user.roles[0].name
                # Add other user properties as needed
            }

            # Generate JWT token
            expiration_date = datetime.utcnow() + timedelta(seconds=30000)
            access_token = jwt.encode({'user': user_data, 'exp': expiration_date}, "your_secret_key")

            response_data = {
                "auth_token": access_token,  # Removed '.decode('UTF-8')'
                "user": user_data
            }

            return make_response(jsonify(response_data), 200)
        else:
            return make_response(jsonify({"message": "Invalid credentials"}), 401)



class UserLogoutResource(Resource):
    @login_required
    def post(self):
        logout_user()
        return jsonify({"message": "User logged out successfully"}), 200

class UserSignUpResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        username = data.get("username")
        password1 = data.get("password1")
        password2 = data.get("password2")

        user = User.query.filter_by(email=email).first()
        if user:
            return make_response(jsonify({"success": False, "message": "Email already exists."}))

        if len(email) < 4:
            return make_response(jsonify({"success": False, "message": "Email must be greater than 3 characters."}))

        if len(username) < 2:
            return make_response(jsonify({"success": False, "message": "First name must be greater than 1 character."}))

        if password1 != password2:
            return make_response(jsonify({"success": False, "message": "Passwords don't match."}))

        if len(password1) < 7:
            return make_response(jsonify({"success": False, "message": "Password must be at least 7 characters."}))

        new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password1, method="sha256"),
                roles=[Role.query.filter_by(name="user").first()],
            )

        try:
            db.session.add(new_user)
            db.session.commit()  # Commit changes before accessing the new_user.id

            user_login = UserLogin(user_id=new_user.id)
            db.session.add(user_login)
            user_login.login_time = datetime.utcnow() 
            db.session.commit()

            # Fetch the user after committing changes
            user = User.query.filter_by(email=email).first()

            # access_token = create_access_token(identity=user.id)
            response_data = {
                "token": user.get_auth_token(),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.roles[0].name
                    # Add other user properties as needed
                },
                "success": True
            }

        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback changes if an error occurs
            response_data = {"message": "Error committing to the database", "success": False}
            print(f"Database error: {e}")

        return make_response(jsonify(response_data), 200)


class AdminLoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(email=email).first()

        if user and user.password == password and 'admin' in [role.name for role in user.roles]:
            user_login = UserLogin(user_id=user.id)
            db.session.add(user_login)
            user_login.login_time = datetime.utcnow()
            db.session.commit()

            # Convert User object to a serializable format
            user_data = {
                "id": user.id,
                "email": user.email,
                "role": user.roles[0].name
                # Add other user properties as needed
            }

            # Generate JWT token
            expiration_date = datetime.utcnow() + timedelta(seconds=30000)
            access_token = jwt.encode({'user': user_data, 'exp': expiration_date}, "your_secret_key")

            response_data = {
                "auth_token": access_token,  # Removed '.decode('UTF-8')'
                "user": user_data
            }

            return make_response(jsonify(response_data), 200)
        else:
            return make_response(jsonify({"message": "Invalid credentials"}), 401)

        
class StatsResource(Resource):
    def get(self):
        try:
            # 1) Total number of users with role == user
            total_users_user_role = User.query.filter(User.roles.any(name='user')).count()

            # 2) Total number of users with role == creator
            total_users_creator_role = User.query.filter(User.roles.any(name='creator')).count()

            # 3) Total number of albums in database
            total_albums = Album.query.count()

            # 4) Top 10 songs with highest stream count across all albums
            top_songs = Track.query \
                .join(artist_track_association, Track.id == artist_track_association.c.track_id) \
                .join(Artist, Artist.id == artist_track_association.c.artist_id) \
                .order_by(Track.stream_count.desc()) \
                .limit(10) \
                .all()

            top_songs_data = [{
                'title': track.title,
                'artist': ', '.join(artist.name for artist in track.artists),
                'album': track.album.title,
                'stream_count': track.stream_count
            } for track in top_songs]

            # 5) Total number of genres and languages of tracks in database
            total_genres = len(set(track.genre for track in Track.query.distinct(Track.genre)))
            total_languages = len(set(track.language for track in Track.query.distinct(Track.language)))

            top_rated_songs = Track.query \
                .filter(Track.average_rating.isnot(None)) \
                .order_by(desc(Track.average_rating)) \
                .limit(10) \
                .all()

            top_rated_songs_data = [{
                'title': track.title,
                'artist': ', '.join(artist.name for artist in track.artists),
                'album': track.album.title,
                'average_rating': track.average_rating
            } for track in top_rated_songs]

        

            # Compile the statistics into a dictionary
            statistics = {
                'total_users_user_role': total_users_user_role,
                'total_users_creator_role': total_users_creator_role,
                'total_albums': total_albums,
                'top_songs': top_songs_data,
                'top_rated_songs': top_rated_songs_data,
                'total_genres': total_genres,
                'total_languages': total_languages,
                
            }

            # Return the statistics as JSON response
            return make_response(jsonify(statistics), 200)
        except Exception as e:
            # Return error message in case of any exceptions
            return make_response(jsonify({'error': str(e)}), 500)
        
class AddArtist(Resource):
    def post(self):
        try:
            # Parse the request JSON data
            data = request.get_json()
            artist_name = data.get('name')
            added_by = data.get('added_by')  # Assuming added_by is provided in the request data

            # Check if the artist name already exists
            existing_artist = Artist.query.filter_by(name=artist_name).first()
            if existing_artist:
                return make_response(jsonify({'error': 'Artist name already exists'}), 409)

            # Create a new artist object
            new_artist = Artist(name=artist_name, added_by=added_by)

            # Add the new artist to the database session
            db.session.add(new_artist)
            db.session.commit()

            return make_response(jsonify({'message': 'Artist added successfully'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)


# Add the resource to the API
api.add_resource(AddArtist, '/add_artist')

# Add the resource to the API
api.add_resource(StatsResource, '/stats')


api.add_resource(UserLoginResource, "/user_login")
api.add_resource(UserLogoutResource, "/user_logout")
api.add_resource(UserSignUpResource, "/sign_up")
api.add_resource(AdminLoginResource, "/admin_login")






