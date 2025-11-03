<!-- frontend/src/modulos/unidades_medida/views/UnidadesMedidaView.vue -->
<template>
    <div class="card">
        <!-- 1. Toolbar (Patrón DEOU) -->
        <Toolbar class="mb-4">
            <template #start>
                <!-- NOTE: El botón se ve porque el componente Button está registrado globalmente. -->
                <Button label="Nuevo" icon="pi pi-plus" class="mr-2" @click="abrirDialogNuevo" />
            </template>
            <template #end>
                <!-- Filtro de Tres Vías (Doctrina VIL) -->
                <SelectButton 
                    v-model="filtroEstado" 
                    :options="opcionesFiltro" 
                    optionLabel="label" 
                    optionValue="value"
                    dataKey="value"
                />
            </template>
        </Toolbar>

        <!-- 2. DataTable (Patrón DEOU) -->
        <DataTable :value="listaFiltrada" :loading="store.isLoading" responsiveLayout="scroll">
            <Column field="codigo_unidad" header="Código" :sortable="true"></Column>
            <Column field="nombre" header="Nombre" :sortable="true"></Column>
            
            <!-- Columna Estado (Doctrina VIL) -->
            <Column field="baja_logica" header="Estado">
                <template #body="slotProps">
                    <Tag :severity="slotProps.data.baja_logica ? 'danger' : 'success'">
                        {{ slotProps.data.baja_logica ? 'INACTIVO' : 'ACTIVO' }}
                    </Tag>
                </template>
            </Column>

            <!-- Columna Acciones (Patrón DEOU F7, F10) -->
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

        <!-- 3. Dialog (Formulario) (Patrón DEOU) -->
        <!-- NOTE: El v-model:visible resuelve el error de prop faltante para Dialog -->
        <Dialog v-model:visible="dialogVisible" :header="dialogHeader" :modal="true" class="p-fluid">
            <UnidadMedidaForm v-model="entidad" :submitted="submitted" />
            <template #footer>
                <Button label="Cancelar" icon="pi pi-times" severity="secondary" @click="cerrarDialog" />
                <Button label="Guardar" icon="pi pi-check" @click="guardar" />
            </template>
        </Dialog>

        <!-- 4. Confirmation Modal (Doctrina VIL) -->
        <!-- NOTE: La ref debe ser correcta para evitar el Missing required prop: "visible" -->
        <ConfirmationModal 
            ref="confirmationModal"
            @confirmar="ejecutarCambioEstado"
        />

    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
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
// CORRECCIÓN CRÍTICA: La ref debe ser tipada correctamente para que Vue la resuelva.
const confirmationModal = ref<InstanceType<typeof ConfirmationModal> | null>(null); 


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
    await store.guardarUnidad(entidad.value);
    
    // Si no hay error (detectado por isLoading), cerrar
    if (!store.isLoading) {
        cerrarDialog();
    }
}

// (F10) Cambiar Estado
let entidadParaCambio: UnidadMedidaModel | null = null;

function confirmarCambioEstado(data: UnidadMedidaModel) {
    entidadParaCambio = data;
    const accion = data.baja_logica ? 'reactivar' : 'dar de baja';
    // Se asegura que la ref no sea null antes de llamar al método.
    confirmationModal.value?.abrir(`¿Está seguro de ${accion} la unidad "${data.nombre}"?`); 
}

function ejecutarCambioEstado() {
    if (entidadParaCambio) {
        store.cambiarEstadoUnidad(entidadParaCambio);
        entidadParaCambio = null;
    }
}
</script>
