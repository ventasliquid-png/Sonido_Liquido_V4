import { createRouter, createWebHistory } from 'vue-router'

// Ruta del Layout (Contenedor TNO)
import TNO from '@/components/layout/TNO.vue' 

// Ruta Raíz (Hijo por defecto)
import RubrosView from '@/views/RubrosView.vue' 

// Ruta Módulo SubRubros
import SubRubrosView from '@/modulos/subrubros/views/SubRubrosView.vue'

// Ruta Módulo (Hito F1-50)
import UnidadesMedidaView from '@/modulos/unidades_medida/views/UnidadesMedidaView.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: TNO, // El TNO es el componente padre
      children: [
        {
          path: '', // La ruta raíz (hija)
          name: 'home',
          component: RubrosView // Carga RubrosView dentro del TNO
        },
        {
          path: 'subrubros',
          name: 'subrubros',
          component: SubRubrosView
        },
        {
          path: 'unidades-medida', // La ruta del hito
          name: 'unidades-medida',
          component: UnidadesMedidaView 
        }
      ]
    }
  ]
})

// Esta línea debe estar sola al final.
export default router