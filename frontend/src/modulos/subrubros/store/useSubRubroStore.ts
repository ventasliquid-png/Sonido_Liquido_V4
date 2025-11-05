// frontend/src/modulos/subrubros/store/useSubRubroStore.ts
// VERSIÓN 2.4 - Lógica ABR V12 Corregida (Fallo 2)
import { defineStore } from 'pinia';
import { ref, computed } from 'vue'; 
import { subRubroService } from '../services/subRubroService';
import type { SubRubroModel, SubRubroUpdateModel } from '../models/subRubroModel';
import notificationService from '@/services/notificationService';

interface ABRInactivoInfo { id: string; campo: string; }

export const useSubRubroStore = defineStore('subrubro', () => {
    
    const subrubros = ref<SubRubroModel[]>([]);
    const subrubroSeleccionado = ref<SubRubroModel | null>(null);
    const estadoCarga = ref<boolean>(false);
    const subrubroInactivoParaReactivar = ref<ABRInactivoInfo | null>(null);
    const filtroEstado = ref<string>('activos'); 

    // --- INICIO CORRECCIÓN FALLO 2 (ABR V12) ---
    // Almacena los datos nuevos (del formulario) mientras se confirma la reactivación
    const datosNuevosParaReactivar = ref<SubRubroUpdateModel | null>(null);
    // --- FIN CORRECCIÓN FALLO 2 ---

    const listaSubRubros = computed(() => subrubros.value);

    async function fetchSubRubros() {
        estadoCarga.value = true;
        try {
            subrubros.value = await subRubroService.listarSubRubros(filtroEstado.value);
        } catch (err: any) {
            notificationService.showError("Error al cargar sub-rubros.", err);
        } finally {
            estadoCarga.value = false;
        }
    }
    
    function setFiltroEstado(estado: string) {
        filtroEstado.value = estado;
        fetchSubRubros(); 
    }

    async function guardarSubRubro(data: SubRubroModel | SubRubroUpdateModel): Promise<boolean> {
        estadoCarga.value = true;
        let exito = false;
        try {
            if ('id' in data && data.id) { 
                await subRubroService.actualizarSubRubro(data.id, data as SubRubroUpdateModel);
                notificationService.showSuccess('Sub-Rubro actualizado.');
            } else { 
                await subRubroService.crearSubRubro(data as SubRubroModel);
                notificationService.showSuccess('Sub-Rubro creado.');
            }
            await fetchSubRubros();
            exito = true;
        } catch (err: any) {
            if (err.response && err.response.status === 409) {
                const detail = err.response.data.detail;
                if (detail && detail.status === 'EXISTE_INACTIVO') {
                    // --- INICIO CORRECCIÓN FALLO 2 (ABR V12) ---
                    // Guardamos los datos nuevos (ej. "Varios 2 mod") antes de preguntar
                    datosNuevosParaReactivar.value = data as SubRubroUpdateModel; 
                    // --- FIN CORRECCIÓN FALLO 2 ---
                    subrubroInactivoParaReactivar.value = { id: detail.id_inactivo, campo: detail.campo };
                } else {
                    const msg = (typeof detail === 'string' ? detail : "El código ya existe.") || detail.message;
                    notificationService.showWarn("Conflicto de Duplicado", msg);
                }
            } else {
                notificationService.showError("Error al guardar el sub-rubro.", err.message); 
            }
        } finally {
            estadoCarga.value = false;
        }
        return exito;
    }

    function seleccionarSubRubro(subrubro: SubRubroModel | null) {
        subrubroSeleccionado.value = subrubro ? { ...subrubro } : null;
    }

    async function eliminarSubRubro(id: string) {
        estadoCarga.value = true;
        try {
            await subRubroService.bajaLogicaSubRubro(id);
            await fetchSubRubros(); 
            notificationService.showSuccess('Sub-Rubro dado de baja.');
        } catch (error: any) {
            const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
            notificationService.showError('Error al dar de baja', mensajeError);
        } finally {
            estadoCarga.value = false;
            seleccionarSubRubro(null);
        }
    }

    async function reactivarSubRubro(id: string | null = null) {
        // ID opcional para la reactivación directa (Fallo 3)
        const idParaActualizar = id || subrubroInactivoParaReactivar.value?.id;

        if (!idParaActualizar) {
            notificationService.showError('Error', 'No se encontró ID para reactivar.');
            return;
        }
        estadoCarga.value = true;
        try {
            // --- INICIO CORRECCIÓN FALLO 2 (ABR V12) ---
            // Si hay datos nuevos (del formulario F10), los usamos.
            // Si no (reactivación directa Fillo 3), solo reactivamos.
            const updatePayload: SubRubroUpdateModel = { 
                ...(datosNuevosParaReactivar.value || {}), // Aplica el nuevo nombre si existe
                baja_logica: false 
            };
            // --- FIN CORRECCIÓN FALLO 2 ---

            await subRubroService.actualizarSubRubro(idParaActualizar, updatePayload);
            notificationService.showSuccess('Sub-Rubro reactivado');
            await fetchSubRubros();
        } catch (error: any) {
            const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
            notificationService.showError('Error al reactivar', mensajeError);
        } finally {
            cancelarReactivacion();
            estadoCarga.value = false;
        }
    }

    function cancelarReactivacion() {
        subrubroInactivoParaReactivar.value = null;
        datosNuevosParaReactivar.value = null; // Limpiar los datos nuevos
        seleccionarSubRubro(null); 
    }

    return {
        subrubros,
        subrubroSeleccionado,
        estadoCarga,
        subrubroInactivoParaReactivar,
        filtroEstado,
        listaSubRubros,
        fetchSubRubros,
        setFiltroEstado,
        guardarSubRubro,
        seleccionarSubRubro,
        eliminarSubRubro, // Asegurado (Fallo de Directiva 79)
        reactivarSubRubro,
        cancelarReactivacion
    };
});
