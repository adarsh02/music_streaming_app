from flask_restful import Resource, Api,reqparse
from flask import Blueprint, request, jsonify,make_response
from flask_security import login_user, logout_user, login_required, current_user, roles_accepted
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from website.models import Playlist,UserRating,Track,User,UserHistory,Flag,Role,Artist,user_roles
from website.__init__ import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from flask_security import auth_required, roles_required
from website.auth import token_required

user = Blueprint("user", __name__)
api = Api(user)


class GetPlaylists(Resource):
    @token_required
    def get(self, user_id):
        try:
            playlists = Playlist.query.filter_by(user_id=user_id).all()
            playlists_data = [{'id': playlist.id, 'title': playlist.title, 'created_time': playlist.created_time} for playlist in playlists]
            return jsonify({'playlists': playlists_data})
        except Exception as e:
            return jsonify({'error': str(e)})



class CreatePlaylist(Resource):
    @token_required # Use Flask-Security login_required decorator
    def post(self,user_id):
        try:
            data = request.get_json()
            title = data.get('title')

            # Validate title if needed
            if not title:
                return {'error': 'Title is required for playlist creation'}, 400

            new_playlist = Playlist(title=title, user_id=user_id)
            db.session.add(new_playlist)
            db.session.commit()

            return {'message': 'Playlist created successfully'}, 201
        except Exception as e:
            return {'error': str(e)}, 500
        
class GetUserRating(Resource):
    @token_required  # Use Flask-Security login_required decorator
    def get(self, user_id, track_id):
        try:
            user_rating = UserRating.query.filter_by(user_id=user_id, track_id=track_id).first()
            if user_rating:
                return {'rating': user_rating.rating}
            return {'rating': None}, 404
        except Exception as e:
            return {'error': str(e)}, 500


class RateSong(Resource):
    @token_required
    def post(self, user_id, track_id):
        try:
            data = request.get_json()
            rating = data.get('rating')

            # Validate rating if needed
            if rating is None or not (0 <= rating <= 100):
                return {'error': 'Invalid rating value'}, 400

            user_rating = UserRating.query.filter_by(user_id=user_id, track_id=track_id).first()

            if user_rating:
                # Update existing user rating
                user_rating.rating = rating
            else:
                # Create a new user rating
                user_rating = UserRating(user_id=user_id, track_id=track_id, rating=rating)
                db.session.add(user_rating)

            # Calculate average rating for the track
            track = Track.query.get(track_id)
            if track:
                ratings = [user_rating.rating for user_rating in track.ratings]
                average_rating = sum(ratings) / len(ratings) if ratings else 0
                track.average_rating = average_rating

            db.session.commit()

            return {'message': 'Rating updated successfully'}, 201
        except Exception as e:
            return {'error': str(e)}, 500
        

class AddToHistory(Resource):
    @token_required
    def post(self, user_id, track_id):
        try:
            # Check if the user and track exist
            user = User.query.get(user_id)
            track = Track.query.get(track_id)

            if not user or not track:
                return {'error': 'User or track not found'}, 404

            # Add the track to user history
            user_history = UserHistory(user_id=user_id, track_id=track_id, timestamp=datetime.utcnow())
            db.session.add(user_history)

            # Increase the stream count of the track
            track.stream_count += 1

            db.session.commit()

            return {'message': 'Song added to history and stream count increased successfully'}, 201
        except Exception as e:
            return {'error': str(e)}, 500
        

class ToggleFlag(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('track_id', type=int, required=True)
        args = parser.parse_args()

        user_id = args['user_id']
        track_id = args['track_id']

        flag = Flag.query.filter_by(user_id=user_id, track_id=track_id).first()
        if flag:
            db.session.delete(flag)
            db.session.commit()
            return {'message': 'Song unflagged'}, 200
        else:
            new_flag = Flag(user_id=user_id, track_id=track_id)
            db.session.add(new_flag)
            db.session.commit()
            return {'message': 'Song flagged'}, 201

api.add_resource(ToggleFlag, '/toggle_flag')


class GetFlagStatus(Resource):
    def get(self, user_id, track_id):
        flag = Flag.query.filter_by(user_id=user_id, track_id=track_id).first()
        if flag:
            return jsonify({'flagged': True})
        else:
            return jsonify({'flagged': False})
        

class RegisterArtist(Resource):
    @token_required  # Requires authentication
    def post(self):
        try:
            data = request.json
            artist_name = data.get('artist_name')
            user_id = data.get('user_id')

            # Check if the user exists
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Check if the artist name already exists
            existing_artist = Artist.query.filter_by(name=artist_name).first()
            if existing_artist:
                return make_response(jsonify({'error': 'Artist name already exists'}), 409)

            # Add the new artist
            new_artist = Artist(name=artist_name, added_by=user_id)
            db.session.add(new_artist)
            db.session.commit()

            # Get the role_id for "creator" role
            creator_role = Role.query.filter_by(name='creator').first()
            if not creator_role:
                return make_response(jsonify({'error': 'Creator role not found'}), 404)

            # Insert user_id and role_id into user_roles table
            user_role = user_roles.insert().values(user_id=user_id, role_id=creator_role.id)
            db.session.execute(user_role)
            db.session.commit()

            return make_response(jsonify({'message': 'Artist registered successfully'}), 201)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)
        

class ArtistList(Resource):
    def get(self, user_id):
        try:
            # Get all artists added by the specified user_id
            artists = Artist.query.filter_by(added_by=user_id).all()
            # Prepare the response data
            artists_data = [{'id': artist.id, 'name': artist.name} for artist in artists]
            return jsonify(artists_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

api.add_resource(ArtistList, '/artists/<int:user_id>')


class AllArtists(Resource):
    def get(self):
        try:
            # Get all artists
            artists = Artist.query.all()
            # Prepare the response data
            artists_data = [{'id': artist.id, 'name': artist.name} for artist in artists]
            return jsonify(artists_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

api.add_resource(AllArtists, '/artists')
        

class UserRoleList(Resource):
    def get(self, user_id):
        try:
            # Retrieve the user
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Query the roles associated with the user
            roles = (
                Role.query
                .join(user_roles)
                .filter(user_roles.c.user_id == user_id)
                .all()
            )

            # Extract role names from the query result
            role_names = [role.name for role in roles]

            return make_response(jsonify({'user_id': user_id, 'roles': role_names}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)

api.add_resource(UserRoleList, '/<int:user_id>/roles')
        
api.add_resource(GetFlagStatus, '/get_flag_status/<int:user_id>/<int:track_id>')

api.add_resource(AddToHistory, '/user/add-to-history/<int:user_id>/<int:track_id>')

api.add_resource(GetUserRating, '/user-rating/<int:user_id>/<int:track_id>')
api.add_resource(RateSong, '/rate-song/<int:user_id>/<int:track_id>')

api.add_resource(CreatePlaylist, '/create_playlist/<int:user_id>')
api.add_resource(GetPlaylists, '/playlists/<int:user_id>')
api.add_resource(RegisterArtist, '/register/artist')