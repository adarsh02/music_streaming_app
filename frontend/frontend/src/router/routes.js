import { createRouter, createWebHistory } from 'vue-router';

import RootPage from '../components/Home.vue';
import UserLogin from '../components/UserLogin.vue';
import UserSignup from '../components/UserSignup.vue';

import UserHome from '../components/UserHome.vue';
import AlbumTracks from '../components/AlbumTracks.vue';
import PlaylistTrack from '../components/PlaylistTrack.vue'
import AlbumManagement from '../components/AlbumManagement.vue'
import SongManagement from '../components/SongManagement.vue'
import AdminHome from '../components/AdminHome.vue'


const routes = [
  {
    path: '/user_login',
    name: 'user_login',
    component: UserLogin,
    props: {
      loginType: 'User',
    }
  },
  {
    path:'/user_home',
    component:UserHome,
    name:'user_home',
    meta: { requiresAuth: true, adminOnly: false }
  },
  {
    path: '/',
    component:RootPage,
    name:'root'
  },
  {
    path:'/user_signup',
    component:UserSignup,
    name:'user_signup'
  },
  {
    path: '/admin_home',
    name: 'AdminHome',
    component: AdminHome,
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path:'/admin_login',
    component:UserLogin,
    name:'admin_login',
    props: {
      loginType: 'Admin',
    }
  },
  {
    path: '/album-tracks/:albumName/:albumId',
    name: 'album-tracks',
    component: AlbumTracks,
    props: route => ({
      albumName: route.params.albumName,
      albumId: route.params.albumId
    }),
    meta: { requiresAuth: true}
  },
  {
    path: '/playlist/:playlistId',
    name: 'playlist-track',
    component: PlaylistTrack,
    meta: { requiresAuth: true}
  },
  {
    path:'/creator_mode',
    component:AlbumManagement,
    name:'creator_mode',
    props:{
      type:'Creator'
    },
    meta: { requiresAuth: true, adminOnly: false }
  },
  {
    path:'/admin_album_management',
    component:AlbumManagement,
    name:'admin_album_management',
    props:{
      type:'Admin'
    },
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/creator_mode/album/:albumId',
    name: 'song-management',
    component: SongManagement,
    props:{
      type:'Creator'
    },
    meta: { requiresAuth: true, adminOnly: false }
  },
  {
    path: '/admin_song_management/album/:albumId',
    name: 'admin_song_management',
    component: SongManagement,
    props:{
      type:'Admin'
    },
    meta: { requiresAuth: true, adminOnly: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// const checkTokenExpiry = async () => {
//   // Check if the token exists in localStorage
//   const authToken = localStorage.getItem('token');
//   if (!authToken) {
//     // If token doesn't exist, return without performing the check
//     return;
//   }

//   try {
//     const response = await fetch('http://127.0.0.1:5000/auth/check_expiry', {
//       method: 'GET',
//       headers: {
//         'Content-Type': 'application/json',
        
//       }
//     });

//     if (response.ok) {
//       const data = await response.json();
//       if (data.expired) {
//         localStorage.clear();
//       }
//     } else {
//       console.error('Failed to check token expiry:', response.statusText);
//     }
//   } catch (error) {
//     console.error('An error occurred while checking token expiry:', error);
//   }
// };



router.beforeEach((to, from, next) => {
  const authToken = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  //checkTokenExpiry();

  // Check if the route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authToken) {
      // If authToken does not exist, redirect to login page
      next({
        name: 'user_login',
        query: { redirect: to.fullPath }
      });
    } else {
      // If authToken exists
      if (role === 'admin' && !to.meta.adminOnly) {
        // If the user is an admin and trying to access non-admin route, redirect to AdminHome
        next({ name: 'AdminHome' });
      } else if (role === 'user' && to.meta.adminOnly) {
        // If the user is a user and trying to access admin-only route, redirect to user_home
        next({ name: 'user_home' });
      } else {
        // Otherwise, proceed to the route
        next();
      }
    }
  } else {
    // If the route does not require authentication, proceed to the route
    if (authToken) {
      // If the user is already logged in and trying to access login page or signup page, redirect to respective home page
      next({ name: role === 'user' ? 'user_home' : 'AdminHome' });
    } else if (!authToken && to.name === '') {
      // If the user is not logged in and trying to access root path, proceed to the route
      next();
    } else {
      // For other cases, proceed to the route
      next();
    }
  }
});






export default router;