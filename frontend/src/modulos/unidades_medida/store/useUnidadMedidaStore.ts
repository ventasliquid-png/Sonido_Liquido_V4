// frontend/src/modulos/unidades_medida/store/useUnidadMedidaStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { UnidadMedidaModel } from '../models/unidadMedidaModel';
import { unidadMedidaService } from '../services/unidadMedidaService';
import notificationService from '@/services/notificationService'; // Importar el servicio canónico

export const useUnidadMedidaStore = defineStore('unidadMedida', () => {
    
    // --- State ---
    const listaCompleta = ref<UnidadMedidaModel[]>([]);
    const isLoading = ref(false);
    
    // --- Getters (Patrón DEOU - Filtro Tres Vías) ---
    const listaActivos = computed(() => listaCompleta.value.filter(u => !u.baja_logica));
    const listaInactivos = computed(() => listaCompleta.value.filter(u => u.baja_logica));

    // --- Actions (Patrón DEOU - F4, F7, F10) ---

    // (F4) Carga de datos (todos)
    async function cargarDatos() {
        if (listaCompleta.value.length > 0) return; // Evitar recargas innecesarias
        isLoading.value = true;
        try {
            listaCompleta.value = await unidadMedidaService.getUnidades('todos');
        } catch (error: any) {
            notificationService.showError("Error al cargar Unidades de Medida", error);
        } finally {
            isLoading.value = false;
        }
    }

    // (F7) Guardado (Crear o Actualizar)
    async function guardarUnidad(data: UnidadMedidaModel) {
        isLoading.value = true;
        try {
            if (data.id) {
                // Actualizar (PATCH)
                const updatedData = { nombre: data.nombre }; // Solo campos permitidos
                const response = await unidadMedidaService.updateUnidad(data.id, updatedData);
                // Actualizar store (F10)
                const index = listaCompleta.value.findIndex(u => u.id === data.id);
                if (index !== -1) {
                    listaCompleta.value[index] = response;
                }
                notificationService.showSuccess("Unidad actualizada");
            } else {
                // Crear (POST)
                const response = await unidadMedidaService.createUnidad(data);
                listaCompleta.value.push(response); // Actualizar store (F10)
                notificationService.showSuccess("Unidad creada");
            }
        } catch (error: any) {
            // Gestión de Duplicados (ABR V12)
            if (error.response && error.response.status === 409) {
                notificationService.showWarn("Conflicto", error.response.data.detail);
            } else {
                notificationService.showError("Error al guardar la unidad", error);
            }
        } finally {
            isLoading.value = false;
        }
    }

    // (F10) Baja/Reactivación
    async function cambiarEstadoUnidad(data: UnidadMedidaModel) {
        isLoading.value = true;
        const nuevoEstado = !data.baja_logica;
        try {
            const response = await unidadMedidaService.updateUnidad(data.id!, { baja_logica: nuevoEstado });
            
            const index = listaCompleta.value.findIndex(u => u.id === data.id);
            if (index !== -1) {
                listaCompleta.value[index] = response;
            }
            
            notificationService.showSuccess(`Unidad ${nuevoEstado ? 'dada de baja' : 'reactivada'}`);

        } catch (error: any) {
            notificationService.showError("Error al cambiar estado", error);
        } finally {
            isLoading.value = false;
        }
    }

    return {
        listaCompleta,
        isLoading,
        listaActivos,
        listaInactivos,
        cargarDatos,
        guardarUnidad,
        cambiarEstadoUnidad
    };
});