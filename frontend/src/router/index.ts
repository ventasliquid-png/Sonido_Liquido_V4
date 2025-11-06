import { createRouter, createWebHistory } from 'vue-router'
// REPARACIÓN G-R-09: Apuntar a la nueva ruta modular
import RubrosView from '@/modulos/rubros/views/RubrosView.vue'
// La importación del archivo (filesystem) SÍ usa guion bajo
import UnidadesMedidaView from '@/modulos/unidades_medida/views/UnidadesMedidaView.vue'
import SubRubrosView from '@/modulos/subrubros/views/SubRubrosView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: RubrosView
    },
    {
      path: '/rubros',
      name: 'rubros',
      component: RubrosView
    },
    {
      path: '/subrubros',
      name: 'subrubros',
      component: SubRubrosView
    },
    {
      // CORRECCIÓN: La ruta URL (path) debe usar guion medio para coincidir con el menú
      path: '/unidades-medida',
      name: 'unidades_medida',
      component: UnidadesMedidaView
    }
  ]
})

export default router
