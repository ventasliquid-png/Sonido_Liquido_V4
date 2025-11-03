<template>
  <div class="tno-layout">
    <aside class="tno-sidebar">
      <nav class="tno-menu">
        
        <router-link to="/">Rubros</router-link>
        <router-link to="/subrubros">SubRubros</router-link>
        <router-link to="/unidades-medida">Unidades de Medida</router-link>
      
      </nav>
    </aside>

    <main class="tno-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
</script>

<style scoped>
/* Estilos de layout (Ajustar según su diseño) */
.tno-layout {
  display: flex;
  min-height: 100vh;
}
.tno-sidebar {
  width: 220px;
  background-color: #f4f4f4; /* (Color de ejemplo) */
  border-right: 1px solid #ddd;
}
.tno-content {
  flex-grow: 1;
  padding: 1rem;
}
.tno-menu a {
  display: block;
  padding: 10px 15px;
  text-decoration: none;
  color: #333;
}
.tno-menu a:hover {
  background-color: #eee;
}
.router-link-active {
  font-weight: bold;
  background-color: #e0e0e0;
}
</style>