<!-- frontend/src/modulos/productos/views/ProductosView.vue -->
<template>
  <div class="card">
    <!-- Toast debe estar presente en App.vue o layout principal para funcionar globalmente -->
    <Toolbar class="mb-4">
      <template #start>
        <!-- Los componentes Toolbar y Button funcionan por registro global en main.ts -->
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

    <!-- Componente ConfirmationModal con props y eventos estándar asumidos -->
    <ConfirmationModal
      v-model:visible="mostrarModalEliminar"
      :message="`¿Está seguro que desea dar de baja el producto ${productoAEliminar?.nombre}?`"
      @confirm="ejecutarEliminacion"
      @cancel="cancelarEliminacion"
      icon="pi pi-exclamation-triangle"
      header="Confirmar Eliminación"
    />
    <!-- Nota: Se asumió 'header', 'icon', '@confirm', '@cancel' como props/eventos. Ajustar si ConfirmationModal.vue usa otros. -->

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
// Cambiado a Producto desde productoModel (asumiendo exportación del tipo/interfaz)
import type { Producto } from '../models/productoModel';

// --- ARSENAL DEOU CANÓNICO ---
import TablaDatos from '@/components/TablaDatos.vue';
// Corregida la ruta y nombre del componente modal
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue';
// --- FIN ARSENAL ---

// La importación ya era correcta respecto al nombre del archivo
import ProductoForm from '../components/ProductoForm.vue';

// 1. EL CEREBRO (Store)
const store = useProductoStore();

// Definición de columnas para "La Columna Vertebral"
// Asegúrate que los 'field' coincidan exactamente con las propiedades del modelo Producto
const columnasProductos = ref([
  { field: 'sku', header: 'SKU' },
  { field: 'nombre', header: 'Nombre' },
  { field: 'precio_costo', header: 'Costo' },
  { field: 'precio_base_venta', header: 'Venta Base' },
  { field: 'baja_logica', header: 'Activo' }, // (Se puede formatear en TablaDatos si es necesario)
]);

// Carga inicial de datos
onMounted(() => {
  store.fetchProductos();
});

// 2. LÓGICA DE FORMULARIO ("El Taller")
const mostrarFormulario = ref(false);

const abrirFormNuevo = () => {
  store.seleccionarProducto(null); // Limpia la selección
  mostrarFormulario.value = true;
};

// Asegúrate que el tipo del parámetro coincida con tu modelo
const onEditarProducto = (producto: Producto) => {
  store.seleccionarProducto(producto); // Carga el producto en el store
  mostrarFormulario.value = true;
};

// El evento 'guardar' de ProductoForm debería emitir un objeto Producto completo
const onGuardarProducto = (productoData: Producto) => {
  store.guardarProducto(productoData); // El store maneja si es 'crear' o 'actualizar'
  // Opcional: Recargar o actualizar la lista localmente si el store no lo hace reactivamente
  // store.fetchProductos(); // Si es necesario forzar recarga
  mostrarFormulario.value = false; // Cerrar el formulario al guardar
};

// 3. LÓGICA DE ELIMINACIÓN ("Doble Llave")
const mostrarModalEliminar = ref(false);
const productoAEliminar = ref<Producto | null>(null);

const onConfirmarEliminar = (producto: Producto) => {
  productoAEliminar.value = producto;
  mostrarModalEliminar.value = true;
};

const ejecutarEliminacion = async () => { // Convertido a async para posible await
  if (productoAEliminar.value && productoAEliminar.value.id) {
    await store.eliminarProducto(productoAEliminar.value.id); // Usar await si la acción retorna promesa
    // Opcional: Recargar o actualizar la lista localmente si el store no lo hace reactivamente
    // store.fetchProductos(); // Si es necesario forzar recarga
  }
  cancelarEliminacion();
};

const cancelarEliminacion = () => {
  productoAEliminar.value = null;
  mostrarModalEliminar.value = false;
};
</script>

<style scoped>
/* Estilos específicos si son necesarios */
.card {
    padding: 1rem;
}
</style>