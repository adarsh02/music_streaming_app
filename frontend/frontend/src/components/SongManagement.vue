<template>
  <div>
    <Player :hidePlayer=false v-if="type!=='Admin'"/>
    <div class="root-page">
      <div v-if="type==='Admin'">
    <nav class="navbar">
      <div class="navbar-left">
        <!-- Use router-link to navigate to the "/admin_album_management" route -->
        <router-link to="/admin_album_management" class="navbar-label">Album Management</router-link>
      </div>
      <router-link to="/admin_home">
        <img src="@/assets/logo.png" alt="Logo" width="100" height="50" />
      </router-link>
      <div class="navbar-right">
        <button class="logout-button" @click="logout">Log out</button>
      </div>
    </nav>
  </div>
      <h1 @click="showEditAlbumDialog=!showEditAlbumDialog">{{ albumName }}</h1>
      <!-- Edit Album Name Dialog -->
      <div v-if="showEditAlbumDialog" class="dialog">
    <button class="close-btn" @click="closeEditAlbumDialog">&times;</button>
    <label>New Album Name:</label>
    <input v-model="editedAlbumName" placeholder="New Album Name" required />
    <label>Select Artist:</label>
    <select v-model="selectedArtist" required>
        <option v-for="artist in artists" :key="artist.id" :value="artist.id">{{ artist.name }}</option>
    </select>
    <button @click="editAlbumName">Save</button>
    <button @click="deleteAlbum">Delete</button>
</div>

  
      <!-- Create Song Button -->
      <button @click="showCreateSongDialog = true">Add Song</button>
  
      <!-- Create Song Dialog -->
      <div v-if="showCreateSongDialog" class="dialog">
  <button class="close-btn" @click="closeCreateSongDialog">&times;</button>
  <label>Song Title:</label>
  <input v-model="newSongTitle" placeholder="Song Title" />
  <label>Genre:</label>
  <input v-model="newSongGenre" placeholder="Genre" />
  <label>Language:</label>
  <input v-model="newSongLanguage" placeholder="Language" />
  <label>Lyrics:</label>
  <textarea v-model="newSongLyrics" placeholder="Lyrics" rows="6"></textarea>

 



  
  
  <!-- Artists dropdown -->
  <label>Select Artist:</label>
  <select v-model="selectedArtist">
    <option v-for="artist in artists" :key="artist.id" :value="artist.id">{{ artist.name }}</option>
  </select>
  
  <button @click="createSong">Create</button>
</div>

  
      <!-- Song List -->
      <div v-for="song in songs" :key="song.id" class="song-container">
    <h3 class="song-title">{{ song.title }}</h3>
    <p class="song-artist">{{ song.artist_name }}</p>
    <button @click="editSong(song)" style="margin-right:10px">Edit</button>
    <button @click="removeSong(song.id)">Remove</button>
</div>
    </div>

    <div v-if="showEditSongDialog" class="dialog">
    <button class="close-btn" @click="closeEditSongDialog">&times;</button>
    <label>Title:</label>
    <input v-model="editedSong.title" placeholder="Song Title" />
    <label>Genre:</label>
    <input v-model="editedSong.genre" placeholder="Genre" />
    <label>Language:</label>
    <input v-model="editedSong.language" placeholder="Language" />
    <label>Lyrics:</label>
    <textarea v-model="editedSong.lyrics" placeholder="Lyrics" rows="6"></textarea>
    <!-- Artists dropdown -->
    <label>Select Artist:</label>
    <select v-model="selectedArtist">
        <option v-for="artist in artists" :key="artist.id" :value="artist.id">{{ artist.name }}</option>
    </select>
    <button @click="saveEditedSong">Save</button>
