import { createApp } from 'vue';
import App from './App.vue';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';

// === INICIO DE LA CONFIGURACIÓN CORRECTA Y DEFINITIVA PARA PRIMEVUE 4 ===

// 1. Importamos el "Preset" del tema. Es un objeto de JavaScript, no un CSS.
import Aura from '@primevue/themes/aura';

// 2. Importamos los íconos y la librería de layout. Esto no cambia.
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';

// === FIN DE LA CONFIGURACIÓN ===

const app = createApp(App);

// 3. Le decimos a PrimeVue que use el modo "sin estilo" y le aplicamos el tema que importamos.
app.use(PrimeVue, {
    unstyled: true, // Esta es la clave que faltaba.
    theme: {
        preset: Aura
    }
});

app.use(ToastService);
app.mount('#app');