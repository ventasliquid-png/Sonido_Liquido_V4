<!-- frontend/src/components/TestImport.vue -->
<template>
  <div style="padding: 2rem; border: 1px solid green; margin: 2rem;">
    <p>Componente TestImport cargado con éxito usando alias '@'.</p>
    <Button label="Botón PrimeVue funciona" severity="success" />
  </div>
</template>

<script setup lang="ts">
// Importamos solo UN componente de PrimeVue para probar node_modules
import Button from 'primevue/button';
</script>