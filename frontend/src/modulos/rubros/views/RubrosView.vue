<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <Button label="Nuevo Rubro (F4)" icon="pi pi-plus" class="mr-2" @click="abrirModalNuevo" v-tooltip.bottom="'F4 - Nuevo'"/>
      </template>
      <template #end>
        <SelectButton v-model="store.filtroEstado" :options="opcionesFiltroEstado" optionLabel="label" optionValue="value" aria-labelledby="basic" :pt="selectButtonPassThrough" @change="onFiltroChange"/>
      </template>
    </Toolbar>

    <DataTable :value="store.todosLosRubros" :loading="store.estadoCarga" :rowClass="getRowClass" responsiveLayout="scroll">
      <Column field="codigo" header="Código" :sortable="true"></Column>
      <Column field="nombre" header="Nombre" :sortable="true"></Column>
      <Column field="baja_logica" header="Activo">
        <template #body="slotProps">
          <Tag :severity="slotProps.data.baja_logica ? 'danger' : 'success'">{{ slotProps.data.baja_logica ? 'INACTIVO' : 'ACTIVO' }}</Tag>
        </template>
      </Column>
      <Column :exportable="false" style="min-width:14rem">
        <template #body="slotProps">
          <Button icon="pi pi-copy" class="p-button-rounded p-button-secondary mr-2" @click="abrirModalClonar(slotProps.data)" v-tooltip.bottom="'F7 - Clonar'"/>
          <Button v-if="!slotProps.data.baja_logica" icon="pi pi-pencil" class="p-button-rounded p-button-info mr-2" @click="abrirModalEditar(slotProps.data)" v-tooltip.bottom="'Editar'"/>
          <Button v-if="!slotProps.data.baja_logica" icon="pi pi-trash" class="p-button-rounded p-button-danger mr-2" @click="abrirModalEliminar(slotProps.data)" v-tooltip.bottom="'Dar de Baja'"/>
          <Button v-if="slotProps.data.baja_logica" icon="pi pi-check" class="p-button-rounded p-button-warning mr-2" @click="abrirModalReactivarDirecto(slotProps.data)" v-tooltip.bottom="'Reactivar'"/>
        </template>
      </Column>
    </DataTable>

    <Dialog
      :visible="formVisible"
      modal
      :header="formTitle"
      :style="{ width: '30rem' }"
      @update:visible="cerrarModal"
      @keydown.esc.prevent="cerrarModal"
      @keydown.f10.prevent="guardarFormulario" >
      <RubroForm v-if="formVisible"
        v-model="formData"
        :esEdicion="esEdicion"
        :esClonado="esClonado"
        @guardar="guardarFormulario" />
      
      <template #footer>
        <Button label="Cancelar (Esc)" icon="pi pi-times" @click="cerrarModal" text />
        <Button label="Guardar (F10/Enter)" icon="pi pi-check" @click="guardarFormulario" />
      </template>
    </Dialog>

    <ConfirmationModal v-if="confirmVisible" :visible="confirmVisible" titulo="Confirmar Baja" :message="'¿Está seguro que desea dar de baja el rubro ' + (itemSeleccionadoParaAccion?.nombre || '') + '?'" @update:visible="confirmVisible = $event" @confirmado="manejarEliminacion" @cancelado="cancelarModalAccion" />
    <ConfirmationModal :visible="confirmReactivarDirectoVisible" titulo="Confirmar Reactivación" :message="`¿Está seguro que desea reactivar el rubro '${itemSeleccionadoParaAccion?.nombre || ''}'?`" @update:visible="confirmReactivarDirectoVisible = $event" @confirmado="manejarReactivarDirecto" @cancelado="cancelarModalAccion" />
    <ConfirmationModal v-if="store.confirmarReactivacionVisible" :visible="store.confirmarReactivacionVisible" titulo="Confirmar Reactivación (ABR)" :message="'El rubro ' + (store.nombreParaReactivar || '') + ' ya existe y está inactivo. ¿Desea reactivarlo?'" @update:visible="manejarCancelarReactivacionABR" @confirmado="manejarConfirmarReactivacionABR" @cancelado="manejarCancelarReactivacionABR" />
  </div>
</template>

<script setup lang="ts">
// (Importaciones... sin cambios)
import { ref, onMounted, onUnmounted, computed } from 'vue'; 
import { useRubroStore } from '../store/useRubroStore';
import type { RubroModel } from '../models/rubroModel';
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue';
import RubroForm from '../components/RubroForm.vue'; 
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import SelectButton from 'primevue/selectbutton';
import Tooltip from 'primevue/tooltip'; 
import DataTable from 'primevue/datatable'; 
import Column from 'primevue/column'; 
import Dialog from 'primevue/dialog'; 
import type { SelectButtonPassThroughOptions } from 'primevue/selectbutton'; 
import notificationService from '@/services/notificationService';

// (Todo el <script setup> es idéntico al v10.2... sin cambios)
const store = useRubroStore();
const formVisible = ref(false);
const getInitialFormData = (): RubroModel => ({
  id: null, codigo: '', nombre: '', baja_logica: false,
});
const formData = ref<RubroModel>(getInitialFormData());
const esEdicion = ref(false);
const esClonado = ref(false);

const formTitle = computed(() => {
    if (esEdicion.value) return 'Editar Rubro';
    if (esClonado.value) return 'Clonar Rubro (Nuevo Código Requerido)';
    return 'Nuevo Rubro';
});

const itemSeleccionadoParaClonar = ref<RubroModel | null>(null); 
const confirmVisible = ref(false); 
const confirmReactivarDirectoVisible = ref(false); 
const itemSeleccionadoParaAccion = ref<RubroModel | null>(null); 

