<template>
  <div>
    <Player
      :sliderPosition="sliderPosition"
      :audioElement="audioElement"
      :currentTrack="selectedTrack"
      :isPaused="isPaused"
      @playbackToggle="handlePlaybackToggle"
      @masterPlayClick="handleMasterPlayClick"
      @seekbarChange="handleSeekbarChange"
      @volumeChange="handleVolumeChange"
      @updateSliderPosition="updateAudioTime"
      @updateSliderPositionvalue="updateSliderPositionvalue"
    />
    <div class="tracks-section">
      <h2>{{ albumName }}</h2>
      <div class="filter-section">
        <select v-model="filterOption">
          <option value="rating">Rating</option>
          <option value="flagged">Flagged</option>
        </select>
        <template v-if="filterOption === 'rating'">
          <input type="number" v-model="minRating" placeholder="Min Rating" />
          <input type="number" v-model="maxRating" placeholder="Max Rating" />
        </template>
        <template v-else-if="filterOption === 'flagged'">
          <input type="radio" id="flagged" v-model="flagStatus" value="flagged" />
          <label for="flagged">Flagged</label>
          <input type="radio" id="unflagged" v-model="flagStatus" value="unflagged" />
          <label for="unflagged">Unflagged</label>
        </template>
        <button @click="applyFilter" style="margin-left: 10px;">Filter</button>
        <button @click="revertFilter" style="margin-left: 10px;">Revert</button>
      </div>
      <ul class="track-list">
        <li class="track-item track-header">
          
            <span class="track-number" style="padding-right:55px;">Track Number</span>
            <span class="track-title" style="padding-right:75px;">Title</span>
            <span class="artist-name" style="padding-right:55px;">Artist Name</span>
            <span class="plays" style="padding-right:50px;">Plays</span>
            <span class="average-rating" style="padding-right:30px;">Average Rating</span>
            <span class="rate-song" style="padding-right:50px;">Rate Song</span>
            
          
        </li>
        <li v-for="track in tracks" :key="track.id" class="track-item">
          <div class="track-info">
            <span class="track-number">{{ track.track_number }}</span>
            <span class="track-title">
              {{ track.title }}
              <i
                class="fas"
                :class="{ 'fa-play': selectedTrack !== track || isPaused, 'fa-pause': selectedTrack === track && !isPaused }"
                @click="playTrack(track)"
              ></i>
            </span>
            <span class="artist-name">{{ track.artist_name }}</span>
            <span class="plays">{{ track.stream_count }}</span>
            <span class="average-rating">{{ track.average_rating }}</span>
  <input type="number" v-model="track.userRating" min="0" max="100" class="rate-song-input" />
  <button @click="rateSong(track)">Rate</button>
            <span class="options" @click="toggleOptionsDropdown(track)">...</span>
            
            <div v-if="showOptionsDropdown && currentTrackForDropdown === track.id"  class="options-dropdown">
              
                <li @click="viewLyrics(track)">View Lyrics</li>
                <li @click="flagSong(track)">{{ track.is_flagged ? 'Unflag Song' : 'Flag Song' }}</li>
             
            </div>
            <i class="fas fa-plus plus-icon" @click="togglePlaylistDropdown(track)"></i>
            <div v-if="showPlaylistDropdown && currentTrackForDropdown === track.id" class="playlist-dialog">
              <ul>
                <li v-for="playlist in userPlaylists" :key="playlist.id">
                  <span @click="togglePlaylist(playlist)">{{ playlist.title }}</span>
                </li>
              </ul>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <div v-if="showLyrics" class="playlist-dialog">
  <button class="close-btn" @click="showLyrics = false">&times;</button>
  <div class="lyrics-content">
    <pre>{{ currentTrackForLyrics }}</pre>
  </div>
</div>
  </div>
</template>





<script>
import { ref, watch, onMounted } from 'vue';

import { watchEffect } from 'vue';

import Player from './Player.vue';

import { onBeforeRouteLeave } from 'vue-router';

