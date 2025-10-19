import { createApp } from 'vue'
import App from './App.vue'
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice'; // Necesario para que el Heraldo funcione

const app = createApp(App);
app.use(PrimeVue);
app.use(ToastService); // Añadimos el servicio de Toast
app.mount('#app');