<template>
  <Toast /> 

  <TNO />

  <main class="tno-contenido">
    <router-view />
  </main>
</template>

<script setup lang="ts">
console.log('--- App.vue (Refactor TNO) <script setup> Ejecutando ---');

// Importamos el componente Toast (Servicio Global)
import Toast from 'primevue/toast'; 

// Importamos el nuevo TNO (Tablero de Navegación de Obra)
import TNO from '@/components/layout/TNO.vue';

// Importamos el RouterView
import { RouterView } from 'vue-router';

// Las vistas específicas (SubRubrosView, RubrosView) ya no se importan aquí.
// El Router (index.ts) gestiona su carga.

</script>

<style scoped>
/* El padding se mueve al contenedor de contenido para dejar el TNO fijo */
.tno-contenido {
  margin-left: 250px; /* Ancho exacto del .tno-sidebar */
  padding: 1.5rem;
  width: calc(100% - 250px); /* Ajuste del ancho restante */
}
</style>