// INICIO REPARACIÓN MANUAL G-U-20 (Manejo de JSON ABR)
// frontend/src/modulos/unidades_medida/store/useUnidadMedidaStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { UnidadMedidaModel } from '../models/unidadMedidaModel';
import { unidadMedidaService } from '../services/unidadMedidaService';
import notificationService from '@/services/notificationService'; 

interface ABRInactivoInfo { id: string; campo: string; detail: any; }

export const useUnidadMedidaStore = defineStore('unidadMedida', () => {

    const listaCompleta = ref<UnidadMedidaModel[]>([]);
    const isLoading = ref(false);
    
    const entidadInactivaParaReactivar = ref<ABRInactivoInfo | null>(null);
    const datosNuevosParaReactivar = ref<UnidadMedidaModel | null>(null);

    const listaActivos = computed(() => listaCompleta.value.filter(u => !u.baja_logica));
    const listaInactivos = computed(() => listaCompleta.value.filter(u => u.baja_logica));

    async function cargarDatos() {
        if (listaCompleta.value.length > 0) {
            listaCompleta.value = [];
        }
        isLoading.value = true;
        try {
            listaCompleta.value = await unidadMedidaService.getUnidades('todos');
        } catch (error: any) {
            notificationService.showError("Error al cargar Unidades de Medida", error);
        } finally {
            isLoading.value = false;
        }
    }

    async function guardarUnidad(data: UnidadMedidaModel): Promise<boolean> {
        isLoading.value = true;
        let exito = false;
        try {
            if (data.id) {
                // Actualizar (PATCH)
                const updatedData = { nombre: data.nombre }; 
                const response = await unidadMedidaService.updateUnidad(data.id, updatedData);
                const index = listaCompleta.value.findIndex(u => u.id === data.id);
                if (index !== -1) {
                    listaCompleta.value[index] = response;
                }
                notificationService.showSuccess("Unidad actualizada");
                exito = true;
            } else {
                // Crear (POST)
                const response = await unidadMedidaService.createUnidad(data);
                
                if (response.status === 201) { // Creado
                    listaCompleta.value.push(response.data); 
                    notificationService.showSuccess("Unidad creada");
                    exito = true;
                }
            }
        } catch (error: any) {
            if (error.response && error.response.status === 409) {
                const detail = error.response.data.detail;
                
                // --- REPARACIÓN G-U-20: Eliminar parseo de string ---
                if (typeof detail === 'object' && detail.status === 'EXISTE_INACTIVO') {
                    // Lógica ABR V12 (SubRubros)
                    datosNuevosParaReactivar.value = data; // Guardamos los datos del form
                    entidadInactivaParaReactivar.value = { 
                        id: detail.id_inactivo, 
                        campo: detail.campo, 
                        detail: detail // Guardamos el JSON
                    };
                } else {
                    // Duplicado Activo
                    const msg = (typeof detail === 'string') ? detail : "Conflicto de duplicado";
                    notificationService.showWarn("Conflicto", msg);
                }
                // --- FIN REPARACIÓN G-U-20 ---
            } else {
                notificationService.showError("Error al guardar la unidad", error);
            }
        } finally {
            isLoading.value = false;
        }
        return exito; 
    }

    // (F10) Baja/Reactivación Directa (Toggle)
    async function toggleEstadoUnidad(data: UnidadMedidaModel) {
        isLoading.value = true;
        
        const idTarget = data.id;
        if (!idTarget) {
            notificationService.showError("Error", "ID no encontrado para cambiar estado.");
            isLoading.value = false;
            return;
        }

        const nuevoEstado = !data.baja_logica; // Invierte el estado
        
        try {
            const payload = {
                nombre: data.nombre, // Usa el nombre existente
                baja_logica: nuevoEstado
            };

            const response = await unidadMedidaService.updateUnidad(idTarget, payload);

            const index = listaCompleta.value.findIndex(u => u.id === idTarget);
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
    
    // (ABR) Reactivación desde 409 (Siempre FORZA baja_logica: false)
    async function reactivarUnidadABR() {
        if (!entidadInactivaParaReactivar.value || !datosNuevosParaReactivar.value) {
             notificationService.showError("Error", "Datos de reactivación no encontrados.");
             return;
        }
        
        isLoading.value = true;
        
        const idTarget = entidadInactivaParaReactivar.value.id;
        
        try {
            const payload = {
                nombre: datosNuevosParaReactivar.value.nombre, // Usa el nombre del formulario
                baja_logica: false // Forzamos FALSE
            };

            const response = await unidadMedidaService.updateUnidad(idTarget, payload);

            const index = listaCompleta.value.findIndex(u => u.id === idTarget);
            if (index !== -1) {
                listaCompleta.value[index] = response;
            } else {
                listaCompleta.value.push(response); // Si no estaba en la lista
            }
            notificationService.showSuccess(`Unidad reactivada`);

        } catch (error: any) {
            notificationService.showError("Error al reactivar la unidad", error);
        } finally {
            isLoading.value = false;
            cancelarReactivacionABR();
        }
    }

    function cancelarReactivacionABR() {
        entidadInactivaParaReactivar.value = null;
        datosNuevosParaReactivar.value = null;
    }

    return {
        listaCompleta,
        isLoading,
        listaActivos,
        listaInactivos,
        // ABR V12
        entidadInactivaParaReactivar,
        datosNuevosParaReactivar,
        cancelarReactivacionABR,
        //---
        cargarDatos,
        guardarUnidad,
        toggleEstadoUnidad, 
        reactivarUnidadABR  
    };
});
// FIN REPARACIÓN MANUAL G-U-20