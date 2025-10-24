    // frontend/src/main.ts (Plan de Acción 1: Registro Global)
    import { createApp } from 'vue';
    import App from './App.vue';
    import PrimeVue from 'primevue/config';
    import ToastService from 'primevue/toastservice';
    import Aura from '@primevue/themes/aura';
    import 'primeicons/primeicons.css';
    import 'primeflex/primeflex.css';
    import { createPinia } from 'pinia';

    // --- INICIO MANIOBRA DE EVASIÓN: Importar Componentes Globalmente ---
    // Importamos aquí todos los componentes de PrimeVue que usan nuestros archivos
    import Button from 'primevue/button';
    import Column from 'primevue/column';
    import DataTable from 'primevue/datatable';
    import Dialog from 'primevue/dialog';
    import InputNumber from 'primevue/inputnumber';
    import InputText from 'primevue/inputtext';
    import Message from 'primevue/message';
    import ProgressBar from 'primevue/progressbar';
    import Textarea from 'primevue/textarea';
    import Toast from 'primevue/toast';
    import Toolbar from 'primevue/toolbar';
    // --- FIN MANIOBRA DE EVASIÓN ---

    const pinia = createPinia();
    const app = createApp(App);

    app.use(PrimeVue, { theme: { preset: Aura } });
    app.use(ToastService);
    app.use(pinia);

    // --- INICIO MANIOBRA DE EVASIÓN: Registrar Componentes Globalmente ---
    // Ahora, los componentes como <Button> o <Toolbar> estarán
    // disponibles en CUALQUIER .vue sin necesidad de importarlos.
    app.component('Button', Button);
    app.component('Column', Column);
    app.component('DataTable', DataTable);
    app.component('Dialog', Dialog);
    app.component('InputNumber', InputNumber);
    app.component('InputText', InputText);
    app.component('Message', Message);
    app.component('ProgressBar', ProgressBar);
    app.component('Textarea', Textarea);
    app.component('Toast', Toast);
    app.component('Toolbar', Toolbar);
    // --- FIN MANIOBRA DE EVASIÓN ---

    app.mount('#app');
    

