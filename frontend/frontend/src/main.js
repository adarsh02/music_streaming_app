import { createApp } from 'vue';
import App from './App.vue';
import router from './router/routes.js';
import store from './store.js';

const app = createApp(App);


app.mixin({
  data() {
    return {
      has_changed: true,
    };
  },
  watch: {
    $route() {
      this.has_changed = !this.has_changed;
    },
  },
});

app.use(router);
app.use(store); 
app.mount('#app');
