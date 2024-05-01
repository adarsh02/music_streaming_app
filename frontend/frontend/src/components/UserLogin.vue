<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <form @submit.prevent="loginUser" class="login-form">
          <h3 class="text-center mb-4">{{ loginType }} Login</h3>
          <div class="form-group">
            <label for="email">Email Address</label>
            <input v-model="email" type="email" class="form-control" id="email" name="email" placeholder="Enter email">
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input v-model="password" type="password" class="form-control" id="password" name="password" placeholder="Enter password">
          </div>
          <button type="submit" class="btn btn-primary btn-block">Login</button>
        </form>
        <div v-if="loginType !== 'Admin'" class="text-center mt-3">
          New user? <router-link to="/user_signup">Create an account</router-link>
        </div>
        <div class="text-center mt-3">
          <router-link to="/">Back to Home</router-link>
        </div>
        <div v-if="message" :class="messageClass" class="mt-3 text-center">{{ message }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserLogin',
  data() {
    return {
      email: '',
      password: '',
      message: '',
      messageClass: '',
    };
  },
  props: {
    loginType: String,
  },
  methods: {
    async loginUser() {
      try {
        let apiEndpoint = '';

        // Determine which API endpoint to use based on loginType
        if (this.loginType === 'User') {
          apiEndpoint = 'http://127.0.0.1:5000/auth/user_login';
        } else if (this.loginType === 'Admin') {
          apiEndpoint = 'http://127.0.0.1:5000/auth/admin_login';
        }

        const response = await fetch(apiEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          

          const user = data.user;

         
          console.log(user.id);

          localStorage.setItem('token', data.auth_token)
          localStorage.setItem('role', data.user.role)
          localStorage.setItem('userId', user.id);
          this.message = data.message;
          this.messageClass = 'text-success';
          
          if (this.loginType === 'User') {
            this.$router.push('user_home');
          } else if (this.loginType === 'Admin') {
            this.$router.push('admin_home');
          }
         

        } else {
          
          this.message = "Login failed. Please check your username and password.";
          this.messageClass = 'text-danger';
          alert('Login failed. Please check your username and password.');
        }
      } catch (error) {
        console.error(error);
      }
    },
  },
};
</script>

<style scoped>

.login-form {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.text-success {
  color: #28a745;
}

.text-danger {
  color: #dc3545;
}
</style>

