<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <Button label="Nuevo Sub-Rubro (F4)" icon="pi pi-plus" class="mr-2" @click="abrirModalNuevo" v-tooltip.bottom="'F4 - Nuevo'"/>
      </template>
      <template #end>
        <SelectButton
          v-model="store.filtroEstado"
          :options="opcionesFiltro"
          optionLabel="label"
          optionValue="value"
          @change="onFiltroChange"
          :allowEmpty="false"
        >
          <template #option="slotProps">
            <i :class="[slotProps.option.icon, getFiltroClass(slotProps.option.value)]" style="margin-right: 4px;"></i>
            <span :class="getFiltroClass(slotProps.option.value)">{{ slotProps.option.label }}</span>
          </template>
        </SelectButton>
      </template>
    </Toolbar>

    <DataTable 
      :value="store.listaSubRubros" 
      :loading="store.estadoCarga" 
      :rowStyle="rowStyle"
      responsiveLayout="scroll"
    >
      <Column field="codigo_subrubro" header="Código" :sortable="true"></Column>
      <Column field="nombre" header="Nombre" :sortable="true"></Column>

      <Column field="baja_logica" header="Estado">
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

    <ConfirmationModal
      :visible="confirmVisible"
      titulo="Confirmar Baja"
      :message="`¿Está seguro que desea dar de baja el sub-rubro '${itemParaAccion?.nombre || ''}'?`"
      @update:visible="confirmVisible = $event"
      @confirmado="manejarEliminacion"
      @cancelado="cancelarModalAccion"
    />

    <ConfirmationModal
      :visible="confirmReactivarDirectoVisible"
      titulo="Confirmar Reactivación"
      :message="`¿Está seguro que desea reactivar el sub-rubro '${itemParaAccion?.nombre || ''}'?`"
      @update:visible="confirmReactivarDirectoVisible = $event"
      @confirmado="manejarReactivarDirecto"
      @cancelado="cancelarModalAccion"
    />

    <ConfirmationModal
      :visible="!!store.subrubroInactivoParaReactivar"
      titulo="Reactivar Sub-Rubro Detectado"
      :message="`Se detectó un sub-rubro inactivo con el mismo ${store.subrubroInactivoParaReactivar?.campo}. ¿Desea reactivarlo (los datos nuevos se sobrescribirán)?`"
      @confirmado="manejarConfirmarReactivacionABR"
      @cancelado="manejarCancelarReactivacionABR"
    />

    <SubRubroForm
      v-if="formVisible"
      :visible="formVisible"
      :subrubro="store.subrubroSeleccionado"
      :modo-clon="esModoClon"
      @update:visible="formVisible = $event"
      @guardar="manejarGuardado"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useSubRubroStore } from '../store/useSubRubroStore';
import type { SubRubroModel, SubRubroUpdateModel } from '../models/subRubroModel';
// REPARACIÓN G-S-09: Se elimina 'TablaDatos' y se añaden los nativos
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue';
import SubRubroForm from '../components/SubRubroForm.vue';
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import SelectButton from 'primevue/selectbutton';
import Tooltip from 'primevue/tooltip';
import DataTable from 'primevue/datatable'; // <-- Importación nativa
import Column from 'primevue/column';     // <-- Importación nativa

const store = useSubRubroStore();
const formVisible = ref(false);
const esModoClon = ref(false);

const itemParaAccion = ref<SubRubroModel | null>(null);
const confirmVisible = ref(false);
const confirmReactivarDirectoVisible = ref(false);

const columnas = [
    { field: 'codigo_subrubro', header: 'Código', sortable: true },
    { field: 'nombre', header: 'Nombre', sortable: true },
    { field: 'baja_logica', header: 'Estado' },
];

// --- DOCTRINA: Filtro de Tres Vías ---
const filtroSeleccionado = ref(store.filtroEstado);
const opcionesFiltro = ref([
    { label: 'Activos', value: 'activos', icon: 'pi pi-check-circle' },
    { label: 'Inactivos', value: 'inactivos', icon: 'pi pi-times-circle' },
    { label: 'Todos', value: 'todos', icon: 'pi pi-list' }
]);
const onFiltroChange = () => {
    // El v-model actualiza 'store.filtroEstado'
    store.setFiltroEstado(store.filtroEstado);
};
const getFiltroClass = (value: string) => {
    return {
        'text-green-600': value === 'activos',
        'text-red-600': value === 'inactivos',
        'text-blue-600': value === 'todos'
    };
};
// --- DOCTRINA: Color Contextual de Fila ---
const rowStyle = (data: SubRubroModel) => {
    return data.baja_logica ? { color: 'var(--red-600)', 'font-style': 'italic' } : { color: 'var(--text-color)'};
};

// --- Lógica de Modales ---
function abrirModalNuevo() {
  esModoClon.value = false;
  store.seleccionarSubRubro(null);
  formVisible.value = true;
}
function abrirModalEditar(subrubro: SubRubroModel) {
  esModoClon.value = false;
  store.seleccionarSubRubro(subrubro);
  formVisible.value = true;
}

function abrirModalEliminar(subrubro: SubRubroModel) {
  itemParaAccion.value = subrubro; 
  confirmVisible.value = true;
}

function abrirModalReactivarDirecto(subrubro: SubRubroModel) {
  itemParaAccion.value = subrubro; 
  confirmReactivarDirectoVisible.value = true;
}

function cancelarModalAccion() {
  itemParaAccion.value = null;
  confirmVisible.value = false;
  confirmReactivarDirectoVisible.value = false;
}

async function manejarEliminacion() {
  if (itemParaAccion.value?.id) {
    await store.eliminarSubRubro(itemParaAccion.value.id);
  }
  cancelarModalAccion();
}

async function manejarReactivarDirecto() {
    if (itemParaAccion.value?.id) {
        await store.reactivarSubRubro(itemParaAccion.value.id);
    }
    cancelarModalAccion();
}

// --- DOCTRINA F7 (Clonar) ---
function abrirModalClonar(subrubro: SubRubroModel) {
  const clon = { ...subrubro, id: null, codigo_subrubro: '' };
  store.seleccionarSubRubro(clon);
  esModoClon.value = true;
  formVisible.value = true;
}

// --- Lógica de Acciones ---
async function manejarGuardado(subrubro: SubRubroModel | SubRubroUpdateModel) {
  const exito = await store.guardarSubRubro(subrubro);
  if (exito) {
    formVisible.value = false;
  }
}

async function manejarConfirmarReactivacionABR() {
  await store.reactivarSubRubro();
  formVisible.value = false;
}

function manejarCancelarReactivacionABR() {
  store.cancelarReactivacion();
  formVisible.value = false;
}

// --- DOCTRINA F4 (Alta Rápida) ---
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'F4' && !formVisible.value && !confirmVisible.value && !confirmReactivarDirectoVisible.value) {
    event.preventDefault();
    abrirModalNuevo();
  }
};

onMounted(() => {
  store.fetchSubRubros();
  document.addEventListener('keydown', handleKeyDown);
});
onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeyDown);
});
</script>