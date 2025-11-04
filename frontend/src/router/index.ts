import { createRouter, createWebHistory } from 'vue-router'
import RubrosView from '../views/RubrosView.vue'
import UnidadesMedidaView from '@/modulos/unidades_medida/views/UnidadesMedidaView.vue'

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
      path: '/unidades_medida',
      name: 'unidades_medida',
      component: UnidadesMedidaView
    }
  ]
})

export default router
