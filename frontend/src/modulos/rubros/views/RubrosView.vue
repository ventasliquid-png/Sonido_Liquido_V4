<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <Button label="Nuevo Rubro (F4)" icon="pi pi-plus" class="mr-2" @click="abrirModalNuevo" v-tooltip.bottom="'F4 - Nuevo'"/>
      </template>

      <template #end>
        <SelectButton
          v-model="store.filtroEstado" 
          :options="opcionesFiltroEstado"
          optionLabel="label"
          optionValue="value"
          aria-labelledby="basic"
          :pt="selectButtonPassThrough" 
          @change="onFiltroChange"
        />
      </template>
    </Toolbar>

    <DataTable 
      :value="store.todosLosRubros" 
      :loading="store.estadoCarga" 
      :rowClass="getRowClass"
      responsiveLayout="scroll"
    >
      <Column field="codigo" header="Código" :sortable="true"></Column>
      <Column field="nombre" header="Nombre" :sortable="true"></Column>

      <Column field="baja_logica" header="Activo">
        <template #body="slotProps">
          <Tag :severity="slotProps.data.baja_logica ? 'danger' : 'success'">
            {{ slotProps.data.baja_logica ? 'INACTIVO' : 'ACTIVO' }}
          </Tag>
        </template>
      </Column>

      <Column :exportable="false" style="min-width:12rem">
        <template #body="slotProps">
          <Button
            icon="pi pi-copy"
            class="p-button-rounded p-button-secondary mr-2"
            @click="abrirModalClonar(slotProps.data)"
            v-tooltip.bottom="'F7 - Clonar'"
          />
        
          <Button
            v-if="!slotProps.data.baja_logica"
            icon="pi pi-pencil"
            class="p-button-rounded p-button-success mr-2"
            @click="abrirModalEditar(slotProps.data)"
            v-tooltip.bottom="'Editar'"
          />

          <Button
            v-if="!slotProps.data.baja_logica"
            icon="pi pi-trash"
            class="p-button-rounded p-button-danger mr-2"
            @click="abrirModalEliminar(slotProps.data)"
            v-tooltip.bottom="'Dar de Baja'"
          />

          <Button
            v-if="slotProps.data.baja_logica"
            icon="pi pi-check"
            class="p-button-rounded p-button-warning mr-2"
            @click="abrirModalReactivarDirecto(slotProps.data)"
            v-tooltip.bottom="'Reactivar'"
          />
        </template>
      </Column>
    </DataTable>

    <RubroForm v-if="formVisible"
      :visible="formVisible"
      :rubro="store.rubroSeleccionado"
      @update:visible="formVisible = $event"
      @guardar="manejarGuardado"
    />

    <ConfirmationModal v-if="confirmVisible"
      :visible="confirmVisible"
      titulo="Confirmar Baja"
      :message="'¿Está seguro que desea dar de baja el rubro ' + (itemSeleccionadoParaAccion?.nombre || '') + '?'"
      @update:visible="confirmVisible = $event"
      @confirmado="manejarEliminacion"
      @cancelado="cancelarModalAccion"
    />
    
    <ConfirmationModal
      :visible="confirmReactivarDirectoVisible"
      titulo="Confirmar Reactivación"
      :message="`¿Está seguro que desea reactivar el rubro '${itemSeleccionadoParaAccion?.nombre || ''}'?`"
      @update:visible="confirmReactivarDirectoVisible = $event"
      @confirmado="manejarReactivarDirecto"
      @cancelado="cancelarModalAccion"
    />

    <ConfirmationModal v-if="store.confirmarReactivacionVisible"
      :visible="store.confirmarReactivacionVisible"
      titulo="Confirmar Reactivación (ABR)"
      :message="'El rubro ' + (store.nombreParaReactivar || '') + ' ya existe y está inactivo. ¿Desea reactivarlo?'"
      @update:visible="manejarCancelarReactivacionABR"
      @confirmado="manejarConfirmarReactivacionABR"
      @cancelado="manejarCancelarReactivacionABR"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRubroStore } from '../store/useRubroStore';
import type { RubroModel } from '../models/rubroModel';
// REPARACIÓN G-R-20: Se elimina 'TablaDatos' y se añaden los nativos
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue';
import RubroForm from '../components/RubroForm.vue';
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import SelectButton from 'primevue/selectbutton';
import Tooltip from 'primevue/tooltip'; 
import DataTable from 'primevue/datatable'; // <-- Importación nativa
import Column from 'primevue/column';     // <-- Importación nativa
import type { SelectButtonPassThroughOptions } from 'primevue/selectbutton'; 

const store = useRubroStore();
const formVisible = ref(false);
const itemSeleccionadoParaClonar = ref<RubroModel | null>(null); // Para F7 (Clonar)

const confirmVisible = ref(false); // Modal Baja
const confirmReactivarDirectoVisible = ref(false); // Modal Reactivar
const itemSeleccionadoParaAccion = ref<RubroModel | null>(null); // Ítem para Baja o Reactivar

type FiltroEstado = 'activos' | 'inactivos' | 'todos';

const opcionesFiltroEstado = ref([
    { label: 'Activos', value: 'activos', colorClass: 'filter-pt-activo' }, 
    { label: 'Inactivos', value: 'inactivos', colorClass: 'filter-pt-inactivo' },
    { label: 'Todos', value: 'todos', colorClass: 'filter-pt-todos' }
]);

const onFiltroChange = (event: any) => {
    console.log('Filtro cambiado a:', event.value);
    store.setFiltroEstado(event.value);
}

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

function abrirModalNuevo() { 
  itemSeleccionadoParaClonar.value = null; 
  store.seleccionarRubro(null); 
  formVisible.value = true;
}

function abrirModalEditar(rubro: RubroModel) { 
  itemSeleccionadoParaClonar.value = rubro; 
  store.seleccionarRubro(rubro); 
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


function abrirModalClonar() { 
  // REPARACIÓN G-R-20: 'itemSeleccionadoParaClonar' es la fuente de verdad para F7
  if (!itemSeleccionadoParaClonar.value) { 
    notificationService.showWarn("Acción Inválida", "Seleccione un rubro de la tabla primero para clonar (F7)."); 
    return; 
  } 
  store.seleccionarParaClonar(itemSeleccionadoParaClonar.value); 
  formVisible.value = true; 
}
function actualizarItemSeleccionado(rubro: RubroModel) { 
  // REPARACIÓN G-R-20: Se debe capturar el 'ver-item' (clic/foco) de la tabla
  itemSeleccionadoParaClonar.value = rubro;
}

async function manejarGuardado(rubro: RubroModel) { 
  const exito = await store.guardarRubro(rubro); 
  if (exito) { 
    formVisible.value = false; 
    itemSeleccionadoParaClonar.value = null; 
  }
}

function handleGlobalKeyDown(event: KeyboardEvent) { 
  if (!formVisible.value && !confirmVisible.value && !confirmReactivarDirectoVisible.value) { 
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

// Flujo ABR (Conflicto 409)
async function manejarConfirmarReactivacionABR() {
  await store.ejecutarReactivacion(); // Llama sin ID, usará el 'idParaReactivar'
  formVisible.value = false; 
}

function manejarCancelarReactivacionABR() {
  store.cancelarReactivacion();
  formVisible.value = false; 
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