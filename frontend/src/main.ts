// frontend/src/main.ts (CON BLINDAJE PROFILÁCTICO)
// Importaciones estándar
import { createApp } from 'vue';
import App from './App.vue';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import Aura from '@primevue/themes/aura';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';
import { createPinia } from 'pinia';

// Componentes Globales (Maniobra de Evasión)
import Button from 'primevue/button';
import Toolbar from 'primevue/toolbar';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Toast from 'primevue/toast';
// import InputNumber from 'primevue/inputnumber'; // Descomentar si se usa

// Servicio de Notificación
import notificationService from './services/notificationService';

console.log(`--- [${new Date().toISOString()}] INICIANDO EJECUCIÓN main.ts ---`);

// --- INICIO DEL PROTOCOLO "SELLO ÚNICO" ---
if (!document.getElementById('app')?.dataset.vueMounted) {
  console.log('--- main.ts: No hay instancia previa. Creando y montando App Vue...');

  const app = createApp(App);
  const pinia = createPinia();

  app.use(pinia);
  app.use(PrimeVue, {
      theme: {
          preset: Aura
      }
  });
  app.use(ToastService);

  // Inicializar NotificationService DESPUÉS de app.use(ToastService)
  const primevueToastService = app.config.globalProperties.$toast;
  if (primevueToastService) {
      notificationService.initialize(primevueToastService);
      console.log('--- main.ts: NotificationService Inicializado.'); // Log añadido
  } else {
      console.error("Error crítico: No se pudo obtener $toast para inicializar NotificationService.");
  }

  // Registro Global
  app.component('Button', Button);
  app.component('Toolbar', Toolbar);
  app.component('Dialog', Dialog);
  app.component('InputText', InputText);
  app.component('Textarea', Textarea);
  app.component('DataTable', DataTable);
  app.component('Column', Column);
  app.component('Tag', Tag);
  app.component('Toast', Toast);
  // app.component('InputNumber', InputNumber); // Descomentar si se usa

  // --- INICIO DE BLINDAJE PROFILÁCTICO (Doctrina Grok) ---
  // Manejador de errores global de Vue.
  // Captura errores de renderizado silenciosos (como TypeErrors en templates)
  // y los fuerza a aparecer en la consola.
  app.config.errorHandler = (err, instance, info) => {
    console.error("--- ERROR GLOBAL DE VUE CAPTURADO ---");
    console.error("Error:", err);
    console.log("Instancia:", instance); // Log cambiado a console.log para mejor visibilidad del objeto
    console.log("Información de Vue:", info); // Log cambiado a console.log
    console.error("--------------------------------------");
  };
  // --- FIN DE BLINDAJE ---

  app.mount('#app');

  // Marcamos el div #app para que este script no se vuelva a ejecutar
  try {
      const appDiv = document.getElementById('app');
      if (appDiv) {
          appDiv.setAttribute('data-vue-mounted', 'true');
          console.log('--- main.ts: Atributo data-vue-mounted establecido.');
      } else {
          console.error('--- main.ts: No se encontró #app para establecer data-vue-mounted.');
      }
  } catch (e) {
      console.error('--- main.ts: Error al establecer data-vue-mounted:', e);
  }

} else {
  console.warn(`--- [${new Date().toISOString()}] main.ts: ADVERTENCIA. Instancia de App ya montada detectada por data-vue-mounted. Se ha prevenido una re-ejecución.`);
}
// --- FIN DEL PROTOCOLO "SELLO ÚNICO" ---

console.log(`--- [${new Date().toISOString()}] FIN EJECUCIÓN main.ts ---`);