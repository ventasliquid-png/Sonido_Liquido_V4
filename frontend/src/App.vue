<template>
  <Toast />
  
  <router-view />
</template>

<script setup lang="ts">
// [INICIO] REPARACIÓN G-R-23
// Importamos solo lo necesario
import { RouterView } from 'vue-router';
import Toast from 'primevue/toast';
// NO importamos TNO.vue aquí.
// [FIN] REPARACIÓN G-R-23
</script>

<style scoped>
/* Estilos mínimos */
</style>