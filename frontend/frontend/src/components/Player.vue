<template>
  <div>
    <div class="header">
      <div class="search-container">
        <input v-model="searchQuery" @input="search" placeholder="Search..." class="search-input" />
        <div v-if="showResults" class="search-results">
          <ul v-if="results.tracks.length > 0" class="results-list">
            <li v-for="track in results.tracks" :key="track.id" @click="navigatetoAlbum(track.album_name,track.album_id)">
              {{ track.name }} - {{ track.album_name }}
            </li>
          </ul> 
          <ul v-if="results.albums.length > 0" class="results-list">
            <li v-for="album in results.albums" :key="album.id" @click="navigatetoAlbum(album.name,album.id)">
              {{ album.name }}
            </li>
          </ul>
          <p v-if="results.tracks.length === 0 && results.albums.length === 0" class="no-results">No results found.</p>
        </div>
        
        <!-- Logout button -->
        <button @click="logout" class="logout-btn">Logout</button>
        <button @click="redirectToCreatorMode" class="logout-btn">Creator Mode</button>
      </div>
    </div>

    <div class="sidebar">
      <router-link to="/user_home">
        <img src="@/assets/logo.png" alt="Logo" width="100" height="50" />
      </router-link>

      <div class="playlist-section">
        <div class="playlist-title">
          Playlists
          <div class="create-playlist-icon" @click="showPlaylistForm = !showPlaylistForm"><i class="fas fa-plus"></i></div>
        </div>

        <!-- Playlist creation form -->
        <div v-if="showPlaylistForm" class="playlist-form">
          <input v-model="newPlaylistName" placeholder="Enter playlist name" style="width: 120px;" />
          <button @click="createPlaylist">Create</button>
        </div>

        
        <ul v-if="playlists.length > 0">
          
          <router-link
            v-for="playlist in playlists"
            :key="playlist.id"
            :to="{ name: 'playlist-track', params: { playlistId: playlist.id } }"
          >
            <li>{{ playlist.title }}</li>
          </router-link>
        </ul>
        <p v-else>No playlists available.</p>
      </div>
    </div>

    <div class="bottom-container" v-if="hidePlayer===true">
  <div class="rows">
    <div class="icons row">
      <span v-if="audioElement" class="truncate">{{ currentTrack.title }}</span>
    </div>
    <div class="icons row">
      <span v-if="audioElement" class="truncate">{{ currentTrack.album_name }}</span>
    </div>
  </div>


      <div style="margin-top:50px">
        <span v-if="audioElement" style="font-size: 0.8em; margin-left:60px; margin-top:2px;">{{ convertToMinuteSeconds(audioElement.currentTime) }}</span>
      </div>


      <div class="rows">
        <div class="icons row">
          
          <i class="far fa-3x" :class="{ 'fa-play-circle': isPaused, 'fa-pause-circle': !isPaused }" id="play" @click="handleMasterPlayClick"></i>
        </div>
        <div class="row">
          <input type="range" id="myProgressBar" max="100" :value="sliderPosition" @input="updateSliderPositionFromInput"/>
        </div>
      </div>

      <div style="margin-top:50px">
        <span v-if="audioElement" style="font-size: 0.8em; margin-right:60px; margin-top:2px;">{{ convertToMinuteSeconds(audioElement.duration) }}</span>
      </div>

      <div class="section">
        <div class="icons">
          <input type="range" id="VolumeBar" max="100" :value="volumeValue" @input="updateVolume" />
          <i style="font-size: 1rem" :class="{'fa-solid fa-volume-high':!isMute,'fa-solid fa-volume-xmark':isMute}" id="VolumeIcon" @click="toggleMute"></i>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import router from '@/router/routes';
import '@fortawesome/fontawesome-free/css/all.css'; // Import Font Awesome CSS

import { ref, onMounted} from 'vue';
import { nextTick } from 'vue';