type FiltroEstado = 'activos' | 'inactivos' | 'todos';
const opcionesFiltroEstado = ref([
    { label: 'Activos', value: 'activos', colorClass: 'filter-pt-activo' }, 
    { label: 'Inactivos', value: 'inactivos', colorClass: 'filter-pt-inactivo' },
    { label: 'Todos', value: 'todos', colorClass: 'filter-pt-todos' }
]);
const onFiltroChange = (event: any) => { store.setFiltroEstado(event.value); }

onMounted(() => {
  store.fetchRubros(); 
  document.addEventListener('keydown', handleGlobalKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeyDown);
});

function cerrarModal() {
  formVisible.value = false;
  formData.value = getInitialFormData();
}

function abrirModalNuevo() { 
  formData.value = getInitialFormData();
  esEdicion.value = false;
  esClonado.value = false;
  formVisible.value = true;
}

function abrirModalEditar(rubro: RubroModel) { 
  itemSeleccionadoParaClonar.value = rubro; 
  formData.value = { ...rubro };
  esEdicion.value = true;
  esClonado.value = false;
  formVisible.value = true; 
}

function abrirModalClonar(rubroAF7: RubroModel | null = null) {
  const rubroBase = rubroAF7 || itemSeleccionadoParaClonar.value;
  if (!rubroBase) { 
    notificationService.showWarn("Acción Inválida", "Seleccione un rubro de la tabla primero para clonar (F7)."); 
    return; 
  }
  store.seleccionarParaClonar(rubroBase); 
  formData.value = { ...store.rubroSeleccionado };
  esEdicion.value = false;
  esClonado.value = true;
  formVisible.value = true; 
}

function abrirModalEliminar(rubro: RubroModel) { 
  itemSeleccionadoParaClonar.value = rubro; 
  itemSeleccionadoParaAccion.value = rubro; 
  store.seleccionarRubro(rubro); 
  confirmVisible.value = true; 
}
function abrirModalReactivarDirecto(rubro: RubroModel) {
  itemSeleccionadoParaAccion.value = rubro;
  confirmReactivarDirectoVisible.value = true;
}
function cancelarModalAccion() {
  itemSeleccionadoParaAccion.value = null;
  confirmVisible.value = false;
  confirmReactivarDirectoVisible.value = false;
}
async function manejarEliminacion() { 
  if (itemSeleccionadoParaAccion.value?.id) { 
    await store.eliminarRubro(itemSeleccionadoParaAccion.value.id); 
  } 
  cancelarModalAccion();
  itemSeleccionadoParaClonar.value = null; 
}
async function manejarReactivarDirecto() {
    if (itemSeleccionadoParaAccion.value?.id) {
        await store.ejecutarReactivacion(itemSeleccionadoParaAccion.value.id);
    }
    cancelarModalAccion();
}

async function guardarFormulario() {
  const codigoTrimmed = (formData.value.codigo || '').trim().toUpperCase();
  const nombreTrimmed = (formData.value.nombre || '').trim();
  if (!codigoTrimmed) {
    notificationService.showWarn("Validación Fallida", "El campo 'Código' es requerido.");
    return;
  }
  if (codigoTrimmed.length > 3) {
    notificationService.showWarn("Validación Fallida", "El campo 'Código' no puede exceder los 3 caracteres.");
    return;
  }
  if (!nombreTrimmed) {
    notificationService.showWarn("Validación Fallida", "El campo 'Nombre' es requerido.");
    return;
  }
  if (nombreTrimmed.length > 30) {
    notificationService.showWarn("Validación Fallida", "El campo 'Nombre' no puede exceder los 30 caracteres.");
    return;
  }
  if (esClonado.value && !codigoTrimmed) {
      notificationService.showWarn("Validación Clon", "Debe ingresar un nuevo Código para el rubro clonado.");
      return;
  }
  const dataToEmit: RubroModel = {
    ...formData.value,
    codigo: codigoTrimmed,
    nombre: nombreTrimmed,
  };
  const exito = await store.guardarRubro(dataToEmit); 
  if (exito) { 
    cerrarModal(); 
    itemSeleccionadoParaClonar.value = null; 
  }
}

function handleGlobalKeyDown(event: KeyboardEvent) { 
  if (!formVisible.value && !confirmVisible.value && !store.confirmarReactivacionVisible) { 
    if (event.key === 'F4') { 
      event.preventDefault(); 
      abrirModalNuevo(); 
    } 
    if (event.key === 'F7') { 
      event.preventDefault(); 
      abrirModalClonar(); 
    } 
  } 
}
async function manejarConfirmarReactivacionABR() {
  await store.ejecutarReactivacion(); 
  cerrarModal(); 
}
function manejarCancelarReactivacionABR() {
  store.cancelarReactivacion();
  cerrarModal(); 
}

const getRowClass = (data: RubroModel) => {
    return data.baja_logica ? 'row-inactivo' : 'row-activo';
};
const selectButtonPassThrough = computed<SelectButtonPassThroughOptions>(() => ({
    button: ({ context, props: buttonProps }) => {
        const option = opcionesFiltroEstado.value.find(opt => opt.value === buttonProps.value);
        return option ? { class: [option.colorClass] } : {};
    }
}));
</script>

<style scoped>
/* (Estilos... sin cambios, v10.1 corregido) */
.card { padding: 1rem; }
:deep(.p-datatable .p-datatable-tbody > tr > td:last-child .p-button) { margin-right: 0.25rem; }
:deep(.p-datatable .p-datatable-tbody > tr > td:last-child .p-button:last-child) { margin-right: 0; }
:deep(.p-datatable .p-datatable-tbody > tr.row-activo) { color: #1a5d2b; }
:deep(.p-datatable .p-datatable-tbody > tr.row-inactivo) { color: #7a2a33; }
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
</style>