</div>
</div>
  </template>
  
  <script>
  import { ref,onMounted,reactive } from 'vue';
  import { useRouter } from 'vue-router';
  import Player from './Player.vue';
  
  export default {
    name: 'SongManagement',
    props:
    {
        type:String
    },
    components: {
    Player
  },
    setup(props) {
      const router = useRouter();
      const albumName = ref('');
      const userId = localStorage.getItem('userId');
      const editedAlbumName = ref('');
      const newSongGenre = ref('');  
      const newSongLanguage = ref('');
      const showEditAlbumDialog = ref(false);
      const newSongTitle = ref('');
      const newSongLyrics = ref('');
      const newSongArtist = ref('');
      const showCreateSongDialog = ref(false);
      const token = localStorage.getItem('token');
      const songs = ref([]);
      const artists = ref([]);
    const selectedArtist = ref(null);
    const showEditSongDialog = ref(false);
    const editedSong = reactive({
        id: null,
        title: '',
        genre: '',
        language: '',
        lyrics: '',
        artist_id: '',

        
    });

    const editSong = (song) => {
        editedSong.id = song.id;
        editedSong.title = song.title;
        editedSong.genre = song.genre;
        editedSong.language = song.language;
        editedSong.lyrics = song.lyrics;
        editedSong.artist_id = selectedArtist.value;
        
        showEditSongDialog.value = true;
    };

    const logout = () => {
      // Clear local storage
      localStorage.clear();
      
      // Navigate to '/user_login'
      router.push('/admin_login');
    };


    const closeEditSongDialog = () => {
        showEditSongDialog.value = false;
    };

    const saveEditedSong = async () => {
    try {
      if (editedSong.title!='' && editedSong.genre!='' && editedSong.language!='' && editedSong.lyrics!='' && selectedArtist.value!=null){
        const response = await fetch(`http://127.0.0.1:5000/albums/edit-song/${editedSong.id}`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authentication-Token': token
            },
            body: JSON.stringify({
                id:editedSong.id,
                title:editedSong.title,
                genre:editedSong.genre,
                language:editedSong.language,
                lyrics:editedSong.lyrics,
                artist_id:selectedArtist.value
       

            })
        });

        if (!response.ok) {
            const error = await response.json(); // Extract JSON error message
            throw new Error(`HTTP error! Status: ${response.status} - ${error.error}`);
        }

        const data = await response.json(); // Extract JSON data from the response
        console.log('Song updated successfully:', data);
        alert('Song saved successfully');
        showEditSongDialog.value = false;
        fetchData();
       }
       else{
        alert('These fields cant be empty');
       } // Assuming fetchData function fetches updated song data
    } catch (error) {
        console.error('Error updating song:', error);
    }
};// Selected artist ID // Use reactive for arrays to ensure reactivity
  
      const fetchData = async () => {
        try {
          // Fetch album data including songs from the backend API
          // You need to replace 'albumId' with the actual ID of the album
          const albumId = router.currentRoute.value.params.albumId;
          const response = await fetch(`http://127.0.0.1:5000/tracks/get_tracks_by_album/${albumId}`, {
          method: 'GET',
          headers: {
            'Authentication-Token': token // Include the token in the headers
        },
        });
          const data = await response.json();
          albumName.value = data.album.title;
          songs.value = data.tracks;
          let artistEndpoint;
          if (props.type==='Admin'){
        artistEndpoint = `http://127.0.0.1:5000/user/artists`;
          }
          else{
         artistEndpoint = `http://127.0.0.1:5000/user/artists/${userId}`;
          }
        const artistResponse = await fetch(artistEndpoint, {
          method: 'GET',
          headers: {
            'Authentication-Token': token
          },
        });

        if (!artistResponse.ok) {
          throw new Error(`HTTP error! Status: ${artistResponse.status}`);
        }

        const artistData = await artistResponse.json();
        artists.value = artistData;
      } 
         catch (error) {
          console.error('Error fetching album data:', error);
        }
      };
  
      const editAlbumName = async () => {
  try {
    if (editedAlbumName.value!=''){
    // Prepare the request data
    const requestData = {
      new_album_title: editedAlbumName.value,
      artist_id: selectedArtist.value
    };
    const albumId = router.currentRoute.value.params.albumId;

    // Send a PUT request to the backend API
    const response = await fetch(`http://127.0.0.1:5000/albums/edit/${albumId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token  // Assuming you have a token stored in a ref named token
      },
      body: JSON.stringify(requestData)
    });

    // Handle the response
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // Show a success message or perform any other action upon successful update
    console.log('Album name updated successfully');
    // Close the edit dialog if needed
    showEditAlbumDialog.value = false;
    fetchData();
  }
  else{
    alert('New album name cant be empty');
  }
  } catch (error) {
    console.error('Error updating album name:', error);
    // Handle errors, e.g., show an error message to the user
  }
};

  
      const closeEditAlbumDialog = () => {
        showEditAlbumDialog.value = false;
      };
  
      const saveAlbumName = () => {
        // Update the album name in the backend
        // Then update albumName.value with the new name
        closeEditAlbumDialog();
      };
  
      const deleteAlbum = async () => {
  try {
    // Send a DELETE request to the backend API
    const albumId = router.currentRoute.value.params.albumId;
    const response = await fetch(`http://127.0.0.1:5000/albums/delete/${albumId}`, {
      method: 'DELETE',
      headers: {
        'Authentication-Token': token // Assuming you have a token stored in a ref named token
      }
    });

    // Handle the response
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // Show a success message or perform any other action upon successful deletion
    console.log('Album deleted successfully');
    // Redirect the user to the albums page after deletion
    router.push({ name: 'creator_mode' });
  } catch (error) {
    console.error('Error deleting album:', error);
    // Handle errors, e.g., show an error message to the user
  }
};

  
      const closeCreateSongDialog = () => {
        showCreateSongDialog.value = false;
        // Reset new song fields
        newSongTitle.value = '';
        newSongArtist.value = '';
        newSongLanguage.value='';
        newSongGenre.value ='';
        newSongLyrics.value='';
        
      };
  
      const createSong = async () => {
    try {
      if (newSongTitle.value!='' && newSongGenre.value!='' && newSongLanguage.value!='' && selectedArtist.value!=null && newSongLyrics.value!='' ){
        
        const albumId = router.currentRoute.value.params.albumId;
        const response = await fetch('http://127.0.0.1:5000/albums/add-song', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: newSongTitle.value,
                genre: newSongGenre.value,
                language: newSongLanguage.value,
                album_id: albumId,
                added_by: userId,
                artist_id: selectedArtist.value,
                lyrics: newSongLyrics.value
                    })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        console.log(data); // Handle response data as needed
        closeCreateSongDialog(); 

        fetchData();
      }
      else{
        alert('The fields cant be empty');// Close dialog after successful creation
    } 
  }catch (error) {
        console.error('Error creating song:', error);
    }
};

  
    
  
      const removeSong = async (songId) => {
    try {
        const response = await fetch(`http://127.0.0.1:5000/tracks/remove-track/${songId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to remove song with ID ${songId}`);
        }

        // Remove the song from the songs array
       
        fetchData();
        console.log(`Song with ID ${songId} removed successfully`);
        alert('Song removed successfully');
    } catch (error) {
        console.error('Error removing song:', error);
    }
};

