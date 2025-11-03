<template>
  <Toast />
  
  <TNO />
</template>

<script setup lang="ts">
// [INICIO] REPARACIÓN TAX-7 (Sello 2 - Jerarquía)

// Importamos el Layout TNO (Contenedor)
// Ruta asimilada del 'tree': frontend/src/components/layout/TNO.vue
import TNO from '@/components/layout/TNO.vue'; 

// Importamos el Toast (Servicio Global)
import Toast from 'primevue/toast';

// NO importamos RouterView aquí. Esa es la responsabilidad del TNO.
// [FIN] REPARACIÓN TAX-7
</script>

<style scoped>
/* Estilos de App.vue (generalmente mínimos) */
</style>