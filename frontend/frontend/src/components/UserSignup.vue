<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <form @submit.prevent="signupUser" class="signup-form">
          <h3 class="text-center mb-4">{{ signupType }} Signup</h3>
          <div class="form-group">
            <label for="email">Email Address</label>
            <input v-model="email" type="email" class="form-control" id="email" name="email" placeholder="Enter email" required>
          </div>
          <div class="form-group">
            <label for="username">User name</label>
            <input v-model="username" type="text" class="form-control" id="username" name="username" placeholder="Enter user name" required>
          </div>
          <div class="form-group">
            <label for="password1">Password</label>
            <input v-model="password1" type="password" class="form-control" id="password1" name="password1" placeholder="Enter password" required>
          </div>
          <div class="form-group">
            <label for="password2">Confirm Password</label>
            <input v-model="password2" type="password" class="form-control" id="password2" name="password2" placeholder="Confirm password" required>
          </div>
          <!-- Add other form fields as needed for signup -->
          <button type="submit" class="btn btn-primary btn-block">Signup</button>
        </form>
        <div class="mt-3 text-center">
          <router-link to="/user_login">Already have an account? Login here</router-link>
        </div>
        <div v-if="message" :class="messageClass" class="mt-3 text-center">{{ message }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserSignup',
  data() {
    return {
      email: '',
      username: '',
      password1: '',
      password2: '',
      message: '',
      messageClass: '',
      
    };
  },
  props: {
    signupType: String,
  },
  methods: {
    async signupUser() {
      try {
        let apiEndpoint = 'http://127.0.0.1:5000/auth/sign_up';
        const response = await fetch(apiEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: this.email,
            username: this.username,
            password1: this.password1,
            password2: this.password2,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            this.message = data.message;
            this.messageClass = 'text-success';
            alert('Account created successfully');
            this.$router.push('user_login');
          } else {
            this.message = data.message;
            this.messageClass = 'text-danger';
            alert('Sign up failed. ' + data.message);
          }
        } else {
          const data = await response.json();
          this.message = data.message;
          this.messageClass = 'text-danger';
          alert('Sign up failed. ' + data.message);
        }
      } catch (error) {
        console.error(error);
      }
    },
  },
};
</script>

<style scoped>

.signup-form {
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
