<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <Button label="Nuevo Rubro (F4)" icon="pi pi-plus" class="mr-2" @click="abrirModalNuevo" />
      </template>
      </Toolbar>

    <TablaDatos
      :datos="store.rubrosActivos"
      :columnas="columnas"
      :cargando="store.estadoCarga"
      @editar-item="abrirModalEditar"
      @ver-item="actualizarItemSeleccionado" @eliminar-item="abrirModalEliminar"
    >
      <template #body-baja_logica="{ data }">
        <Tag
          :value="data.baja_logica ? 'No' : 'Sí'"
          :severity="data.baja_logica ? 'danger' : 'success'"
        />
      </template>
    </TablaDatos>

    <RubroForm v-if="formVisible"
      :visible="formVisible"
      :rubro="store.rubroSeleccionado"
      @update:visible="formVisible = $event"
      @guardar="manejarGuardado"
    />

    <ConfirmationModal v-if="confirmVisible && store.rubroSeleccionado"
      :visible="confirmVisible"
      titulo="Confirmar Baja"
      :message="`¿Está seguro que desea dar de baja el rubro '${store.rubroSeleccionado?.nombre || ''}'?`"
      @update:visible="confirmVisible = $event"
      @confirmado="manejarEliminacion"
      @cancelado="confirmVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRubroStore } from '@/stores/useRubroStore';
import type { RubroModel } from '@/models/rubroModel';
import TablaDatos from '@/components/TablaDatos.vue';
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue';
import RubroForm from '@/components/RubroForm.vue';
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import notificationService from '@/services/notificationService'; // Importar para F7

const store = useRubroStore();
const formVisible = ref(false);
const confirmVisible = ref(false);
const itemSeleccionadoParaClonar = ref<RubroModel | null>(null); // NUEVO: Para F7

const columnas = [
    { field: 'codigo', header: 'Código', sortable: true },
    { field: 'nombre', header: 'Nombre', sortable: true },
    { field: 'baja_logica', header: 'Activo' },
];

onMounted(() => {
  store.fetchRubros();
  document.addEventListener('keydown', handleGlobalKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeyDown);
});

// --- Lógica de Modales ---
function abrirModalNuevo() {
  console.log('--- [RubrosView] Iniciando abrirModalNuevo ---');
  itemSeleccionadoParaClonar.value = null; // Limpiar selección F7
  store.seleccionarRubro(null);
  formVisible.value = true;
  console.log(`--- [RubrosView] formVisible cambiado a: ${formVisible.value} ---`);
}
function abrirModalEditar(rubro: RubroModel) {
  itemSeleccionadoParaClonar.value = rubro; // Guardar para posible F7
  store.seleccionarRubro(rubro);
  formVisible.value = true;
}
function abrirModalEliminar(rubro: RubroModel) {
  itemSeleccionadoParaClonar.value = rubro; // Guardar para posible F7
  store.seleccionarRubro(rubro);
  confirmVisible.value = true;
}
// NUEVO: Función para clonar (F7)
function abrirModalClonar() {
  if (!itemSeleccionadoParaClonar.value) {
    notificationService.mostrarAdvertencia("Acción Inválida", "Seleccione un rubro de la tabla primero para clonar (F7).");
    return;
  }
  console.log('--- [RubrosView] Iniciando abrirModalClonar ---');
  store.seleccionarParaClonar(itemSeleccionadoParaClonar.value); // Usa la nueva acción del store
  formVisible.value = true;
}
// NUEVO: Actualizar item seleccionado (placeholder para selección real de TablaDatos)
// IMPORTANTE: Asegúrate que tu componente TablaDatos emita 'ver-item' (o un evento similar)
// cuando una fila es seleccionada, pasando el objeto de datos de esa fila.
function actualizarItemSeleccionado(rubro: RubroModel) {
  console.log('--- [RubrosView] Item seleccionado para posible clonación:', rubro);
  itemSeleccionadoParaClonar.value = rubro;
}

// --- Lógica de Acciones ---
async function manejarGuardado(rubro: RubroModel) {
    const exito = await store.guardarRubro(rubro);
    if (exito) {
        formVisible.value = false;
        itemSeleccionadoParaClonar.value = null; // Limpiar selección F7 al guardar
    }
}
async function manejarEliminacion() {
    if (store.rubroSeleccionado?.id) {
        await store.eliminarRubro(store.rubroSeleccionado.id);
    }
    confirmVisible.value = false;
    itemSeleccionadoParaClonar.value = null; // Limpiar selección F7 al eliminar
}

// --- Manejador Global F4/F7 ---
function handleGlobalKeyDown(event: KeyboardEvent) {
  // Solo actuar si no hay modales de esta vista activos
  if (!formVisible.value && !confirmVisible.value) {
    if (event.key === 'F4') {
      event.preventDefault();
      abrirModalNuevo();
    }
    if (event.key === 'F7') { // NUEVO: Listener F7
      event.preventDefault();
      abrirModalClonar();
    }
  }
}
// ---

</script>

<style scoped>
.card { padding: 1rem; }
/* Estilos botones acciones */
:deep(.p-datatable .p-datatable-tbody > tr > td:last-child .p-button) { margin-right: 0.25rem; }
:deep(.p-datatable .p-datatable-tbody > tr > td:last-child .p-button:last-child) { margin-right: 0; }
</style>