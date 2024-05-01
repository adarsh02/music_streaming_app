

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
      @fetchAgain="fetchAgain"
    />
    <div class="tracks-section">
      <h2 @click="editPlaylist">{{ playlist.name }}</h2>
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
     
      <ul class="track-list" v-if="tracks.length > 0">
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
            <span class="track-number" @click="navigatetoAlbum(track.album_name,track.album_id)">{{ track.order }}</span>
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
            <div v-if="showOptionsDropdown && currentTrackForDropdown === track.id" class="options-dropdown">
              <ul>
                <li @click="viewLyrics(track)">View Lyrics</li>
                <li @click="flagSong(track)">{{ track.is_flagged ? 'Unflag Song' : 'Flag Song' }}</li>
              </ul>
            </div>
            <i class="fas fa-plus plus-icon" @click="togglePlaylistDropdown(track)"></i>
            <i class="fas fa-minus remove-icon" @click="removeSong(track)"></i>
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
      <div v-else>
        <p>No songs added yet.</p>
      </div>
    </div>

    <div v-if="showPlaylistDialog" class="playlist-dialog">
      <button class="close-btn" @click="closeDialog">&times;</button>
      <label>Edit Playlist Title</label>
      <input v-model="newPlaylistName" placeholder="New Playlist Name" />
      <button @click="savePlaylist">Save</button>
      <button @click="deletePlaylist">Delete</button>
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
import Player from './Player.vue';
import { useRoute,useRouter } from 'vue-router';
import { onBeforeRouteLeave } from 'vue-router';



