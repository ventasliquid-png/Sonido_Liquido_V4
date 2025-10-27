<!-- frontend/src/modulos/productos/views/ProductosView.vue (SIN COMENTARIOS EN TAGS) -->
<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <Button label="Nuevo Producto" icon="pi pi-plus" class="p-button-success" @click="abrirFormNuevo" />
      </template>
    </Toolbar>

    <TablaDatos
      :datos="store.productos"
      :columnas="columnasProductos"
      :cargando="store.estadoCarga"
      @editar-item="onEditarProducto"
      @eliminar-item="onConfirmarEliminar"
    />

    <ConfirmationModal
      v-model:visible="mostrarModalEliminar"
      titulo="Confirmar Eliminación"
      :message="`¿Está seguro que desea dar de baja el producto ${productoAEliminar?.nombre}?`"
      @confirmado="ejecutarEliminacion"
      @cancelado="cancelarEliminacion"
    />

    <ProductoForm
      v-model:visible="mostrarFormulario"
      :producto="store.productoSeleccionado"
      @guardar="onGuardarProducto"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useProductoStore } from '../store/useProductoStore';
import type { Producto } from '../models/productoModel'; // Asumiendo exportación del tipo/interfaz

// --- ARSENAL DEOU CANÓNICO ---
import TablaDatos from '@/components/TablaDatos.vue';
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue';
// --- FIN ARSENAL ---

import ProductoForm from '../components/ProductoForm.vue';

// 1. EL CEREBRO (Store)
const store = useProductoStore();

// Definición de columnas
const columnasProductos = ref([
  { field: 'sku', header: 'SKU' },
  { field: 'nombre', header: 'Nombre' },
  { field: 'precio_costo', header: 'Costo' },
  { field: 'precio_base_venta', header: 'Venta Base' },
  { field: 'baja_logica', header: 'Activo' },
]);

// Carga inicial
onMounted(() => {
  store.fetchProductos();
});

// 2. LÓGICA DE FORMULARIO
const mostrarFormulario = ref(false);

const abrirFormNuevo = () => {
  store.seleccionarProducto(null);
  mostrarFormulario.value = true;
};

const onEditarProducto = (producto: Producto) => {
  store.seleccionarProducto(producto);
  mostrarFormulario.value = true;
};

const onGuardarProducto = (productoData: Producto) => {
  store.guardarProducto(productoData);
  mostrarFormulario.value = false;
};

// 3. LÓGICA DE ELIMINACIÓN
const mostrarModalEliminar = ref(false);
const productoAEliminar = ref<Producto | null>(null);

const onConfirmarEliminar = (producto: Producto) => {
  productoAEliminar.value = producto;
  mostrarModalEliminar.value = true;
};

const ejecutarEliminacion = async () => {
  if (productoAEliminar.value && productoAEliminar.value.id) {
    await store.eliminarProducto(productoAEliminar.value.id);
  }
  cancelarEliminacion();
};

const cancelarEliminacion = () => {
  productoAEliminar.value = null;
  mostrarModalEliminar.value = false;
};
</script>

<style scoped>
.card {
    padding: 1rem;
}
</style>