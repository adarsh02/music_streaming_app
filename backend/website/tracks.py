from flask_restful import Resource, Api,abort
from flask import Blueprint, request, jsonify, make_response
from flask_security import login_required, current_user
from flask_jwt_extended import jwt_required
from website.models import Track, Album,Playlist,PlaylistTrack,artist_track_association,Artist,artist_album_association
from website.__init__ import db
from flask_security import auth_required, roles_required,auth_token_required
from website.auth import token_required
from sqlalchemy.exc import IntegrityError

track = Blueprint("tracks", __name__)
api = Api(track)


class GetAlbumInformation(Resource):
    def get(self):
        try:
            # Query the database to get all albums along with associated artist names
            albums_data = []
            albums = Album.query.all()
            for album in albums:
                artists = db.session.query(Artist.name)\
                    .join(artist_album_association, Artist.id == artist_album_association.c.artist_id)\
                    .filter(artist_album_association.c.album_id == album.id).all()
                artist_names = [artist[0] for artist in artists]
                albums_data.append({
                    "id": album.id,
                    "title": album.title,
                    "artist_names": artist_names
                })

            return make_response(jsonify(albums_data), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)

# Add the resource to the API
api.add_resource(GetAlbumInformation, '/albums')


class GetTracksByAlbum(Resource):
    @token_required  # Require a valid JWT for this route
    def get(self, album_id):
        # Fetch album for the given album_id
        album = Album.query.get(album_id)

        if not album:
            return jsonify({"error": "Album not found"}), 404

        # Fetch tracks for the specific album from the database using SQLAlchemy
        tracks = Track.query.filter_by(album_id=album_id).all()

        # Convert track data to a format suitable for JSON response
        track_data = []
        for track in tracks:
            # Fetch artists associated with the track
            artists = [artist.name for artist in track.artists][0]

            # Calculate average rating for the track
            ratings = [rating.rating for rating in track.ratings]
        
            track_info = {
                "id": track.id,
                "title": track.title,
                "file_path": track.file_path,
                "artist_name": artists,
                "genre":track.genre,
                "language":track.language,
                "stream_count": track.stream_count,
                "average_rating": track.average_rating,
                "track_number": track.track_number,
                "lyrics":track.lyrics,
                "album_name":album.title
            }

            track_data.append(track_info)

        # Convert album object to a dictionary
        album_data = {
            "id": album.id,
            "title": album.title,
            # Include any other album attributes as needed
        }

        # Include album name along with the tracks
        response_data = {
            "album": album_data,
            "tracks": track_data
        }

        return jsonify(response_data)


    

class SearchTracks(Resource):
    def get(self):
        query = request.args.get('query', '')

        # Search for tracks and albums where the name contains the query
        matching_tracks = Track.query.filter(Track.title.ilike(f'%{query}%')).all()
        matching_albums = Album.query.filter(Album.title.ilike(f'%{query}%')).all()

        # If there are no matches, search for tracks and albums where the name starts with the query
        if not matching_tracks:
            matching_tracks = Track.query.filter(Track.title.ilike(f'{query}%')).all()

        if not matching_albums:
            matching_albums = Album.query.filter(Album.title.ilike(f'{query}%')).all()

        # Convert results to dictionaries for JSON response
        tracks_result = [{'id': track.id, 'name': track.title, 'album_name': Album.query.get(track.album_id).title,'album_id':track.album_id} for track in matching_tracks]
        albums_result = [{'id': album.id, 'name': album.title} for album in matching_albums]

        return jsonify({'tracks': tracks_result, 'albums': albums_result})
    
class ToggleTrackInPlaylist(Resource):
    def post(self):
        data = request.get_json()
        playlist_id = data.get('playlist_id')
        track_id = data.get('track_id')

        playlist = Playlist.query.get(playlist_id)
        track = Track.query.get(track_id)

        if playlist and track:
            try:
                if track in playlist.tracks:
                    playlist.tracks.remove(track)
                else:
                    playlist_track = PlaylistTrack(track_id=track.id, track_order=len(playlist.tracks) + 1)
                    playlist.tracks.append(playlist_track)

                db.session.commit()
                return make_response(jsonify({'success': True}), 200)

            except IntegrityError:
                # Handle the case where the track already exists in the playlist
                db.session.rollback()
                return make_response(jsonify({'error': 'Track already exists in the playlist'}), 400)

        else:
            return make_response(jsonify({'error': 'Playlist or Track not found'}), 404)

# API route to check if a track is in a playlist
class CheckTrackInPlaylist(Resource):
    def post(self):
        data = request.get_json()
        playlist_id = data.get('playlist_id')
        track_id = data.get('track_id')

        playlist_track = PlaylistTrack.query.filter_by(playlist_id=playlist_id, track_id=track_id).first()

        if playlist_track:
            return make_response(jsonify({'is_in_playlist': True}), 200)
        else:
            return make_response(jsonify({'is_in_playlist': False}), 200)
        

from flask import jsonify

    
class TracksInPlaylistResource(Resource):
    @token_required  # Require a valid JWT for this route
    def get(self, playlist_id):
        playlist_tracks = PlaylistTrack.query.filter_by(playlist_id=playlist_id).all()

        if playlist_tracks:
            track_data = []

            for playlist_track in playlist_tracks:
                track = Track.query.get(playlist_track.track_id)
                if track:
                    album = Album.query.get(track.album_id)
                    artists = [artist.name for artist in track.artists]

                    track_info = {
                        "id": track.id,
                        "title": track.title,
                        "file_path": track.file_path,
                        "album_id":track.album_id,
                        "album_name": album.title if album else None,
                        "artist_name": artists[0] if artists else None,
                        "stream_count": track.stream_count,
                        "average_rating": track.average_rating,
                        "track_number": track.track_number,
                        "order": playlist_track.track_order,
                        "lyrics":track.lyrics
                    }
                    track_data.append(track_info)

            return jsonify(track_data)
        else:
            return jsonify([])  # Return an empty list if no tracks are found
