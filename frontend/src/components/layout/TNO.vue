<template>
  <nav class="tno-sidebar">
    <h1 class="tno-titulo">Operación Patrón V2.3</h1>
    <ul class="tno-lista">
      <li>
        <router-link to="/rubros" class="tno-enlace">
          <i class="pi pi-tags"></i>
          <span>Rubros</span>
        </router-link>
      </li>
      <li>
        <router-link to="/subrubros" class="tno-enlace">
          <i class="pi pi-sitemap"></i>
          <span>Sub-Rubros</span>
        </router-link>
      </li>
      <li>
        <router-link to="/productos" class="tno-enlace">
          <i class="pi pi-box"></i>
          <span>Productos</span>
        </router-link>
      </li>
      </ul>
  </nav>
</template>

<script setup lang="ts">
// TNO (Tablero de Navegación de Obra) - Misión F1
// Rol: Navegación principal.
import { RouterLink } from 'vue-router';
</script>

<style scoped>
.tno-sidebar {
  width: 250px;
  background-color: #f8f9fa; /* Color de obra neutro */
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  border-right: 1px solid #dee2e6;
  padding: 1.5rem;
  z-index: 99; /* Asegura que esté sobre el contenido pero debajo de modales */
}

.tno-titulo {
  font-size: 1.25rem;
  font-weight: 600;
  color: #343a40;
  margin-bottom: 2rem;
}

.tno-lista {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tno-lista li {
  margin-bottom: 0.5rem;
}

.tno-enlace {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  color: #495057;
  transition: background-color 0.2s, color 0.2s;
}

.tno-enlace i {
  margin-right: 0.75rem;
  font-size: 1.1rem;
}

.tno-enlace span {
  font-weight: 500;
}

.tno-enlace:hover {
  background-color: #e9ecef;
}

/* Estilo para el enlace activo */
.router-link-active,
.router-link-exact-active {
  background-color: #e0e7ff; /* Un color de acento sutil (Aura) */
  color: #4f46e5; /* Color primario de Aura */
}
</style>