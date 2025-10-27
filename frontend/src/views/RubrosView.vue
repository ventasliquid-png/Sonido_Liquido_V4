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
      @eliminar-item="abrirModalEliminar"
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

const store = useRubroStore();
const formVisible = ref(false);
const confirmVisible = ref(false);

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
  console.log('--- [RubrosView] Iniciando abrirModalNuevo ---'); // <-- NUEVO LOG
  store.seleccionarRubro(null);
  formVisible.value = true;
  console.log(`--- [RubrosView] formVisible cambiado a: ${formVisible.value} ---`); // <-- NUEVO LOG
}
function abrirModalEditar(rubro: RubroModel) { store.seleccionarRubro(rubro); formVisible.value = true; }
function abrirModalEliminar(rubro: RubroModel) { store.seleccionarRubro(rubro); confirmVisible.value = true; }

// --- Lógica de Acciones ---
async function manejarGuardado(rubro: RubroModel) {
    const exito = await store.guardarRubro(rubro);
    if (exito) {
        formVisible.value = false;
    }
}
async function manejarEliminacion() {
    if (store.rubroSeleccionado?.id) {
        await store.eliminarRubro(store.rubroSeleccionado.id);
    }
    confirmVisible.value = false;
}

// --- Manejador Global F4 ---
function handleGlobalKeyDown(event: KeyboardEvent) {
  if (!formVisible.value && !confirmVisible.value) { // Solo si no hay modales activos
    if (event.key === 'F4') {
      event.preventDefault();
      abrirModalNuevo();
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