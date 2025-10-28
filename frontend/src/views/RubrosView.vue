<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <Button label="Nuevo Rubro (F4)" icon="pi pi-plus" class="mr-2" @click="abrirModalNuevo" />
      </template>

      <template #end>
        <SelectButton
          v-model="filtroEstadoSeleccionado"
          :options="opcionesFiltroEstado"
          optionLabel="label"
          optionValue="value"
          aria-labelledby="basic"
          @change="onFiltroChange" />
          </template>
      </Toolbar>

    <TablaDatos
      :datos="rubrosFiltrados"
      :columnas="columnas"
      :cargando="store.estadoCarga"
      :rowClass="getRowClass"
      @editar-item="abrirModalEditar"
      @ver-item="actualizarItemSeleccionado"
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
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRubroStore } from '@/stores/useRubroStore';
import type { RubroModel } from '@/models/rubroModel';
import TablaDatos from '@/components/TablaDatos.vue';
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue';
import RubroForm from '@/components/RubroForm.vue';
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import SelectButton from 'primevue/selectbutton';
import notificationService from '@/services/notificationService';

const store = useRubroStore();
const formVisible = ref(false);
const confirmVisible = ref(false);
const itemSeleccionadoParaClonar = ref<RubroModel | null>(null);

type FiltroEstado = 'activos' | 'inactivos' | 'todos';
const filtroEstadoSeleccionado = ref<FiltroEstado>('activos');
const opcionesFiltroEstado = ref([
    { label: 'Activos', value: 'activos' },
    { label: 'Inactivos', value: 'inactivos' },
    { label: 'Todos', value: 'todos' }
]);

// Log para ver cambios en el filtro
const onFiltroChange = (event: any) => {
    console.log('Filtro cambiado a:', event.value);
    filtroEstadoSeleccionado.value = event.value; // Asegurar actualización
}

const rubrosFiltrados = computed(() => {
  const todos = store.todosLosRubros;
  console.log('Calculando rubrosFiltrados. Estado filtro:', filtroEstadoSeleccionado.value, 'Total rubros:', todos.length); // Log de depuración
  switch (filtroEstadoSeleccionado.value) {
    case 'activos':
      return todos.filter(r => !r.baja_logica);
    case 'inactivos':
      return todos.filter(r => r.baja_logica);
    case 'todos':
    default:
      return todos;
  }
});

const columnas = [
    { field: 'codigo', header: 'Código', sortable: true },
    { field: 'nombre', header: 'Nombre', sortable: true },
    { field: 'baja_logica', header: 'Activo' },
];

onMounted(() => {
  console.log('RubrosView Montado. Opciones Filtro:', opcionesFiltroEstado.value); // Log de depuración
  store.fetchRubros();
  document.addEventListener('keydown', handleGlobalKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeyDown);
});

function abrirModalNuevo() { /* ... sin cambios ... */ itemSeleccionadoParaClonar.value = null; store.seleccionarRubro(null); formVisible.value = true;}
function abrirModalEditar(rubro: RubroModel) { /* ... sin cambios ... */ itemSeleccionadoParaClonar.value = rubro; store.seleccionarRubro(rubro); formVisible.value = true; }
function abrirModalEliminar(rubro: RubroModel) { /* ... sin cambios ... */ itemSeleccionadoParaClonar.value = rubro; store.seleccionarRubro(rubro); confirmVisible.value = true; }
function abrirModalClonar() { /* ... sin cambios ... */ if (!itemSeleccionadoParaClonar.value) { notificationService.mostrarAdvertencia("Acción Inválida", "Seleccione un rubro de la tabla primero para clonar (F7)."); return; } store.seleccionarParaClonar(itemSeleccionadoParaClonar.value); formVisible.value = true; }
function actualizarItemSeleccionado(rubro: RubroModel) { /* ... sin cambios ... */ itemSeleccionadoParaClonar.value = rubro;}
async function manejarGuardado(rubro: RubroModel) { /* ... sin cambios ... */ const exito = await store.guardarRubro(rubro); if (exito) { formVisible.value = false; itemSeleccionadoParaClonar.value = null; }}
async function manejarEliminacion() { /* ... sin cambios ... */ if (store.rubroSeleccionado?.id) { await store.eliminarRubro(store.rubroSeleccionado.id); } confirmVisible.value = false; itemSeleccionadoParaClonar.value = null; }
function handleGlobalKeyDown(event: KeyboardEvent) { /* ... sin cambios ... */ if (!formVisible.value && !confirmVisible.value) { if (event.key === 'F4') { event.preventDefault(); abrirModalNuevo(); } if (event.key === 'F7') { event.preventDefault(); abrirModalClonar(); } } }

const getRowClass = (data: RubroModel) => {
    return data.baja_logica ? 'row-inactivo' : 'row-activo';
};

// Función de color eliminada temporalmente ya que no se usa el slot
// const getColorClassForFilter = (value: FiltroEstado) => { /* ... */ };

</script>

<style scoped>
.card { padding: 1rem; }
/* Estilos botones acciones tabla (sin cambios) */
:deep(.p-datatable .p-datatable-tbody > tr > td:last-child .p-button) { margin-right: 0.25rem; }
:deep(.p-datatable .p-datatable-tbody > tr > td:last-child .p-button:last-child) { margin-right: 0; }

/* --- Estilos Condicionales para Filas (sin cambios) --- */
:deep(.p-datatable .p-datatable-tbody > tr.row-activo) { color: #1a5d2b; }
:deep(.p-datatable .p-datatable-tbody > tr.row-inactivo) { color: #7a2a33; }

/* --- Estilos para SelectButton (ELIMINADOS TEMPORALMENTE) --- */
/* :deep(.p-selectbutton .p-button.p-highlight.filter-button-activo) { ... } */
/* :deep(.p-selectbutton .p-button.p-highlight.filter-button-inactivo) { ... } */
/* :deep(.p-selectbutton .p-button.p-highlight.filter-button-todos) { ... } */
/* .filter-button-activo span, .filter-button-inactivo span, .filter-button-todos span { ... } */
</style>