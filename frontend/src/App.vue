<!-- RUTA: frontend/src/App.vue (AÑADIR :key) -->
<template>
  <div :key="'app-root'"> <!-- AÑADIDO :key -->
    <Toast />
    <header>
      <h1 class="main-title">Sonido Líquido V4</h1>
    </header>
    <main class="main-content">
      <RubrosView />
    </main>
  </div>
</template>

<script setup lang="ts">
import RubrosView from './views/RubrosView.vue';
// Toast se asume global
</script>

<style>
/* ... estilos globales ... */
</style>