export default {
  name: 'UserHome',
  components: {
    Player,
  },
  props: {
    albumName: String,
    albumId: Number,
  },
  setup(props) {

    console.log('Album name'+props.albumName);
    


    const isPaused = ref(true);
    
    const selectedTrack = ref(null);
    const audioElement = ref(null);
    const sliderPosition = ref(0);
    const tracks = ref([]);
    const token = localStorage.getItem('token');
    const showPlaylistDropdown = ref(false);  
    const showLyrics = ref(false);  
    const userPlaylists = ref([]);
    const currentTrackForDropdown = ref(0);
    const currentTrackForLyrics = ref('');
    const showOptionsDropdown = ref(false);
    const filterOption = ref('default');
    const minRating = ref(0);
    const maxRating = ref(100);
    const flagStatus = ref('flagged');
    const originalTracks = ref([]);
  
   

    const applyFilter = () => {
      tracks.value = originalTracks.value;
      
      if (filterOption.value === 'rating') {
       tracks.value = tracks.value.filter(track => track.average_rating >= minRating.value && track.average_rating <= maxRating.value);
      } else if (filterOption.value === 'flagged') {
        if (flagStatus.value === 'flagged') {
          tracks.value = tracks.value.filter(track => track.is_flagged);
        } else {
          tracks.value = tracks.value.filter(track => !track.is_flagged);
        }
      }
    };

    const revertFilter = () => {
      tracks.value = originalTracks.value;
      filterOption.value = 'default';
      minRating.value = 0;
      maxRating.value = 100;
      flagStatus.value = 'flagged';
    };
    

    const viewLyrics=(track)=>{
      currentTrackForLyrics.value = track.lyrics;
      showLyrics.value = !showLyrics.value;
      

    };

    const rateSong = async (track) => {
      try {
        const userId = localStorage.getItem('userId');
        const token = localStorage.getItem('token');
        const response = await fetch(`http://127.0.0.1:5000/user/rate-song/${userId}/${track.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token,

          },
          body: JSON.stringify({ rating: track.userRating }),
        });
       
        console.log(response);
        fetchData();
        alert("Song rated successfully");
      } catch (error) {
        
        console.error(error);
      }
    };


    const flagSong = async (track) => {
  try {
    const userId = localStorage.getItem('userId');
    const token = localStorage.getItem('token');
    const response = await fetch(`http://127.0.0.1:5000/user/toggle_flag`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token,
      },
      body: JSON.stringify({ user_id: userId, track_id: track.id }),
    });
    
    console.log(response);
    
    fetchData();
    alert("Flag status updated successfully");
  } catch (error) {
    
    console.error(error);
  }
};



const toggleOptionsDropdown = (track) => {
  showOptionsDropdown.value = !showOptionsDropdown.value;
  currentTrackForDropdown.value = track.id;
};


const addToHistory=(track)=> {
      const userId = localStorage.getItem('userId');
      const token = localStorage.getItem('token');

      fetch(`http://127.0.0.1:5000/user/user/add-to-history/${userId}/${track.id}`, {
        method: 'POST',
        headers: {
          'Authentication-Token': token,
        },
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log(data.message);
          
        })
        .catch(error => {
          console.error('Error adding to history:', error);
        });
    };

  

    const togglePlaylistDropdown = (track) => {
      console.log("Hi");
      if (currentTrackForDropdown.value === track.id){
        showPlaylistDropdown.value = !showPlaylistDropdown.value;
      }
      else{
      currentTrackForDropdown.value = track.id;
      
      showPlaylistDropdown.value = true;
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
        userPlaylists.value = data['playlists']; 
      } catch (error) {
        console.error('Error fetching playlists:', error);
      }
    };

    
    const isInPlaylist = async (track_id, playlist_id) => {
  try {
    console.log("Hi again");
    const response = await fetch('http://127.0.0.1:5000/tracks/playlist/check-track', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        playlist_id: playlist_id,
        track_id: track_id,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      console.log(data.is_in_playlist);
      return data.is_in_playlist;

    } else {
      console.error('Error checking track in playlist');
      return false;
    }
  } catch (error) {
    console.error('Error checking track in playlist:', error);
    return false;
  }
};

