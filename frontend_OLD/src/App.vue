<template>
  <div class="card">
    <h1>Prueba de Aislamiento</h1>
    <p>Si este botón se ve estilizado, las librerías están bien.</p>

    <!-- Nuestro "Botón Violeta" -->
    <Button label="Ay" @click="decirAy" severity="secondary" />

  </div>
</template>

<script setup lang="ts">
// Solo importamos lo mínimo indispensable para la prueba
import Button from 'primevue/button';

const decirAy = () => {
  alert('Ay');
}
</script>

<style>
/* Mantenemos los estilos básicos para que la tarjeta se vea bien */
body { font-family: sans-serif; background-color: #f8f9fa; }
.card {
  max-width: 600px;
  margin: 5rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center; /* Centramos el botón */
}
</style>