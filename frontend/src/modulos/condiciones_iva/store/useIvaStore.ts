// --- INICIO BLOQUE IVA-F-03 ---
// frontend/src/modulos/condiciones_iva/store/useIvaStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { IvaModel } from '../models/ivaModel';
import { ivaService } from '../services/ivaService';
import notificationService from '@/services/notificationService';
import { Decimal } from 'decimal.js'; // Importar Decimal para la lógica

export const useIvaStore = defineStore('iva', () => {
    
    // --- State ---
    const listaCompleta = ref<IvaModel[]>([]);
    const isLoading = ref(false);
    const ivaSeleccionada = ref<IvaModel | null>(null);

    // Estado ABR para reactivación
    const idParaReactivar = ref<string | null>(null);
    const nombreCampoParaReactivar = ref<string | null>(null);
    
    // --- Getters ---
    const listaActivos = computed(() => listaCompleta.value.filter(i => !i.baja_logica));
    const listaInactivos = computed(() => listaCompleta.value.filter(i => i.baja_logica));

    // Getters para UI
    const confirmarReactivacionVisible = computed(() => !!idParaReactivar.value);
    const nombreParaReactivar = computed(() => nombreCampoParaReactivar.value);

    // --- Actions ---

    // (F4) Carga de datos
    async function cargarDatos() {
        // Forzar recarga (lógica de UDM)
        if (listaCompleta.value.length > 0) {
            listaCompleta.value = [];
        } 
        isLoading.value = true;
        try {
            // Carga todos para el manejo interno de filtros
            listaCompleta.value = await ivaService.getIvas('todos');
        } catch (error: any) {
            notificationService.showError("Error al cargar Condiciones IVA", error);
        } finally {
            isLoading.value = false;
        }
    }

    // (F10 - Crear o Actualizar)
    async function guardarIva(data: IvaModel): Promise<boolean> {
        isLoading.value = true;
        let exito = false;
        try {
            // Asegurar que la alícuota se maneje como Decimal
            const payload = {
                ...data,
                alicuota: new Decimal(data.alicuota)
            };

            if (payload.id) {
                // Actualizar (PATCH) - Solo campos mutables
                const updatedData = { 
                    nombre: payload.nombre,
                    alicuota: payload.alicuota
                }; 
                const response = await ivaService.updateIva(payload.id, updatedData);
                
                // Actualizar store (F10)
                const index = listaCompleta.value.findIndex(i => i.id === payload.id);
                if (index !== -1) {
                    listaCompleta.value[index] = response;
                }
                notificationService.showSuccess("Condición IVA actualizada");
                exito = true;
            } else {
                // Crear (POST)
                const response = await ivaService.createIva(payload);
                if (response.status === 201) { // Creado
                    listaCompleta.value.push(response.data); 
                    notificationService.showSuccess("Condición IVA creada");
                    exito = true;
                }
            }
        } catch (error: any) {
            // [CANON V2.4.1] Canon de Separación: El Frontend interpreta el JSON de conflicto
            if (error.response && error.response.status === 409) {
                const detail = error.response.data.detail;
                
                if (detail.status === 'EXISTE_INACTIVO') {
                    // Prepara el estado para mostrar el modal de reactivación
                    idParaReactivar.value = detail.id_inactivo;
                    nombreCampoParaReactivar.value = data.codigo_iva;
                    return false; // Bloquea el cierre del formulario
                } else if (detail.status === 'EXISTE_ACTIVO') {
                    notificationService.showWarn("Conflicto", `El ${detail.campo || 'código'} '${data.codigo_iva}' ya está en uso activo.`);
                } else if (detail.status === 'TIENE_HIJOS_ACTIVOS') {
                     notificationService.showWarn("Bloqueo de Baja", detail.message);
                }
            } else {
                notificationService.showError("Error al guardar la Condición IVA", error);
            }
        } finally {
            isLoading.value = false;
        }
        return exito;
    }

    // (F10 - Baja/Reactivación)
    async function cambiarEstadoIva(data: IvaModel, nuevoEstado: boolean) {
        isLoading.value = true;
        try {
            const response = await ivaService.updateIva(data.id!, { baja_logica: nuevoEstado });
            
            // Actualizar store (F10)
            const index = listaCompleta.value.findIndex(i => i.id === data.id);
            if (index !== -1) {
                listaCompleta.value[index] = response;
            }
            
            notificationService.showSuccess(`Condición IVA ${nuevoEstado ? 'dada de baja' : 'reactivada'}`);

        } catch (error: any) {
            // Manejo de Anti-Orfandad
            if (error.response && error.response.status === 409 && error.response.data.detail.status === 'TIENE_HIJOS_ACTIVOS') {
                notificationService.showWarn("Bloqueo de Baja", error.response.data.detail.message);
            } else {
                notificationService.showError("Error al cambiar estado", error);
            }
        } finally {
            isLoading.value = false;
        }
    }
    
    // --- Lógica de Reactivación (ABR) ---
    function seleccionarIva(iva: IvaModel | null) {
        ivaSeleccionada.value = iva;
    }

    function seleccionarParaClonar(iva: IvaModel) {
        ivaSeleccionada.value = { 
            ...iva, 
            id: undefined, // Debe ser undefined para Pydantic opcional
            codigo_iva: '' // Borra el código para forzar la unicidad
        };
    }

    function cancelarReactivacion() {
        idParaReactivar.value = null;
        nombreCampoParaReactivar.value = null;
    }

    async function ejecutarReactivacion(dataOriginalForm: IvaModel) {
        if (!idParaReactivar.value) return;
        
        isLoading.value = true;
        try {
            // Reactiva el registro inactivo (forzando baja_logica: false)
            // Y actualiza el nombre/alícuota con los datos del formulario (Patrón UDM G-U-17)
            const response = await ivaService.updateIva(idParaReactivar.value, { 
                nombre: dataOriginalForm.nombre,
                alicuota: new Decimal(dataOriginalForm.alicuota),
                baja_logica: false 
            });
            
            // Reemplaza el registro viejo en el store
            const index = listaCompleta.value.findIndex(i => i.id === response.id);
            if (index !== -1) {
                listaCompleta.value[index] = response;
            }
            
            notificationService.showSuccess(`Condición IVA reactivada (Código: ${response.codigo_iva})`);
            cancelarReactivacion();

        } catch (error: any) {
            notificationService.showError("Error al reactivar la condición IVA", error);
        } finally {
            isLoading.value = false;
        }
    }

    return {
        listaCompleta,
        isLoading,
        ivaSeleccionada,
        listaActivos,
        listaInactivos,
        confirmarReactivacionVisible,
        nombreParaReactivar,
        cargarDatos,
        guardarIva,
        cambiarEstadoIva,
        seleccionarIva,
        seleccionarParaClonar,
        cancelarReactivacion,
        ejecutarReactivacion
    };
});
// --- FIN BLOQUE IVA-F-03 ---