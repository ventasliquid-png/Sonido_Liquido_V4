<template>
    <div class="card">
            <Toolbar class="mb-4">
            <template #start>
                <Button label="Nueva Unidad (F4)" icon="pi pi-plus" class="mr-2" @click="abrirDialogNuevo" />
            </template>
            <template #end>
                    <SelectButton
                        v-model="filtroEstado"
                        :options="opcionesFiltro"
                        optionLabel="label"
                        optionValue="value"
                        dataKey="value"
                    />
            </template>
        </Toolbar>

            <DataTable :value="listaFiltrada" :loading="store.isLoading" responsiveLayout="scroll">
            <Column field="codigo_unidad" header="Código" :sortable="true"></Column>
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
                    <Button icon="pi pi-pencil" class="mr-2" v-tooltip.top="'Editar'" @click="abrirDialogEditar(slotProps.data)" />

                    <Button
                        :icon="slotProps.data.baja_logica ? 'pi pi-check' : 'pi pi-trash'"
                    :severity="slotProps.data.baja_logica ? 'success' : 'danger'"
                        v-tooltip.top="slotProps.data.baja_logica ? 'Reactivar' : 'Dar de Baja'"
                        @click="confirmarCambioEstado(slotProps.data)"
                    />
                </template>
            </Column>
        </DataTable>

        <Dialog 
            v-model:visible="dialogVisible" 
            :header="dialogHeader" 
            :modal="true" 
            class="p-fluid"
            @keydown.f10.prevent="guardar"
            @keydown.esc.prevent="cerrarDialog"
        >
            <UnidadMedidaForm 
                v-model="entidad" 
                :submitted="submitted" 
                @guardar="guardar" 
            />
            <template #footer>
                <Button label="Cancelar (Esc)" icon="pi pi-times" severity="secondary" @click="cerrarDialog" text />
                <Button label="Guardar (F10)" icon="pi pi-check" @click="guardar" />
            </template>
        </Dialog>

            <ConfirmationModal
            v-if="confirmVisible"
            :visible="confirmVisible"
            :titulo="confirmTitulo"
            :message="confirmMensaje"
            @update:visible="confirmVisible = $event"
            @confirmado="ejecutarCambioEstado"
            @cancelado="cancelarCambioEstado"
        />
        
        <ConfirmationModal
            v-if="!!store.entidadInactivaParaReactivar"
            :visible="!!store.entidadInactivaParaReactivar"
            titulo="Reactivar Unidad Detectada"
            :message="`El código '${store.datosNuevosParaReactivar?.codigo_unidad}' ya existe pero está inactivo. ¿Desea reactivarlo?`"
            @confirmado="manejarConfirmarReactivacionABR"
            @cancelado="manejarCancelarReactivacionABR"
        />

    </div> </template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useUnidadMedidaStore } from '../store/useUnidadMedidaStore';
import type { UnidadMedidaModel } from '../models/unidadMedidaModel';
import UnidadMedidaForm from '../components/UnidadMedidaForm.vue';
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue';

// Importaciones de PrimeVue (Patrón DEOU)
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import SelectButton from 'primevue/selectbutton';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import vTooltip from 'primevue/tooltip';

// --- Store (Patrón DEOU) ---
const store = useUnidadMedidaStore();

// --- State ---
const filtroEstado = ref<'activos' | 'inactivos' | 'todos'>('activos');
const opcionesFiltro = ref([
    { label: 'Activos', value: 'activos' },
    { label: 'Inactivos', value: 'inactivos' },
    { label: 'Todos', value: 'todos' }
]);

const dialogVisible = ref(false);
const dialogHeader = ref('');
const submitted = ref(false);
const entidad = ref<UnidadMedidaModel>(crearEntidadVacia());

// State para el modal de confirmación (Baja/Reactivar F10)
const confirmVisible = ref(false);
const confirmTitulo = ref('');
const confirmMensaje = ref('');
let entidadParaCambio: UnidadMedidaModel | null = null;

// --- Getters ---
const listaFiltrada = computed(() => {
    switch (filtroEstado.value) {
        case 'inactivos': return store.listaInactivos;
        case 'todos': return store.listaCompleta;
        case 'activos':
        default:
            return store.listaActivos;
    }
});

// --- Ciclo de Vida ---
onMounted(() => {
    store.cargarDatos(); // (F4)
    document.addEventListener('keydown', handleGlobalKeyDown);
});

onUnmounted(() => {
    document.removeEventListener('keydown', handleGlobalKeyDown);
});

// --- Funciones ---
function crearEntidadVacia(): UnidadMedidaModel {
    return {
    codigo_unidad: '',
    nombre: '',
    baja_logica: false
    };
}

function abrirDialogNuevo() {
    entidad.value = crearEntidadVacia();
    dialogHeader.value = "Nueva Unidad de Medida";
    submitted.value = false;
    dialogVisible.value = true;
}

function abrirDialogEditar(data: UnidadMedidaModel) {
    entidad.value = { ...data };
    dialogHeader.value = "Editar Unidad de Medida";
    submitted.value = false;
    dialogVisible.value = true;
}

function cerrarDialog() {
    dialogVisible.value = false;
    submitted.value = false;
    entidad.value = crearEntidadVacia();
}

// (F7) Guardar
async function guardar() {
    submitted.value = true;
    if (!entidad.value.nombre || !entidad.value.codigo_unidad) {
        return; // Validación simple
    }
    
    const exito = await store.guardarUnidad(entidad.value);

    if (exito) {
        cerrarDialog();
    }
}

// (F10) Cambiar Estado
function confirmarCambioEstado(data: UnidadMedidaModel) {
    entidadParaCambio = data;
    const accion = data.baja_logica ? 'reactivar' : 'dar de baja';
    confirmTitulo.value = data.baja_logica ? 'Confirmar Reactivación' : 'Confirmar Baja';
    confirmMensaje.value = `¿Está seguro de ${accion} la unidad "${data.nombre}"?`;
    confirmVisible.value = true;
}

function ejecutarCambioEstado() {
    if (entidadParaCambio) {
        store.toggleEstadoUnidad(entidadParaCambio);
    }
    cancelarCambioEstado();
}

function cancelarCambioEstado() {
    confirmVisible.value = false;
    entidadParaCambio = null;
    confirmTitulo.value = '';
    confirmMensaje.value = '';
}

// --- Lógica ABR V12 ---
async function manejarConfirmarReactivacionABR() {
    await store.reactivarUnidadABR();
    cerrarDialog(); 
}

function manejarCancelarReactivacionABR() {
    store.cancelarReactivacionABR();
    cerrarDialog(); 
}
// ---

function handleGlobalKeyDown(event: KeyboardEvent) { 
    if (!dialogVisible.value && !confirmVisible.value && !store.entidadInactivaParaReactivar) { 
        if (event.key === 'F4') { 
            event.preventDefault(); 
            abrirDialogNuevo(); 
        }
    } 
}
</script>