const isInCurrentPlaylist = async (playlist_id) => {
  if (currentTrackForDropdown.value) {
    const result = await isInPlaylist(currentTrackForDropdown.value, playlist_id);
    return result;
  }
  else{
 return false;
  }
};


    

    const playTrack = (track) => {
      if (selectedTrack.value === track) {
        isPaused.value = !isPaused.value;
        if (audioElement.value !== null) {
          isPaused.value ? audioElement.value.pause() : audioElement.value.play();
        } else {
          audioElement.value = new Audio(track.file_path);
          audioElement.value.play();
        }
      } else {
        selectedTrack.value = track;
        isPaused.value = false;
        if (audioElement.value !== null) {
          audioElement.value.pause();
          audioElement.value = null;
        }
        audioElement.value = new Audio(selectedTrack.value.file_path);
        audioElement.value.play();
      }

      addToHistory(track);
    };

    const handlePlaybackToggle = () => {
      isPaused.value = !isPaused.value;
    };

    const handleMasterPlayClick = () => {
      if (!audioElement.value) {
        console.error('Audio element is null.');
        return;
      }
      isPaused.value = !isPaused.value;
      isPaused.value ? audioElement.value.pause() : audioElement.value.play().catch(error => console.error('Audio Play Error:', error));
    };

    const handleSeekbarChange = (newTime) => {
      if (audioElement.value) {
        audioElement.value.currentTime = newTime;
        sliderPosition.value = (newTime / audioElement.value.duration) * 100;
      }
    };

    const updateAudioTime = (newPosition) => {
      if (audioElement.value) {
        audioElement.value.currentTime = newPosition;
      }
    };

    const updateSliderPositionvalue = (value) => {
      sliderPosition.value = value;
    };

    const handleVolumeChange = (newVolume) => {
      if (audioElement.value) {
        audioElement.value.volume = newVolume / 100;
      }
    };

    const updateSliderPosition = () => {
      if (audioElement.value) {
        sliderPosition.value = (audioElement.value.currentTime / audioElement.value.duration) * 100;
      }
    };


    const fetchData = async () => {
      try {
        const userId = localStorage.getItem('userId');
        const token = localStorage.getItem('token');
        const apiEndpoint = `http://127.0.0.1:5000/tracks/get_tracks_by_album/${props.albumId}`;
        const response = await fetch(apiEndpoint, {
          method: 'GET',
          headers: {
            'Authentication-Token': token,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const tracksData = await response.json();
        tracks.value = tracksData.tracks;
        originalTracks.value = tracks.value

        for (const track of tracks.value) {
          const userRatingResponse = await fetch(`http://127.0.0.1:5000/user/user-rating/${userId}/${track.id}`, {
            method: 'GET',
            headers: {
              'Authentication-Token': token,
            },
          });

          const userRatingData = await userRatingResponse.json();
          track.userRating = userRatingData.rating;
        }

        for (const track of tracks.value) {
          const userFlagResponse = await fetch(`http://127.0.0.1:5000/user/get_flag_status/${userId}/${track.id}`, {
            method: 'GET',
            headers: {
              'Authentication-Token': token,
            },
          });

          const userFlagData = await userFlagResponse.json();
          track.is_flagged= userFlagData.flagged;
        }
      } catch (error) {
        console.error('Error fetching tracks and user ratings:', error);
      }
    };


    const togglePlaylist = async (playlist) => {
  try {
    if (currentTrackForDropdown.value) {
      const response = await fetch('http://127.0.0.1:5000/tracks/playlist/toggle-track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          playlist_id: playlist.id,
          track_id: currentTrackForDropdown.value,
        }),
      });

      if (!response.ok) {
       
      
        const responseData = await response.json();
        if (responseData.error && responseData.error.includes('Track already exists')) {
          
          alert('Error: Track already exists in the playlist');
        } else {
          console.error('Error toggling track in playlist:', responseData.error);
        }
      }
      else{
        alert('Track added to playlist '+playlist.title);
      }
    }
  } catch (error) {
    console.error('Error toggling track in playlist:', error);
  } finally {
   
    currentTrackForDropdown.value = null;
  }
};

 

    // const updateGroupedTracks = () => {
    //   groupedTracks.value = {};
    //   tracks.value.forEach((track) => {
    //     if (!groupedTracks.value[track.album_name]) {
    //       groupedTracks.value[track.album_name] = [];
    //     }
    //     groupedTracks.value[track.album_name].push(track);
    //   });
    // };

    onMounted(() => {
       fetchPlaylists();
       fetchData();
       
      if (audioElement.value) {
        audioElement.value.addEventListener('timeupdate', updateSliderPosition);
      }
    });
    watch(audioElement, (newAudioElement, oldAudioElement) => {
      if (oldAudioElement) {
        oldAudioElement.removeEventListener('timeupdate', updateSliderPosition);
      }
      if (newAudioElement) {
        newAudioElement.addEventListener('timeupdate', updateSliderPosition);
      }
    });

    const watchPathChanges = () => {
      watchEffect(() => {
        fetchData();

      
      
        
      });
    };

    


