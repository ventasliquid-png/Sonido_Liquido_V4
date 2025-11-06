<template>
    <div class="card">
        
        <Toolbar class="mb-4">
            <template #start>
                <Button label="Nueva Condición (F4)" icon="pi pi-plus" class="mr-2" @click="abrirDialogNuevo" v-tooltip.bottom="'F4 - Alta Rápida'" />
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

        <DataTable :value="listaFiltrada" :loading="store.isLoading" responsiveLayout="scroll" :rowStyle="rowStyle">
            
            <Column field="codigo_iva" header="Código" :sortable="true"></Column>
            <Column field="nombre" header="Nombre" :sortable="true"></Column>
            <Column field="alicuota" header="Alícuota (%)" :sortable="true">
                <template #body="slotProps">
                    {{ slotProps.data.alicuota }}%
                </template>
            </Column>

            <Column field="baja_logica" header="Estado">
                <template #body="slotProps">
                    <Tag :severity="slotProps.data.baja_logica ? 'danger' : 'success'">
                        {{ slotProps.data.baja_logica ? 'INACTIVO' : 'ACTIVO' }}
                    </Tag>
                </template>
            </Column>

            <Column :exportable="false" style="min-width:14rem">
                <template #body="slotProps">
                    <Button 
                        icon="pi pi-copy" 
                        class="p-button-rounded p-button-secondary mr-2" 
                        v-tooltip.top="'F7 - Clonar'" 
                        @click="abrirDialogClonar(slotProps.data)" 
                    />
                    <Button 
                        v-if="!slotProps.data.baja_logica"
                        icon="pi pi-pencil" 
                        class="p-button-rounded p-button-info mr-2" 
                        v-tooltip.top="'Editar'" 
                        @click="abrirDialogEditar(slotProps.data)" 
                    />
                    <Button 
                        v-if="!slotProps.data.baja_logica"
                        icon="pi pi-trash"
                        severity="danger"
                        class="p-button-rounded mr-2"
                        v-tooltip.top="'Dar de Baja'"
                        @click="confirmarCambioEstado(slotProps.data)" 
                    />
                    <Button 
                        v-if="slotProps.data.baja_logica"
                        icon="pi pi-check"
                        severity="success"
                        class="p-button-rounded mr-2"
                        v-tooltip.top="'Reactivar'"
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
            @show="onDialogShow" 
        >
            <IvaForm 
                ref="ivaFormRef"
                v-model="entidad" 
                :submitted="submitted" 
                @guardar="guardar"
            />
            <template #footer>
                <Button label="Cancelar (Esc)" icon="pi pi-times" severity="secondary" @click="cerrarDialog" text />
                <Button label="Guardar (F10)" icon="pi pi-check" @click="guardar" autofocus />
            </template>
        </Dialog>

        <ConfirmationModal 
            v-if="confirmVisible"
            :visible="confirmVisible"
            :titulo="confirmTitulo"
            :message="confirmMensaje"
            @update:visible="confirmVisible = $event"
            @confirmado="ejecutarBaja"
            @cancelado="cancelarBaja"
        />

        <ConfirmationModal 
            v-if="store.confirmarReactivacionVisible"
            :visible="store.confirmarReactivacionVisible"
            titulo="Conflicto: Reactivación Requerida"
            :message="`El código de Condición IVA '${store.nombreParaReactivar}' ya existe pero está inactivo. ¿Desea reactivarlo?`"
            @update:visible="manejarCancelarReactivacionABR"
            @confirmado="ejecutarReactivacionYGuardar"
            @cancelado="manejarCancelarReactivacionABR"
        />

        </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue'; // REPARACIÓN: Importar nextTick
import { useIvaStore } from '../store/useIvaStore';
import type { IvaModel } from '../models/ivaModel';
import IvaForm from '../components/IvaForm.vue';
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue'; 

// Importaciones de PrimeVue
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import SelectButton from 'primevue/selectbutton';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import vTooltip from 'primevue/tooltip';
import { Decimal } from 'decimal.js'; 

