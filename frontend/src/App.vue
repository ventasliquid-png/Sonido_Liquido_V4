    <template>
      <Toast />
      <ProductosView />
    </template>

    <script setup lang="ts">
    // import Toast from 'primevue/toast'; // <-- ELIMINADO (Ahora es global)
    import ProductosView from './modulos/productos/views/ProductosView.vue'; // Ruta directa al módulo
    </script>

    <style>
    body { font-family: sans-serif; background-color: #f8f9fa; margin: 0; padding: 1rem; color: #495057; }
    .p-component { font-family: inherit; }
    </style>
    