export default {
  name: 'AudioPlayer',
  props: {
    currentTrack: Object,
    isPaused: Boolean,
    audioElement: Object,
    updateSliderPosition: Function,
    sliderPosition: Number
  },
  setup(props, { emit }) {
    const isMute = ref(false);
    const oldVolume = ref(50);
    const liked = ref(false);
    const volumeValue = ref(100);
    const hidePlayer = ref(true);

    const showPlaylistForm = ref(false);
    const newPlaylistName= ref("");
    const token = localStorage.getItem('token');
    const playlists = ref([]);

    const searchQuery = ref('');
    const results = ref({ tracks: [], albums: [] });
    const showResults = ref(false);

    const logout = () => {
      
      localStorage.clear();
      
      // Navigate to '/user_login'
      router.push('/user_login');
    };

    const redirectToCreatorMode = ()=>{
      router.push('/creator_mode');
    };

    const navigatetoAlbum = (albumName,albumId)=>{
      router.push(`/album-tracks/${albumName}/${albumId}`);
      showResults.value = false;

      
    };

    const search = async () => {
      try {
        if (searchQuery.value.trim() === '') {
          results.value = { tracks: [], albums: [] };
          showResults.value = false;
          return;
        }

        const response = await fetch(`http://127.0.0.1:5000/tracks/search?query=${searchQuery.value}`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        results.value = data;
        showResults.value = true;
      } catch (error) {
        console.error('Error searching:', error);
      }
    };

    const fetchPlaylists = async () => {
      try {
        const userId = localStorage.getItem('userId');
        const token = localStorage.getItem('token');

        const response = await fetch(`http://127.0.0.1:5000/user/playlists/${userId}`, {
          method: 'GET',
          headers: {
            'Authentication-Token': token,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        playlists.value = data['playlists']; 
      } catch (error) {
        console.error('Error fetching playlists:', error);
      }
    };

    const updateSliderPositionFromInput = () => {

      if (props.audioElement){
      emit('updateSliderPositionvalue',document.getElementById("myProgressBar").value);

      nextTick(() => {

    const newPosition = (props.sliderPosition / 100) * props.audioElement.duration;
    emit('updateSliderPosition', newPosition);
      
  });
}
    };

    const formatDuration = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);

  const formattedDuration = `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  return formattedDuration;
};

    const likeController = () => {
      liked.value = !liked.value;
      emit('likeChange', liked.value);
    };


    const setVolume = (value) => {

      if (props.audioElement) {
        volumeValue.value = value;
        emit('volumeChange', value);
      }
    };

    const createPlaylist = async () => {
  try {
    const userId=localStorage.getItem('userId');
    const response = await fetch(`http://127.0.0.1:5000/user/create_playlist/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token
        
      },
      body: JSON.stringify({
        title:newPlaylistName.value,
      
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
 
    
    fetchPlaylists();
    emit('fetchAgain');
    alert('Playlist created successfully');

    // Reset the form state
    showPlaylistForm.value = false;
    newPlaylistName.value = '';
  } catch (error) {
    console.error('Error creating playlist:', error);
  }
};

  

    const updateVolume = () => {
      if (props.audioElement){
      volumeValue.value = document.getElementById("VolumeBar").value;
      if (volumeValue.value==0){
        isMute.value=true;
      }
      else{
        isMute.value=false;
      }
      emit('volumeChange',volumeValue.value);
      }
      
    };
   
    const handleMasterPlayClick = () => {
      
        if (!props.audioElement) {
          console.error('Audio element is null.');
          return;
        }

        emit('masterPlayClick');
    };

    const convertToMinuteSeconds= (decimalNumber)=> {
      const minutes = Math.floor(decimalNumber / 60);
      const seconds = Math.floor(decimalNumber % 60);

      return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    };

    const toggleMute = () => {
      isMute.value = !isMute.value;
      if (props.audioElement){
      if (isMute.value) {
        console.log('New volume'+volumeValue.value);
        oldVolume.value = volumeValue.value;
        console.log(oldVolume.value);
        
        setVolume(0);
      } else {
        setVolume(oldVolume.value);
        console.log(oldVolume.value);
      }
      
    }
    
  
  };

  

onMounted(() => {
      handleMasterPlayClick();
      fetchPlaylists();
    });

    

    return {
      isMute,
      oldVolume,
      liked,
      volumeValue,
      updateSliderPositionFromInput,
      likeController,
      setVolume,
      updateVolume,
      handleMasterPlayClick,
      toggleMute,
      formatDuration,
      convertToMinuteSeconds,
      playlists,
      createPlaylist,
      showPlaylistForm,
      newPlaylistName,
      fetchPlaylists,
      searchQuery,
      results,
      showResults,
      search,
      navigatetoAlbum,
      logout,
      redirectToCreatorMode,
      hidePlayer

    
    };
  }
};
</script>




  
  <style>
  body {
    margin: 0;
    font-family: Arial, sans-serif;
  }
  
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 150px;
    bottom: 80px;
    background-color: #ede7e7;
    padding: 10px;
    box-sizing: border-box;
    overflow-y: auto; 
}
  
 

  .search-input {
  width: 300px;
  padding: 8px;
  font-size: 16px;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background-color: white;
  border: 1px solid #ccc;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.truncate {
  display: inline-block;
  width: 120px; 
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}


  
  
  .header {
    position: fixed;
    top: 0;
    left: 150px;
    width: calc(100% - 150px);
    background-color: #ff6699;
    color: #fff;
    padding: 10px;
    box-sizing: border-box;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.search-container {
    position: relative;
}

.search-input {
    border: none;
    padding: 8px;
    border-radius: 20px;
    width: 300px;
    font-size: 16px;
    color: #333;
}

.search-results {
    position: absolute;
    top: calc(100% + 5px);
    left: 0;
    width: 100%;
    background-color: #fff;
    border: 1px solid #ccc;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 999;
}

.results-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.results-list li {
    padding: 10px;
    cursor: pointer;
}

.results-list li:hover {
    background-color: #f0f0f0;
}

.no-results {
    padding: 10px;
    margin: 0;
}

.logout-btn {
    background-color: transparent;
    color: #fff;
    border: none;
    cursor: pointer;
    font-size: 16px;
    padding: 8px 12px;
    border-radius: 4px;
}

.logout-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

  
  
  
  #myProgressBar {
    width: 50vw;
    cursor: pointer;
  }
  
  #VolumeBar {
    width: 8vw;
    cursor: pointer;
  }

  .bottom-container {
    display: grid;
    grid-template-columns: 1fr 0.125fr 2fr 0.125fr 1fr;
    grid-template-rows: 1fr;
    background-color: #ffffff;
    width: 100%;
    bottom: 0px;
    position: fixed;
    border-top: #333;
    border-width: 3px;
    box-sizing: border-box;
    height: 80px;
  }
  
  .section,
  .rows,
  .row {
    border: 1px;
    margin: 5px;
  }

  .row .icons {
    width: 20px;
    height: 20px;
    margin-right: 10px;
  }
  .rows {
    display: flex;
    flex-direction: column;
  }
  
  
  .icons {
    margin-top: 8px;
    justify-content: center;
    align-items: center;
    margin-left: 20px;
  }
  
  .icons i {
    cursor: pointer;
    margin-left: 20px;
    font-size: 2rem;
  }

  .playlist-section {
      margin-bottom: 20px;
      margin-top: 50px;
    }

    .playlist-title {
      font-size: 24px;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
    }

    .create-playlist-icon {
      font-size: 28px;
      cursor: pointer;
      margin-left: auto;
      transition: color 0.3s;
    }

    .create-playlist-icon:hover {
      color: #5cb85c; 
    }

    .tooltip {
      display: none;
      position: absolute;
      background-color: #333;
      color: white;
      padding: 5px;
      border-radius: 5px;
      font-size: 14px;
      margin-left: 10px;
    }

    .create-playlist-icon:hover + .tooltip {
      display: block;
    }

    ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    li {
      padding: 8px 0;
      font-size: 16px;
      color: #000;
      cursor: pointer;
      transition: color 0.3s;
    }

    li:hover {
      color: #5cb85c; /* Green color on hover */
    }

    .search-results {
  position: absolute;
  background-color: white;
  border: 1px solid #ccc;
  max-height: 200px;
  overflow-y: auto;
}
  </style>