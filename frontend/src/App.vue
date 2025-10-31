<template>
  <Toast /> 
  
  <main>
    <SubRubrosView />
  </main>
</template>

<script setup lang="ts">
console.log('--- BANDERA 5: App.vue <script setup> Ejecutando ---');

// Importamos el componente Toast
import Toast from 'primevue/toast'; 
// Importamos el nuevo módulo V12
import SubRubrosView from '@/modulos/subrubros/views/SubRubrosView.vue';
</script>

<style scoped>
main {
  padding: 1.5rem;
}
</style>