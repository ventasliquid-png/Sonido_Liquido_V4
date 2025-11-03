// frontend/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';

// Importaciones canónicas de Vistas de módulos existentes
import RubrosView from '@/views/RubrosView.vue';
import SubRubrosView from '@/modulos/subrubros/views/SubRubrosView.vue';
import ProductosView from '@/modulos/productos/views/ProductosView.vue';

// Importación de la nueva Vista de Misión ST8
import UnidadesMedidaView from '@/modulos/unidades_medida/views/UnidadesMedidaView.vue';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            redirect: '/rubros'
        },
        // --- Rutas de Módulos Core ---
        {
            path: '/rubros',
            name: 'rubros',
            component: RubrosView,
            meta: { breadcrumb: 'Rubros' }
        },
        {
            path: '/subrubros',
            name: 'subrubros',
            component: SubRubrosView,
            meta: { breadcrumb: 'Sub-Rubros' }
        },
        {
            path: '/productos',
            name: 'productos',
            component: ProductosView,
            meta: { breadcrumb: 'Productos' }
        },
        // --- Nueva Ruta de Misión ST8 ---
        {
            path: '/unidades-medida',
            name: 'unidades-medida',
            component: UnidadesMedidaView,
            meta: { breadcrumb: 'Unidades de Medida' }
        }
    ]
});

export default router;