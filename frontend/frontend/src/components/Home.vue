<template>
  <div class="root-page">
    <!-- Title -->
    <h1 class="text-center mb-5">Welcome to Dawn FM</h1>
    
    <!-- User Login Section -->
    <div class="login-section">
      <div class="login-box user-login">
        <h2>User Login</h2>
        <p>Log in as a user to stream songs and register as a creator</p>
        <router-link to="/user_login" class="btn btn-primary">Login</router-link>
      </div>
    
      <!-- Admin Login Section -->
      <div class="login-box admin-login">
        <h2>Admin Login</h2>
        <p>Log in as an admin to manage Dawn.FM.</p>
        <router-link to="/admin_login" class="btn btn-primary">Login</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RootPage'
};
</script>

<style scoped>
.root-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #ff6699;
}

.login-section {
  display: flex;
  justify-content: center;
  gap: 30px;
}

.login-box {
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2); 
  background-color: #ffffff;
  text-align: center;
}

.login-box h2 {
  margin-bottom: 15px;
  color: #333333; 
}

.login-box p {
  margin-bottom: 30px;
  color: #666666; 
}

.btn-primary {
  background-color: #ff3366; 
  border-color: #ff3366; 
  color: #ffffff; 
  text-transform: uppercase;
  padding: 12px 24px;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #ff0044; 
}

h1 {
  margin-top: 0;
}
</style>
