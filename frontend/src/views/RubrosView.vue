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
          :pt="selectButtonPassThrough" @change="onFiltroChange"
        />
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
import type { SelectButtonPassThroughOptions } from 'primevue/selectbutton'; // Importar tipos PT
import notificationService from '@/services/notificationService';

const store = useRubroStore();
const formVisible = ref(false);
const confirmVisible = ref(false);
const itemSeleccionadoParaClonar = ref<RubroModel | null>(null);

type FiltroEstado = 'activos' | 'inactivos' | 'todos';
const filtroEstadoSeleccionado = ref<FiltroEstado>('activos');
const opcionesFiltroEstado = ref([
    { label: 'Activos', value: 'activos', colorClass: 'filter-pt-activo' }, // Añadir clase para PT
    { label: 'Inactivos', value: 'inactivos', colorClass: 'filter-pt-inactivo' },
    { label: 'Todos', value: 'todos', colorClass: 'filter-pt-todos' }
]);

const onFiltroChange = (event: any) => {
    console.log('Filtro cambiado a:', event.value);
    filtroEstadoSeleccionado.value = event.value;
}

const rubrosFiltrados = computed(() => {
  const todos = store.todosLosRubros;
  console.log('Calculando rubrosFiltrados. Estado filtro:', filtroEstadoSeleccionado.value, 'Total rubros:', todos.length);
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
  store.fetchRubros();
  document.addEventListener('keydown', handleGlobalKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeyDown);
});

function abrirModalNuevo() { itemSeleccionadoParaClonar.value = null; store.seleccionarRubro(null); formVisible.value = true;}
function abrirModalEditar(rubro: RubroModel) { itemSeleccionadoParaClonar.value = rubro; store.seleccionarRubro(rubro); formVisible.value = true; }
function abrirModalEliminar(rubro: RubroModel) { itemSeleccionadoParaClonar.value = rubro; store.seleccionarRubro(rubro); confirmVisible.value = true; }
function abrirModalClonar() { if (!itemSeleccionadoParaClonar.value) { notificationService.mostrarAdvertencia("Acción Inválida", "Seleccione un rubro de la tabla primero para clonar (F7)."); return; } store.seleccionarParaClonar(itemSeleccionadoParaClonar.value); formVisible.value = true; }
function actualizarItemSeleccionado(rubro: RubroModel) { itemSeleccionadoParaClonar.value = rubro;}
async function manejarGuardado(rubro: RubroModel) { const exito = await store.guardarRubro(rubro); if (exito) { formVisible.value = false; itemSeleccionadoParaClonar.value = null; }}
async function manejarEliminacion() { if (store.rubroSeleccionado?.id) { await store.eliminarRubro(store.rubroSeleccionado.id); } confirmVisible.value = false; itemSeleccionadoParaClonar.value = null; }
function handleGlobalKeyDown(event: KeyboardEvent) { if (!formVisible.value && !confirmVisible.value) { if (event.key === 'F4') { event.preventDefault(); abrirModalNuevo(); } if (event.key === 'F7') { event.preventDefault(); abrirModalClonar(); } } }

const getRowClass = (data: RubroModel) => {
    return data.baja_logica ? 'row-inactivo' : 'row-activo';
};

// --- NUEVO: Configuración Passthrough (PT) para SelectButton ---
const selectButtonPassThrough = computed<SelectButtonPassThroughOptions>(() => ({
    button: ({ context, props: buttonProps }) => {
        // Encontrar la opción correspondiente en nuestras 'opcionesFiltroEstado'
        const option = opcionesFiltroEstado.value.find(opt => opt.value === buttonProps.value);
        // Devolver un objeto con la clase de color si la opción se encontró
        return option ? { class: [option.colorClass] } : {};
    }
}));
// --- FIN PT ---

</script>

<style scoped>
.card { padding: 1rem; }

:deep(.p-datatable .p-datatable-tbody > tr > td:last-child .p-button) { margin-right: 0.25rem; }
:deep(.p-datatable .p-datatable-tbody > tr > td:last-child .p-button:last-child) { margin-right: 0; }

:deep(.p-datatable .p-datatable-tbody > tr.row-activo) { color: #1a5d2b; }
:deep(.p-datatable .p-datatable-tbody > tr.row-inactivo) { color: #7a2a33; }

/* --- NUEVO: Estilos PT para SelectButton --- */
/* Aplicar color al botón CUANDO ESTÁ SELECCIONADO (.p-highlight) */
:deep(.p-selectbutton .p-button.filter-pt-activo.p-highlight) {
    background: #28a745 !important;
    border-color: #28a745 !important;
    color: #ffffff !important;
}
:deep(.p-selectbutton .p-button.filter-pt-inactivo.p-highlight) {
    background: #dc3545 !important;
    border-color: #dc3545 !important;
    color: #ffffff !important;
}
:deep(.p-selectbutton .p-button.filter-pt-todos.p-highlight) {
    background: #007bff !important;
    border-color: #007bff !important;
    color: #ffffff !important;
}

/* Opcional: Estilos para botones NO seleccionados (mantener default o ajustar) */
:deep(.p-selectbutton .p-button:not(.p-highlight)) {
   /* background: #f8f9fa; */
   /* border-color: #dee2e6; */
   /* color: #495057; */
}
/* Opcional: Estilo hover para no seleccionados */
:deep(.p-selectbutton .p-button:not(.p-highlight):hover) {
    /* background: #e9ecef; */
    /* border-color: #dee2e6; */
    /* color: #495057; */
}

</style>