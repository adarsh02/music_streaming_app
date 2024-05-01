<template>
  <div>

  <Player v-if="type!=='Admin'"/>
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
    
    <div v-if="isCreator">
      <h1>Your albums</h1>
      <button @click="showCreateAlbumDialog = !showCreateAlbumDialog">Create New Album</button>
    </div>
    <div v-else>
      <h2>Want to register as creator?</h2>
      <label>Enter Artist Name:</label>
      <input v-model="artistName" placeholder="Artist Name" />
      <button @click="registerArtist">Register</button>
    </div>
    <div v-for="album in tracks" :key="album.id" class="album-card" @click="navigateToAlbum(album.id)">
  <h2 class="album-title">{{ album.title }}</h2>
</div>

    <!-- Dialog for Creating a New Album -->
    <div v-if="showCreateAlbumDialog" class="playlist-dialog">
      <button class="close-btn" @click="closeCreateAlbumDialog">&times;</button>
      <label>Enter Album Name:</label>
      <input v-model="newAlbumName" placeholder="Album Name" />
    
      <!-- Drop-down list to select artist -->
      <label>Select Artist:</label>
      <select v-model="selectedArtist">
        <option v-for="artist in artists" :key="artist.id" :value="artist.id">{{ artist.name }}</option>
      </select>
    
      <button @click="createAlbum">Create</button>
    </div>
  </div>
</div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Player from './Player.vue';

export default {
  name: 'AlbumManagement',
  props: {
    type: String
  },
  components: {
    Player
  },
  setup(props) {
    const tracks = ref([]);
    const artistName = ref('');
    const showCreateAlbumDialog = ref(false);
    const isCreator = ref(false);
    const newAlbumName = ref('');
    const router = useRouter();
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('userId');
    const artists = ref([]);
    const selectedArtist = ref(null); 

    const navigateToAlbum = (albumId) => {
      if (props.type !== 'Admin'){
  router.push({ name: 'song-management', params: { albumId } });
      }
      else{
        router.push({ name: 'admin_song_management', params: { albumId } });
      }
};

    const fetchData = async () => {
    try {
      let albumEndpoint = `http://127.0.0.1:5000/albums/user/${userId}`;
      let artistEndpoint = `http://127.0.0.1:5000/user/artists/${userId}`;

      if (props.type === 'Admin') {
        albumEndpoint = `http://127.0.0.1:5000/albums/albums`;
        artistEndpoint = `http://127.0.0.1:5000/user/artists`;
      }

      const albumResponse = await fetch(albumEndpoint, {
        method: 'GET',
        headers: {
          'Authentication-Token': token
        },
      });

      if (!albumResponse.ok) {
        throw new Error(`HTTP error! Status: ${albumResponse.status}`);
      }

      const albumData = await albumResponse.json();
      tracks.value = albumData;

     
        const artistResponse = await fetch(artistEndpoint, {
          method: 'GET',
          headers: {
            'Authentication-Token': token
          },
        });

        if (!artistResponse.ok) {
          throw new Error(`HTTP error! Status: ${artistResponse.status}`);
        }

        const fetchedArtists = await artistResponse.json();
        artists.value = fetchedArtists;
      
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };


    const createAlbum = async () => {
      try {
        if (selectedArtist.value!=null && newAlbumName.value!=''){
        const response = await fetch('http://127.0.0.1:5000/albums/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token
          },
          body: JSON.stringify({
            user_id: userId,
            artist_id: selectedArtist.value, 
            album_title: newAlbumName.value
          })
        });
        

        if (!response.ok) {
          throw new Error('Failed to create album');
        }

        // Reset form fields
        closeCreateAlbumDialog();
        newAlbumName.value = '';
        fetchData();

        console.log('Album created successfully');
      }
      else{
        alert('These fields cant be empty');
      }
      } catch (error) {
        console.error('Error creating album:', error);
      }
    };

    const checkUserRole = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/user/${userId}/roles`, {
          method: 'GET',
          headers: {
            'Authentication-Token': token
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const roles = data.roles;

        // Check if the user has the "creator" role
        isCreator.value = roles.includes('creator') || roles.includes('admin');
      } catch (error) {
        console.error('Error checking user role:', error);
      }
    };

    const logout = () => {
      // Clear local storage
      localStorage.clear();
      
      // Navigate to '/user_login'
      router.push('/admin_login');
    };


    const closeCreateAlbumDialog = () => {
      showCreateAlbumDialog.value = false;
      newAlbumName.value = '';
    };

    const registerArtist = async () => {
  try {
    if (artistName.value!=''){
    const response = await fetch('http://127.0.0.1:5000/user/register/artist', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
      },
      body: JSON.stringify({
        artist_name: artistName.value,
        user_id: userId
      })
    });

    if (!response.ok) {
      throw new Error('Failed to register artist');
    }

    // Reset artistName field
    artistName.value = '';
    isCreator.value = true;

    
    console.log('Artist registered successfully');
    
  }
  else{
    alert('Artist name cant be empty');
  }
  } catch (error) {
   
    console.error('Error registering artist:', error);

    
    
      alert('Artist name already exists');
    
  }
};


    onMounted(() => {
      checkUserRole();
      fetchData();


    });

    return {
      tracks,
      navigateToAlbum,
      token,
      showCreateAlbumDialog,
      newAlbumName,
      createAlbum,
      closeCreateAlbumDialog,
      artistName,
      registerArtist,
      checkUserRole,
      isCreator,
      artists,
      selectedArtist,
      logout
    };
  },
};
</script>

<style>
.root-page {
 
  padding: 20px;
  min-height: 100vh;
  margin-bottom: 80px;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #333;
  color: #fff;
  padding: 10px 20px;
}

.navbar-left {
  display: flex;
  align-items: center;
}

.navbar-right {
  display: flex;
  align-items: center;
}

.navbar-label {
  color: #fff;
  text-decoration: none;
  margin-right: 20px;
}

.logout-button {
  padding: 8px 16px;
  cursor: pointer;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.logout-button:hover {
  background-color: #0056b3;
}

.card-header {
  font-weight: bold;
}

.card-text {
  font-size: 16px;
}

.album-card {
  display: inline-block;
  margin: 10px; 
  padding: 15px; 
  border-radius: 5px;
  background-color: #f5f5f5; 
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); 
  cursor: pointer; 
  transition: transform 0.2s ease-in-out; 
}

.album-card:hover {
  transform: scale(1.02); 
}

.album-title {
  font-size: 18px;
  font-weight: bold; 
  margin-bottom: 5px; 
  text-align: center; 
}

.btn-light {
  background-color: #fff;
  color: #333;
}

.playlist-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 24px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  text-align: center;
  width: 300px;
}

.playlist-dialog label {
  display: block;
  margin-bottom: 8px;
}

.playlist-dialog input,
.playlist-dialog select {
  width: calc(100% - 24px);
  padding: 8px;
  margin-bottom: 16px;
}

.playlist-dialog button {
  padding: 8px 16px;
  margin-top: 16px;
  cursor: pointer;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.playlist-dialog button:hover {
  background-color: #0056b3;
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