const pauseAudio = () => {
  if (audioElement.value && !audioElement.value.paused) {
    audioElement.value.pause();
  }
};


onBeforeRouteLeave((to, from, next) => {
  pauseAudio();
  next();
});

    
    watchPathChanges();

   

    return {
      isPaused,
      selectedTrack,
      audioElement,
      sliderPosition,
      playTrack,
      rateSong,
      handlePlaybackToggle,
      handleMasterPlayClick,
      handleSeekbarChange,
      handleVolumeChange,
      updateAudioTime,
      updateSliderPositionvalue,
      tracks,
      fetchData,
      togglePlaylist,
      togglePlaylistDropdown,
      isInPlaylist,
      showPlaylistDropdown,
      userPlaylists,
      fetchPlaylists,
      isInCurrentPlaylist,
      currentTrackForDropdown,
      toggleOptionsDropdown,
      showOptionsDropdown,
      token,
      addToHistory,
      viewLyrics,
      showLyrics,
      currentTrackForLyrics,
      flagSong,
      filterOption,
      minRating,
      maxRating,
      flagStatus,
      originalTracks,
      applyFilter,
      revertFilter,
     
    };
  },
};
</script>


  <style>
 .user-home {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh; 
}

.tracks-section {
  margin-top: 30px;
  width: 80%;
  margin-left: 180px;
  margin-bottom: 80px;
  color: #000;
}

.track-list {
  list-style: none;
  padding: 0;
}

.track-item {
  border-bottom: 1px solid #ccc;
  padding: 5px;
  text-align:left;
}

.track-header {
  font-weight: bold;
}


.track-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.track-number,
.track-title,
.artist-name,
.plays,
.average-rating,
.rate-song,
.options,
.plus-icon {
  width: 100px;
  text-align: center;
  box-sizing: border-box; 
  margin: 0; 
  padding: 0;
}

.rate-song-input {
  width: 5%;
  text-align: center;
  box-sizing: border-box;
  margin: 0; 
  padding: 0; 
}
.options {
  cursor: pointer;
  font-size: 20px; 
}

.options-dropdown {
  position: absolute;
  top: 20%;
  left: 80%;
  transform: translate(-50%, -50%);
  background-color: #fff;
  border: 1px solid #ccc;
  padding: 10px;
  width: max-content;
}


.fa-plus {
  cursor: pointer;
}

.fa-play,
.fa-pause {
  color: #3498db;
}

.fa-music {
  color: #e74c3c;
}

.fa-star {
  color: #f39c12;
}

.fa-plus {
  color: #2ecc71;
}

.fa-flag {
  color: #e74c3c;
}
  .root-page {
    background-color: #f4f4f4; 
    padding: 20px;
    min-height: 100vh; 
  }
  
  .card-header {
    font-weight: bold;
  }
  
  .card-text {
    font-size: 16px;
  }
  
  .btn-light {
    background-color: #fff;
    color: #333;
  }

  .playlist-dropdown {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50%; 
  max-height: 80%; 
  overflow-y: auto;
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.playlist-dropdown ul {
  list-style: none;
  margin: 0;
  padding: 0;
}


.playlist-dropdown li {
  cursor: pointer;
  padding: 5px;
}

.playlist-dropdown span {
  display: flex;
  align-items: center;
}

.playlist-dropdown i {
  margin-left: 5px;
  color: green;
}
.playlist-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50%; 
  max-height: 80%; 
  overflow-y: auto;
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
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
