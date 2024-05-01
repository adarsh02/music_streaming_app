// store.js
import { createStore } from 'vuex';

export default createStore({
  state() {
    return {
      user: {
        id:localStorage.getItem('userId') || null,
        // other user-related properties
      },
      playlists: [],
    };
  },
  mutations: {
    SET_USER(state, userId) {
      state.user.id = userId;
      
    },
    SET_PLAYLISTS(state, playlists) {
      state.playlists = playlists;
    },
    // other mutations related to user
  },
  actions: {
    async fetchPlaylists({ commit, state }) {
      try {
        const userId = state.user.id;
        const token=localStorage.getItem('token');

        const response = await fetch(`http://127.0.0.1:5000/user/playlists/${userId}`,{
          method: 'GET',
          headers: {
            'Authentication-Token': token // Include the token in the headers
          },
        });
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        commit('SET_PLAYLISTS', data);  // Corrected mutation name
      } catch (error) {
        console.error('Error fetching playlists:', error);
      }
    },
    // actions related to user
    setUserId({ commit }, userId) {
      commit('SET_USER', userId);
    },
  },
  getters: {
    // getters related to user
    playlists: state => state.playlists,
  },
});

