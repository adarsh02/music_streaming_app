from flask_restful import Resource, Api
from flask import Blueprint, request, jsonify,make_response
from flask_security import login_user, logout_user, login_required, current_user, roles_accepted
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from website.models import Album,User,Artist,Track,artist_track_association,artist_album_association
from website.__init__ import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from flask_security import auth_required, roles_required
from website.auth import token_required
from sqlalchemy import func
import random
from sqlalchemy import Table


albums = Blueprint("albums", __name__)
api = Api(albums)

class AlbumNamesByUser(Resource):
    def get(self, user_id):
        # Query the database to get all albums added by the specified user ID
        albums = Album.query.filter_by(added_by=user_id).all()
        
        # Extract album id and title from the query result
        album_data = [{"id": album.id, "title": album.title} for album in albums]

        return make_response(jsonify(album_data))

api.add_resource(AlbumNamesByUser, '/user/<int:user_id>')

class AllAlbumNames(Resource):
    def get(self):
        # Query the database to get all albums
        albums = Album.query.all()
        
        # Extract album id and title from the query result
        album_data = [{"id": album.id, "title": album.title} for album in albums]

        return make_response(jsonify(album_data))

api.add_resource(AllAlbumNames, '/albums')

class CreateAlbum(Resource):
    def post(self):
        try:
            # Parse request data
            data = request.json
            user_id = data.get('user_id')
            artist_id = data.get('artist_id')
            album_title = data.get('album_title')

            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Check if the artist exists
            artist = Artist.query.get(artist_id)
            if not artist:
                return jsonify({'error': 'Artist not found'}), 404

            # Create the album
            album = Album(title=album_title, added_by=user_id)

            # Add the album to the database session
            db.session.add(album)
            db.session.commit()

            # Associate the album with the artist
            artist_album_association_entry = artist_album_association.insert().values(artist_id=artist_id, album_id=album.id)
            db.session.execute(artist_album_association_entry)
            db.session.commit()

            return make_response(jsonify({'message': 'Album created successfully'}), 201)
        except Exception as e:
            # Handle exceptions
            return make_response(jsonify({'error': str(e)}), 500)


api.add_resource(CreateAlbum, '/create')

class EditAlbum(Resource):
    def put(self, album_id):
        try:
            # Parse request data
            data = request.json
            new_album_title = data.get('new_album_title')
            artist_id = data.get('artist_id')

            # Check if album exists
            album = Album.query.get(album_id)
            if not album:
                return jsonify({'error': 'Album not found'}), 404

            # Check if artist exists
            artist = Artist.query.get(artist_id)
            if not artist:
                return jsonify({'error': 'Artist not found'}), 404

            # Update the album title
            album.title = new_album_title

            # Update artist_album_association entry
            artist_album_assoc = Table('artist_album_association', db.metadata, autoload=True, autoload_with=db.engine)
            stmt = artist_album_assoc.update().where(artist_album_assoc.c.album_id == album_id).values(artist_id=artist_id)
            db.session.execute(stmt)

            # Commit changes to the database
            db.session.commit()

            return make_response(jsonify({'message': 'Album name and artist updated successfully'}), 200)
        except Exception as e:
            # Handle exceptions
            return make_response(jsonify({'error': str(e)}), 500)
api.add_resource(EditAlbum, '/edit/<int:album_id>')

class DeleteAlbum(Resource):
    def delete(self, album_id):
        try:
            # Check if the album exists
            album = Album.query.get(album_id)
            if not album:
                return make_response(jsonify({'error': 'Album not found'}), 404)

            # Delete the album from the artist_album_association table
            db.session.execute(artist_album_association.delete().where(artist_album_association.c.album_id == album_id))

            # Delete all tracks associated with the album
            for track in album.tracks:
                # Remove associations of the track with artists from artist_track_association table
                db.session.execute(artist_track_association.delete().where(artist_track_association.c.track_id == track.id))
                # Delete the track
                db.session.delete(track)

            # Commit changes to the database
            db.session.commit()

            # Delete the album
            db.session.delete(album)
            db.session.commit()

            return make_response(jsonify({'message': 'Album and associated tracks deleted successfully'}), 200)
        except Exception as e:
            # Handle exceptions
            return make_response(jsonify({'error': str(e)}), 500)

api.add_resource(DeleteAlbum, '/delete/<int:album_id>')

class AddSong(Resource):
    def post(self):
        try:
            data = request.json
            title = data.get('title')
            genre = data.get('genre')
            language = data.get('language')
            lyrics = data.get('lyrics')
            album_id = data.get('album_id')
            added_by = data.get('added_by')
            artist_id = data.get('artist_id')

            # Fetch the highest track number for the given album
            highest_track_number = db.session.query(func.max(Track.track_number)).filter(Track.album_id == album_id).scalar()

            # Increment the highest track number by 1 to determine the next track number
            if highest_track_number is None:
                track_number = 1
            else:
                track_number = highest_track_number + 1

            # Get a list of valid file paths from the track table
            valid_file_paths = db.session.query(Track.file_path).filter(Track.file_path.isnot(None)).all()

            # Choose a random file path from the list
            chosen_file_path = random.choice(valid_file_paths)[0] if valid_file_paths else None

            # Create the new song entry with average rating set to 0 and randomly chosen file path
            new_song = Track(
                title=title,
                genre=genre,
                language=language,
                lyrics=lyrics,
                album_id=album_id,
                track_number=track_number,
                added_by=added_by,
                average_rating=0,  # Set average rating to 0
                file_path=chosen_file_path  # Assign randomly chosen file path
            )
            db.session.add(new_song)
            db.session.commit()

            # Update the Artist-Track association table
            if artist_id:
                new_artist_track_association = artist_track_association.insert().values(artist_id=artist_id, track_id=new_song.id)
                db.session.execute(new_artist_track_association)
                db.session.commit()

            return make_response(jsonify({'message': 'Song updated successfully'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)
api.add_resource(AddSong, '/add-song')

class EditSong(Resource):
    @token_required
    def put(self, song_id):
        try:
            data = request.json
            

            # Retrieve the song object from the database
            song = Track.query.get(song_id)

            if not song:
                return make_response(jsonify({'error': 'Song not found'}), 404)

            # Update the song attributes with the new data
            song.title = data.get('title', song.title)
            song.genre = data.get('genre', song.genre)
            song.language = data.get('language', song.language)
            song.lyrics = data.get('lyrics', song.lyrics)
            song.added_by = data.get('added_by', song.added_by)
            new_artist_id = data.get('artist_id')  # Get the new artist_id from JSON data

            # Commit the changes to the database
            db.session.commit()

            # Update the artist_track_association table
            if new_artist_id:
                # Remove existing associations for this song
                db.session.execute(artist_track_association.delete().where(artist_track_association.c.track_id == song.id))
                # Create a new association with the provided artist_id
                new_association = artist_track_association.insert().values(artist_id=new_artist_id, track_id=song.id)
                db.session.execute(new_association)

            db.session.commit()

            return make_response(jsonify({'message': 'Song updated successfully'}), 200)
        except Exception as e:
            error_message = 'An error occurred while updating the song.'
            # Log the actual exception for debugging purposes
            print(e)
            return make_response(jsonify({'error': error_message}), 500)

            

# Add the endpoint to the API
api.add_resource(EditSong, '/edit-song/<int:song_id>')


