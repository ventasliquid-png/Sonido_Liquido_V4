<template>
    <div class="card p-4">
        <div class="text-xl font-bold mb-4">Operación Patrón V2.3</div>
        <div class="menu-list">
            
            <router-link to="/rubros" class="menu-item" active-class="active">
                <i class="pi pi-box mr-2"></i>
                Rubros
            </router-link>

            <router-link to="/subrubros" class="menu-item" active-class="active">
                <i class="pi pi-tags mr-2"></i>
                Sub-Rubros
            </router-link>

            <router-link to="/productos" class="menu-item" active-class="active">
                <i class="pi pi-shopping-bag mr-2"></i>
                Productos
            </router-link>

            <router-link to="/unidades-medida" class="menu-item" active-class="active">
                <i class="pi pi-balance-scale mr-2"></i>
                Unidades de Medida
            </router-link>
            
        </div>
        <Toast position="top-right" />
    </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { RouterLink } from 'vue-router';
import Toast from 'primevue/toast';

// Props típicos para componentes de layout, aunque no se usen aquí.
defineProps({
    title: {
        type: String,
        default: 'Menú Principal'
    }
});

// Nota: Los estilos canónicos deben ser importados o definidos globalmente.
// Aquí se incluyen estilos mínimos para asegurar visibilidad si no hay estilos globales.
</script>

<style scoped>
.menu-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    border-radius: 6px;
    text-decoration: none;
    color: var(--text-color);
    transition: background-color 0.2s;
}

.menu-item:hover {
    background-color: var(--surface-hover);
}

.menu-item.active {
    background-color: var(--primary-color);
    color: var(--primary-color-text);
    font-weight: bold;
}
</style>