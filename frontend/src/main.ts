// frontend/src/main.ts (ESTABILIZADO TAX-5)
console.log('--- BANDERA 1: main.ts Ejecutando (Nivel 0) ---');

// Importaciones estándar
import { createApp } from 'vue';
import App from './App.vue';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
// --- CORRECCIÓN CRÍTICA DE CSS Y THEMES ---
// Se debe usar la importación directa, no la ruta fallida 'primevue/resources/themes/...'
import Aura from '@primevue/themes/aura'; 
// --- FIN CORRECCIÓN ---
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';
import { createPinia } from 'pinia';
import Tooltip from 'primevue/tooltip'; 

// --- INICIO MISION F1: TNO ---
import router from './router'; 
// --- FIN MISION F1 ---

// Componentes Globales
import Button from 'primevue/button';
import Toolbar from 'primevue/toolbar';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Toast from 'primevue/toast';
// --- NUEVO COMPONENTE: Requerido por el nuevo ABM ---
import InputNumber from 'primevue/inputnumber'; 

// Servicio de Notificación
import notificationService from './services/notificationService';

console.log(`--- [${new Date().toISOString()}] INICIANDO EJECUCIÓN main.ts ---`);

// --- INICIO DEL PROTOCOLO "SELLO ÚNICO" ---
if (!document.getElementById('app')?.dataset.vueMounted) {
  console.log('--- main.ts: No hay instancia previa. Creando y montando App Vue...');

  console.log('--- BANDERA 2: main.ts antes de createApp() ---');
  const app = createApp(App);
  console.log('--- BANDERA 3: main.ts DESPUÉS de createApp() ---');

  const pinia = createPinia();

  app.use(pinia);
  app.use(PrimeVue, {
      theme: {
          preset: Aura // Uso del tema importado
      }
  });
  app.use(ToastService);
  app.directive('tooltip', Tooltip);
  
  // Instalar el router
  app.use(router);
  console.log('--- main.ts: Misión F1 (TNO) -> vue-router instalado.');
  
  // --- CORRECCIÓN CRÍTICA DE NOTIFICATION SERVICE ---
  // Se garantiza que el servicio esté listo antes de usarlo.
  const primevueToastService = app.config.globalProperties.$toast;
  if (primevueToastService) {
      notificationService.initialize(primevueToastService);
      console.log('--- main.ts: NotificationService Inicializado (Corrección V2.3).');
  } else {
      console.error("Error crítico: No se pudo obtener $toast para inicializar NotificationService.");
  }
  // --- FIN CORRECCIÓN ---
  
  // Registro de Componentes Globales (Asegurando que Button/Dialog resuelvan)
  app.component('Button', Button);
  app.component('Toolbar', Toolbar);
  app.component('Dialog', Dialog);
  app.component('InputText', InputText);
  app.component('Textarea', Textarea);
  app.component('DataTable', DataTable);
  app.component('Column', Column);
  app.component('Tag', Tag);
  app.component('Toast', Toast);
  app.component('InputNumber', InputNumber); // Nuevo componente para ST9

  // --- Montaje de la App ---
  app.mount('#app');
  console.log('--- BANDERA 4: main.ts DESPUÉS de app.mount() ---');


} else { 
    console.warn('--- main.ts: DETECTADA INSTANCIA PREVIA DE VUE. Montaje abortado para prevenir HMR duplicado.');
}

// (Código para setear data-vue-mounted)
const appElement = document.getElementById('app');
if (appElement && !appElement.dataset.vueMounted) {
    appElement.dataset.vueMounted = 'true';
    console.log('--- main.ts: Atributo data-vue-mounted establecido.');
}

console.log(`--- [${new Date().toISOString()}] FIN EJECUCIÓN main.ts ---`);