<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <Button label="Nuevo Sub-Rubro (F4)" icon="pi pi-plus" class="mr-2" @click="abrirModalNuevo" v-tooltip.bottom="'F4 - Nuevo'"/>
      </template>
      <template #end>
        <SelectButton
          v-model="filtroSeleccionado"
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

    <TablaDatos
      :datos="store.listaSubRubros"
      :columnas="columnas"
      :cargando="store.estadoCarga"
      :rowStyle="rowStyle"
      @editar-item="abrirModalEditar"
      @eliminar-item="abrirModalEliminar"
    >
      <template #actions-prepend="slotProps">
        <Button
          icon="pi pi-copy"
          class="p-button-rounded p-button-secondary"
          @click="abrirModalClonar(slotProps.data)"
          v-tooltip.bottom="'F7 - Clonar'"
        />
      </template>
      <template #body-baja_logica="{ data }">
        <Tag
          :value="data.baja_logica ? 'Inactivo' : 'Activo'"
          :severity="data.baja_logica ? 'danger' : 'success'"
        />
      </template>
    </TablaDatos>

    <ConfirmationModal
      :visible="confirmVisible"
      titulo="Confirmar Baja"
      :message="¿Está seguro que desea dar de baja el sub-rubro ''?"
      @update:visible="confirmVisible = "
      @confirmado="manejarEliminacion"
      @cancelado="confirmVisible = false"
    />

    <ConfirmationModal
      :visible="!!store.subrubroInactivoParaReactivar"
      titulo="Reactivar Sub-Rubro Detectado"
      :message="Se detectó un sub-rubro inactivo con el mismo . ¿Desea reactivarlo?"
      @confirmado="store.reactivarSubRubro"
      @cancelado="store.cancelarReactivacion"
    />

    <SubRubroForm
      v-if="formVisible"
      :visible="formVisible"
      :subrubro="store.subrubroSeleccionado"
      :modo-clon="esModoClon"
      @update:visible="formVisible = "
      @guardar="manejarGuardado"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useSubRubroStore } from '../store/useSubRubroStore';
import type { SubRubroModel } from '../models/subRubroModel';
import TablaDatos from '@/components/TablaDatos.vue';
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue';
import SubRubroForm from '../components/SubRubroForm.vue'; // Adaptado
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import SelectButton from 'primevue/selectbutton';
import Tooltip from 'primevue/tooltip';

const store = useSubRubroStore();
const formVisible = ref(false);
const confirmVisible = ref(false);
const esModoClon = ref(false);

const columnas = [
    { field: 'codigo_subrubro', header: 'Código', sortable: true }, // Adaptado
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
    store.setFiltroEstado(filtroSeleccionado.value);
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
  store.seleccionarSubRubro(null); // Limpia
  formVisible.value = true;
}
function abrirModalEditar(subrubro: SubRubroModel) {
  esModoClon.value = false;
  store.seleccionarSubRubro(subrubro);
  formVisible.value = true;
}
function abrirModalEliminar(subrubro: SubRubroModel) {
  store.seleccionarSubRubro(subrubro);
  confirmVisible.value = true;
}

// --- DOCTRINA F7 (Clonar) ---
function abrirModalClonar(subrubro: SubRubroModel) {
  const clon = { ...subrubro, id: null, codigo_subrubro: '' }; // Borra ID y Codigo
  store.seleccionarSubRubro(clon);
  esModoClon.value = true;
  formVisible.value = true;
}

// --- Lógica de Acciones ---
async function manejarGuardado(subrubro: SubRubroModel | SubRubroUpdateModel) {
  const exito = await store.guardarSubRubro(subrubro);
  if (exito) {
    formVisible.value = false; // Cierra el modal solo si el guardado fue exitoso
  }
}
async function manejarEliminacion() {
  if (store.subrubroSeleccionado?.id) {
    await store.eliminarSubRubro(store.subrubroSeleccionado.id);
  }
  confirmVisible.value = false;
}

// --- DOCTRINA F4 (Alta Rápida) ---
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'F4') {
    event.preventDefault();
    abrirModalNuevo();
  }
  // F7 (Clonar) se maneja a nivel de fila, no global
};

onMounted(() => {
  store.fetchSubRubros();
  document.addEventListener('keydown', handleKeyDown);
});
onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeyDown);
});
</script>