// --- Store ---
const store = useIvaStore();

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
const entidad = ref<IvaModel>(crearEntidadVacia());
const confirmVisible = ref(false);
const confirmTitulo = ref('');
const confirmMensaje = ref('');
let entidadParaCambioEstado: IvaModel | null = null;
let entidadParaGuardar: IvaModel | null = null;

// --- REPARACIÓN G-U-35: Ref al formulario ---
const ivaFormRef = ref<InstanceType<typeof IvaForm> | null>(null);

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

// --- Funciones de Utilidad ---
function crearEntidadVacia(): IvaModel {
    return {
        codigo_iva: '',
        nombre: '',
        alicuota: new Decimal(0), 
        baja_logica: false
    };
}
const rowStyle = (data: IvaModel) => {
    return data.baja_logica ? { fontStyle: 'italic', opacity: '0.6' } : {};
};

// --- Manejo de Dialogs (F4, F7) ---
function abrirDialogNuevo() {
    entidad.value = crearEntidadVacia();
    dialogHeader.value = "Nueva Condición IVA";
    submitted.value = false;
    dialogVisible.value = true;
}

function abrirDialogEditar(data: IvaModel) {
    store.seleccionarIva(data);
    entidad.value = { ...data };
    dialogHeader.value = "Editar Condición IVA";
    submitted.value = false;
    dialogVisible.value = true;
}

function abrirDialogClonar(data: IvaModel) {
    store.seleccionarParaClonar(data);
    entidad.value = store.ivaSeleccionada!
    dialogHeader.value = "Clonar Condición IVA";
    submitted.value = false;
    dialogVisible.value = true;
}

function cerrarDialog() {
    dialogVisible.value = false;
    submitted.value = false;
    entidad.value = crearEntidadVacia();
    entidadParaGuardar = null;
    store.seleccionarIva(null);
}

// --- REPARACIÓN G-U-35: Lógica de Foco (Doctrina T149) ---
async function onDialogShow() {
    await nextTick(); // Esperar que el DOM del Dialog se estabilice
    
    // El 'entidad' ya ha sido seteado por abrirDialogNuevo/Editar
    if (entidad.value.id) {
        // Editando
        ivaFormRef.value?.focusNombre();
    } else {
        // Alta o Clonar
        ivaFormRef.value?.focusCodigo();
    }
}

// --- F10: Guardar ---
async function guardar() {
    submitted.value = true;
    if (!entidad.value.nombre || !entidad.value.codigo_iva || entidad.value.alicuota === null) {
        return; 
    }
    
    entidadParaGuardar = { ...entidad.value };
    
    const exito = await store.guardarIva(entidadParaGuardar);
    
    if (exito) {
        cerrarDialog();
    }
}

// --- Lógica ABR V12 (G-U-15) ---
async function ejecutarReactivacionYGuardar() {
    if (!entidadParaGuardar) return;
    await store.ejecutarReactivacion(entidadParaGuardar);
    cerrarDialog();
}

function manejarCancelarReactivacionABR() {
    store.cancelarReactivacion();
    cerrarDialog();
}
// ---

// --- F10: Cambio de Estado (Baja/Reactivar) ---
function confirmarCambioEstado(data: IvaModel) {
    entidadParaCambioEstado = data;
    const accion = data.baja_logica ? 'reactivar' : 'dar de baja';
    confirmTitulo.value = data.baja_logica ? 'Confirmar Reactivación' : 'Confirmar Baja';
    confirmMensaje.value = `¿Está seguro de ${accion} la Condición IVA "${data.nombre}"?`;
    confirmVisible.value = true;
}

async function ejecutarBaja() { 
    if (entidadParaCambioEstado) {
        await store.cambiarEstadoIva(entidadParaCambioEstado, !entidadParaCambioEstado.baja_logica);
    }
    cancelarBaja();
}

function cancelarBaja() {
    confirmVisible.value = false;
    entidadParaCambioEstado = null;
    confirmTitulo.value = '';
    confirmMensaje.value = '';
}

// --- F4: Alta Rápida ---
function handleGlobalKeyDown(event: KeyboardEvent) { 
    if (!dialogVisible.value && !confirmVisible.value && !store.confirmarReactivacionVisible) { 
        if (event.key === 'F4') { 
            event.preventDefault(); 
            abrirDialogNuevo(); 
        }
    } 
}

</script>