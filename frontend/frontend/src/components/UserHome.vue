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
    <div class="container">
  

    <div class="flash-card" v-for="album in albums" :key="album.id" @click="navigateToAlbum(album.title,album.id)">
      <h2>{{ album.title }}</h2>
      <p><strong>Artists:</strong></p>
      <ul>
        <li v-for="artist in album.artist_names" :key="artist">{{ artist }}</li>
      </ul>
    </div>
  </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import Player from './Player.vue';
import { useRouter } from 'vue-router';

export default {
  name: 'UserHome',
  components: {
    Player,
  },
  setup() {
    const isPaused = ref(true);
    const selectedTrack = ref(null);
    const albums = ref([]);
    const audioElement = ref(null);
    const sliderPosition = ref(0);
    const router = useRouter();
    const role = localStorage.getItem('role');
    const token = localStorage.getItem('token');

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

    const navigateToAlbum = (albumName,albumId) => {
      
      router.push({ name: 'album-tracks', params: { albumName,albumId } });
    };

    const fetchData = async () => {
  try {
    const apiEndpoint = 'http://127.0.0.1:5000/tracks/albums';
    const response = await fetch(apiEndpoint, {
      method: 'GET',
      headers: {
        'Authentication-Token': token // Include the token in the headers
      },
    });
    console.log('Token is '+ token);

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
        const data = await response.json();
        albums.value = data;
      
      } catch (error) {
        console.error('Error fetching tracks:', error);
      }
    };

   

    onMounted(() => {
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

   

    return {
      isPaused,
      selectedTrack,
      albums,
      audioElement,
      sliderPosition,
      playTrack,
      handlePlaybackToggle,
      handleMasterPlayClick,
      handleSeekbarChange,
      handleVolumeChange,
      updateAudioTime,
      updateSliderPositionvalue,
      navigateToAlbum,
      role,
      token
    };
  },
};
</script>


  <style>
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

  .container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  margin-bottom: 50px;
}

.flash-card {
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.flash-card h2 {
  margin-bottom: 10px;
}

.flash-card ul {
  list-style-type: none;
  padding: 0;
}

.flash-card ul li {
  margin-left: 20px;
}
  </style>
  