export default {
  name: 'PlaylistTrack',
  components: {
    Player
  },
 
  setup(props) {

    console.log('Album name'+props.albumName);


    const isPaused = ref(true);
    const showOptionsDropdown = ref(false);
    const selectedTrack = ref(null);
    const audioElement = ref(null);
    const sliderPosition = ref(0);
    const token = localStorage.getItem('token');
    const showPlaylistDropdown = ref(false);  
    const userPlaylists = ref([]);
    const showLyrics = ref(false); 
    const currentTrackForDropdown = ref(0);
    const showPlaylistDialog = ref(false);
    const newPlaylistName = ref('');
    const router = useRouter();
    const currentTrackForLyrics = ref('');
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

    const pauseAudio = () => {
  if (audioElement.value && !audioElement.value.paused) {
    audioElement.value.pause();
  }
};


onBeforeRouteLeave((to, from, next) => {
  pauseAudio(); 
  next();
});
    


     const viewLyrics=(track)=>{
      currentTrackForLyrics.value = track.lyrics;
      showLyrics.value = !showLyrics.value;
      

    };


    const navigatetoAlbum = (albumName,albumId)=>{
      router.push(`/album-tracks/${albumName}/${albumId}`);
      
    };
    

    const playlist = ref({});
    const tracks = ref([]);
    const route = useRoute();

    const fetchAgain = ()=>{
      fetchPlaylists();
    }

    const editPlaylist = () => {
      newPlaylistName.value = playlist.value.name;
      showPlaylistDialog.value = true;
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
        fetchPlaylistAndTracks();
        alert("Song rated successfully");
      } catch (error) {
        
        console.error(error);
      }
    };
    const toggleOptionsDropdown = (track) => {
  showOptionsDropdown.value = !showOptionsDropdown.value;
  currentTrackForDropdown.value = track.id;
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
    
    fetchPlaylistAndTracks();
    alert("Flag status updated successfully");
  } catch (error) {
    
    console.error(error);
  }
};

    const removeSong = async (track) => {
      try {
        const playlistId = playlist.value.id; 
        const trackId = track.id;

        
        const response = await fetch(`http://127.0.0.1:5000/tracks/playlists/remove-song/${playlistId}/${trackId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': localStorage.getItem('token'), 
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            
            alert('Removed track '+track.title+' from playlist');
            fetchPlaylistAndTracks();
          } else {
            console.error('Error removing song:', data.message);
          }
        } else {
          console.error('Error removing song:', response.status);
        }
      } catch (error) {
        console.error('Error removing song:', error);
      }
    };



    const savePlaylist = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/tracks/playlists/edit/${playlist.value.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authentication-Token': token,
          },
          body: JSON.stringify({
            name: newPlaylistName.value,
          }),
        });

        if (response.ok) {
          showPlaylistDialog.value = false;
          fetchAgain();
          fetchPlaylistAndTracks();
        } else {
          console.error('Error updating playlist name');
        }
      } catch (error) {
        console.error('Error updating playlist name:', error);
      }
    };

    const deletePlaylist = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/tracks/playlists/delete/${playlist.value.id}`, {
          method: 'DELETE',
          headers: {
            'Authentication-Token': token,
          },
        });

        if (response.ok) {
          showPlaylistDialog.value = false;
          router.push({ name: 'user_home' }); // Redirect to UserHome
        } else {
          console.error('Error deleting playlist');
        }
      } catch (error) {
        console.error('Error deleting playlist:', error);
      }
    };

    const closeDialog = () => {
      showPlaylistDialog.value = false;
    };
  
    const fetchPlaylistAndTracks = async () => {
    try {
        const token = localStorage.getItem('token');
        const userId = localStorage.getItem('userId');
        const playlistId = ref(route.params.playlistId);
        const playlistResponse = await fetch(`http://127.0.0.1:5000/tracks/playlists/getname/${playlistId.value}`, {
            method: 'GET',
            headers: {
                'Authentication-Token': token,
            },
        });
        const tracksResponse = await fetch(`http://127.0.0.1:5000/tracks/playlists/${playlistId.value}`, {
            method: 'GET',
            headers: {
                'Authentication-Token': token,
            },
        });

        if (playlistResponse.ok && tracksResponse.ok) {
            playlist.value = await playlistResponse.json();
            tracks.value = await tracksResponse.json();
            tracks.value = [...tracks.value].sort((a, b) => a.order - b.order);
            originalTracks.value = tracks.value;
        } else {
            console.error('Error fetching playlist and tracks');
        }

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
        console.error('Error fetching playlist and tracks:', error);
    }
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
        userPlaylists.value = data['playlists']; // Assuming your API response is an array of playlists
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
      addToHistory(track );
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
      fetchPlaylistAndTracks();
       fetchPlaylists();
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

    watch(() => route.params.playlistId, (newPlaylistId, oldPlaylistId) => {
      if (newPlaylistId !== oldPlaylistId) {
        fetchPlaylistAndTracks(newPlaylistId);
        closeDialog();

      }
    });

    return {
      isPaused,
      selectedTrack,
      audioElement,
      sliderPosition,
      playTrack,
      token,
      fetchPlaylistAndTracks,
      handlePlaybackToggle,
      handleMasterPlayClick,
      handleSeekbarChange,
      handleVolumeChange,
      updateAudioTime,
      updateSliderPositionvalue,
      tracks,
      togglePlaylist,
      togglePlaylistDropdown,
      isInPlaylist,
      showPlaylistDropdown,
      userPlaylists,
      fetchPlaylists,
      isInCurrentPlaylist,
      currentTrackForDropdown,
      playlist,
      fetchAgain,
      showPlaylistDialog,
      newPlaylistName,
      editPlaylist,
      savePlaylist,
      deletePlaylist,
      closeDialog,
      removeSong,
      navigatetoAlbum,
      rateSong,
      toggleOptionsDropdown,
      showOptionsDropdown,
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
      revertFilter
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

.options-dropdown ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.options-dropdown li {
  cursor: pointer;
  padding: 5px;
  font-weight: bold; 
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
  left: 100%;
  transform: translate(-50%, -50%);
  background-color: #fff;
  border: 1px solid #ccc;
  padding: 10px;
  width: max-content;
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
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  text-align: center;
}

.playlist-dialog label {
  display: block;
  margin-bottom: 8px;
}

.playlist-dialog input {
  width: 100%;
  padding: 8px;
  margin-bottom: 16px;
}

.playlist-dialog button {
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










  