onMounted(() => {
      
      fetchData();


    });
  
      
  
      return {
        albumName,
        editedAlbumName,
        showEditAlbumDialog,
        newSongTitle,
        newSongArtist,
        newSongLyrics,
        newSongGenre,
        newSongLanguage,
        showCreateSongDialog,
        songs,
        editAlbumName,
        closeEditAlbumDialog,
        saveAlbumName,
        deleteAlbum,
        closeCreateSongDialog,
        createSong,
        editSong,
        removeSong,
        artists,
        selectedArtist,
        showEditSongDialog,
        closeEditSongDialog,
        saveEditedSong,
        editedSong,
        logout
      };
    },
  };
  </script>
  
  <style>
  .song-container {
    background-color: #f4f4f4;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.song-title {
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 5px;
}

.song-artist {
    color: #888;
}
  .root-page {
    background-color: #f4f4f4;
    padding: 20px;
  }
  
  .dialog {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    padding: 16px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    text-align: center;
}

.dialog textarea {
    width: 100%;
    resize: vertical; /* Allow vertical resizing */
    overflow-y: auto; /* Add vertical scrollbar when needed */
    margin-bottom: 10px;
    border: 1px solid #ccc; /* Add a border */
    border-radius: 4px; /* Optional: Add border radius */
    padding: 8px; /* Optional: Add padding */
}
  
  .dialog label {
    display: block;
    margin-bottom: 8px;
  }
  
  .dialog input {
    width: 100%;
    padding: 8px;
    margin-bottom: 16px;
    border: 1px solid #ccc; /* Add a border */
    border-radius: 4px; /* Optional: Add border radius */
    
  }
  
  .dialog button {
    padding: 8px 16px;
    margin-right: 8px;
    cursor: pointer;
  }
  
  .close-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 16px;
    background: none;
    border: none;
    cursor: pointer;
    color: #555;
  }
  
  .close-btn:hover {
    color: #000;
  }
  </style>
  