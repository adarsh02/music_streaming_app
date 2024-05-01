<template>
  <div class="dashboard-container">
    <nav class="navbar">
      <div class="navbar-left">
        <router-link to="/admin_album_management" class="navbar-label">Album Management</router-link>
      </div>
      <router-link to="/user_home">
        <img src="@/assets/logo.png" alt="Logo" class="logo" />
      </router-link>
      <div class="navbar-right">
        <button class="logout-button" @click="logout">Log out</button>
      </div>
    </nav>
    <div class="container">
      <h1>Welcome to the Management Console</h1>

      <div class="stats-section">
        <div class="stats-card">
          <h2>Total Users with Role User</h2>
          <p>{{ stats.total_users_user_role }}</p>
        </div>

        <div class="stats-card">
          <h2>Total Users with Role Creator</h2>
          <p>{{ stats.total_users_creator_role }}</p>
        </div>

        <div class="stats-card">
          <h2>Total Albums</h2>
          <p>{{ stats.total_albums }}</p>
        </div>

        <div class="stats-card">
          <h2>Total Genres</h2>
          <p>{{ stats.total_genres }}</p>
        </div>

        <div class="stats-card">
          <h2>Total Languages</h2>
          <p>{{ stats.total_languages }}</p>
        </div>
      </div>

      <div class="top-songs-container">
        <div class="top-songs-section">
          <h2>Top 10 Songs with Highest Stream Count</h2>
          <div v-for="song in stats.top_songs" :key="song.title" class="song-item">
            <p><strong>Title:</strong> {{ song.title }}</p>
            <p><strong>Artist:</strong> {{ song.artist }}</p>
            <p><strong>Album:</strong> {{ song.album }}</p>
            <p><strong>Stream Count:</strong> {{ song.stream_count }}</p>
          </div>
        </div>

        <div class="top-rated-songs-section">
          <h2>Top 10 Songs with Highest Average Rating</h2>
          <div v-for="song in stats.top_rated_songs" :key="song.title" class="song-item">
            <p><strong>Title:</strong> {{ song.title }}</p>
            <p><strong>Artist:</strong> {{ song.artist }}</p>
            <p><strong>Album:</strong> {{ song.album }}</p>
            <p><strong>Average Rating:</strong> {{ song.average_rating }}</p>
          </div>
        </div>
      </div>

      <div class="add-artist-section">
        <h2>Add New Artist</h2>
        <form @submit.prevent="addArtist" class="add-artist-form">
          <label for="artistName">Artist Name:</label>
          <input type="text" id="artistName" v-model="newArtistName" required />
          <button type="submit" class="add-artist-button">Add Artist</button>
        </form>
      </div>
    </div>
  </div>
</template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import router from '@/router/routes';
  
  export default {
    name: 'AdminHome',
    setup() {
      const stats = ref({});
      const newArtistName = ref('');
  
      const fetchData = async () => {
        try {
          const response = await fetch('http://127.0.0.1:5000/auth/stats');
          if (!response.ok) {
            throw new Error('Failed to fetch statistics');
          }
          const data = await response.json();
          stats.value = data;
        } catch (error) {
          console.error(error);
        }
      };

      const logout = () => {
      // Clear local storage
      localStorage.clear();
      
      // Navigate to '/user_login'
      router.push('/admin_login');
    };

    const addArtist = async () => {
  try {
    const userId = localStorage.getItem('userId');
    const response = await fetch('http://127.0.0.1:5000/auth/add_artist', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: newArtistName.value,
        added_by: userId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to add artist');
    }

    // Clear the input field after successful addition
    newArtistName.value = '';
    
    // Fetch updated statistics after adding the artist
    await fetchData();

    
    alert('Artist successfully added');
  } catch (error) {
    console.error(error);

    
    alert('Unable to add artist');
  }
};

  
      onMounted(() => {
        fetchData();
      });
  
      return {
        stats,
        addArtist,
        newArtistName,
        logout
      };
    }
  };
  </script>
  
  <style scoped>
  .root-page {

 margin-bottom: 80px;
}
  .dashboard-container {
    background-color: #f5f5f5;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    font-family: Arial, sans-serif;
  }

  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    background-color: #333;
    color: white;
  }

  .navbar-label {
    cursor: pointer;
    font-size: 18px;
    text-decoration: none;
    color: white;
  }

  .logo {
    width: 100px;
    height: 50px;
  }

  .logout-button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background-color: #dc3545;
    color: white;
    cursor: pointer;
    font-size: 16px;
  }

  .container {
    width: 100%;
    max-width: 800px;
    margin: 20px auto;
    padding: 0 20px;
  }

  h1 {
    text-align: center;
    font-size: 28px;
    margin-bottom: 30px;
    color: #333;
  }

  .stats-section {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 40px;
  }

  .stats-card {
    flex: 1 1 calc(50% - 20px);
    background-color: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .stats-card h2 {
    margin-bottom: 10px;
    color: #333;
    font-size: 20px;
  }

  .top-songs-container {
    display: flex;
    gap: 20px;
  }

  .top-songs-section,
  .top-rated-songs-section {
    flex: 1;
  }

  .top-songs-section h2,
  .top-rated-songs-section h2 {
    margin-bottom: 20px;
    color: #333;
    font-size: 24px;
  }

  .song-item {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .song-item p {
    margin: 5px 0;
  }

  .add-artist-section {
    margin-top: 40px;
  }

  .add-artist-form {
    display: flex;
    align-items: center;
    margin-bottom: 40px;
  }

  .add-artist-form label {
    margin-right: 10px;
    font-size: 18px;
    color: #333;
  }

  .add-artist-form input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 16px;
  }

  .add-artist-button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background-color: #007bff;
    color: white;
    cursor: pointer;
    font-size: 16px;
  }
</style>