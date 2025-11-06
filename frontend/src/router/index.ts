// --- INICIO BLOQUE IVA-TNO-01 (R3) (Reparación Manual) ---
// frontend/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

// --- REPARACIÓN G-R-20: Importar el Layout TNO ---
import TNO from '@/components/layout/TNO.vue'

// Rutas de Módulos
import RubrosView from '@/modulos/rubros/views/RubrosView.vue'
import SubRubrosView from '@/modulos/subrubros/views/SubRubrosView.vue'
import UnidadesMedidaView from '@/modulos/unidades_medida/views/UnidadesMedidaView.vue'
import IvaView from '@/modulos/condiciones_iva/views/IvaView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // --- REPARACIÓN G-R-20: Ruta padre TNO ---
      path: '/',
      component: TNO, 
      children: [
        {
          path: '', // Home (Rubros)
          name: 'home',
          component: RubrosView 
        },
        {
          path: 'rubros', // Ruta explícita (alias de home)
          name: 'rubros',
          component: RubrosView
        },
        {
          path: 'subrubros',
          name: 'subrubros',
          component: SubRubrosView
        },
        {
          path: 'unidades-medida', 
          name: 'unidades-medida',
          component: UnidadesMedidaView 
        },
        // --- INTEGRACIÓN HITO F1-50 (IVA) ---
        {
          path: 'condiciones-iva',
          name: 'condiciones-iva',
          component: IvaView
        }
        // --- FIN INTEGRACIÓN ---
      ]
    }
  ]
})

export default router
// --- FIN BLOQUE IVA-TNO-01 (R3) ---