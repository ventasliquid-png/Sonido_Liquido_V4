<script setup lang="ts">
import { RouterView } from 'vue-router';
import TNO from '@/components/layout/TNO.vue';
import Toast from 'primevue/toast';
</script>

<template>
  <div style="display: flex;">
    <div style="width: 250px; padding: 20px; border-right: 1px solid var(--surface-border);">
        <TNO />
    </div>

    <div style="flex-grow: 1; padding: 20px;">
        <RouterView />
    </div>
    
    <Toast position="top-right" />
  </div>
</template>

<style scoped>
/* Sin estilos aquí, se usan estilos globales o PrimeFlex */
</style>