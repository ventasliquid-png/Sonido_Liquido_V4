// frontend/src/router/index.ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

// --- VISTAS ASIMILADAS DEL MAPA DE TERRENO ---
// Estas rutas se basan en la estructura de archivos existente.
import RubrosView from '@/views/RubrosView.vue';
import SubRubrosView from '@/modulos/subrubros/views/SubRubrosView.vue';
import ProductosView from '@/modulos/productos/views/ProductosView.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/rubros' // Redirigir a una ruta por defecto (Rubros)
  },
  {
    path: '/rubros',
    name: 'Rubros',
    component: RubrosView
  },
  {
    path: '/subrubros',
    name: 'SubRubros',
    component: SubRubrosView
  },
  {
    path: '/productos',
    name: 'Productos',
    component: ProductosView
  }
  // Futuras rutas de la Operación Patrón V2.3 se integrarán aquí.
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;