# Return an empty list if no tracks are found


        

class PlaylistNameResource(Resource):
    def get(self, playlist_id):
        playlist = Playlist.query.get(playlist_id)

        if playlist:
            playlist_info = {"id": playlist.id, "name": playlist.title}
            return jsonify(playlist_info)
        else:
            return jsonify({'error': 'Playlist not found'}), 404

class EditPlaylistNameResource(Resource):
    @token_required
    def put(self, playlist_id):
        try:
            playlist = Playlist.query.get(playlist_id)
            if not playlist:
                return make_response(jsonify({'error': 'Playlist not found'}), 404)

            # Check if the current user is the owner of the playlist
            

            data = request.get_json()
            new_name = data.get('name')

            if not new_name:
                return make_response(jsonify({'error': 'Name cannot be empty'}), 400)

            playlist.title = new_name
            db.session.commit()

            return make_response(jsonify({'success': True}), 200)

        except Exception as e:
            print(str(e))
            return make_response(jsonify({'error': 'Internal Server Error'}), 500)
        
class DeletePlaylistResource(Resource):
    @token_required
    def delete(self, playlist_id):
        try:
            playlist = Playlist.query.get(playlist_id)
            if not playlist:
                return make_response(jsonify({'error': 'Playlist not found'}), 404)

            # Check if the current user is the owner of the playlist
           
            # Delete the playlist and associated tracks
            playlist_tracks = PlaylistTrack.query.filter_by(playlist_id=playlist_id).all()
            for playlist_track in playlist_tracks:
                db.session.delete(playlist_track)

            db.session.delete(playlist)
            db.session.commit()

            return make_response(jsonify({'success': True}), 200)

        except Exception as e:
            print(str(e))
            return make_response(jsonify({'error': 'Internal Server Error'}), 500)
        

class RemoveSongResource(Resource):
    def delete(self, playlist_id, track_id):
        try:
            # Fetch the playlist and track
            playlist = Playlist.query.get(playlist_id)
            track = Track.query.get(track_id)

            # Check if the playlist and track exist
            if not playlist or not track:
                abort(404, error="Playlist or Track not found")

            # Fetch the playlist track entry for the specified track in the playlist
            playlist_track = PlaylistTrack.query.filter_by(playlist_id=playlist_id, track_id=track_id).first()

            # Check if the playlist track entry exists
            if not playlist_track:
                abort(404, error="Track not found in the playlist")

            # Delete the playlist track entry
            db.session.delete(playlist_track)

            # Update the track orders for songs below the removed track
            below_tracks = PlaylistTrack.query.filter_by(playlist_id=playlist_id).filter(PlaylistTrack.track_order > playlist_track.track_order).all()
            for below_track in below_tracks:
                below_track.track_order -= 1

            # Commit changes to the database
            db.session.commit()

            return jsonify({"success": True, "message": "Song removed successfully"})

        except Exception as e:
            abort(500, error=str(e))

class UpdateTrackOrdersResource(Resource):
    def put(self, playlist_id):
        parser = reqparse.RequestParser()
        parser.add_argument('newTrackOrders', type=list, location='json', required=True)
        args = parser.parse_args()

        try:
            # Fetch the playlist tracks for the given playlist_id
            playlist_tracks = PlaylistTrack.query.filter_by(playlist_id=playlist_id).all()

            if not playlist_tracks:
                return jsonify({"error": "Playlist not found or has no tracks"}), 404

            # Update track orders based on the received data
            for new_order_data in args['newTrackOrders']:
                track_id = new_order_data['trackId']
                new_order = new_order_data['newOrder']

                # Find the playlist track entry for the track in the playlist
                playlist_track = next((pt for pt in playlist_tracks if pt.track_id == track_id), None)

                if playlist_track:
                    playlist_track.track_order = new_order

            # Commit changes to the database
            db.session.commit()

            return jsonify({"success": True, "message": "Track orders updated successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
class RemoveTrack(Resource):
    def delete(self, track_id):
        try:
            # Check if the track exists
            track = Track.query.get(track_id)
            if not track:
                return jsonify({'error': 'Track not found'}), 404

            # Delete the track from the track table
            db.session.delete(track)
            db.session.commit()

            # Remove the track from the artist_track_association table
            artist_track_association_entry = artist_track_association.delete().where(artist_track_association.c.track_id == track_id)
            db.session.execute(artist_track_association_entry)
            db.session.commit()

            return make_response(jsonify({'message': 'Track removed successfully'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)
        


# Add the endpoint to your Flask application
api.add_resource(RemoveTrack, '/remove-track/<int:track_id>')


api.add_resource(GetTracksByAlbum, '/get_tracks_by_album/<int:album_id>')
api.add_resource(SearchTracks,"/search")
api.add_resource(ToggleTrackInPlaylist, '/playlist/toggle-track')
api.add_resource(CheckTrackInPlaylist, '/playlist/check-track')
api.add_resource(TracksInPlaylistResource, '/playlists/<int:playlist_id>')
api.add_resource(PlaylistNameResource, '/playlists/getname/<int:playlist_id>')
api.add_resource(EditPlaylistNameResource, '/playlists/edit/<int:playlist_id>')
api.add_resource(DeletePlaylistResource, '/playlists/delete/<int:playlist_id>')
api.add_resource(RemoveSongResource, '/playlists/remove-song/<int:playlist_id>/<int:track_id>')
api.add_resource(UpdateTrackOrdersResource, '/playlists/update-track-orders/<int:playlist_id>')
