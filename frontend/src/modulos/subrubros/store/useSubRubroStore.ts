// frontend/src/modulos/subrubros/store/useSubRubroStore.ts
import { defineStore } from 'pinia';
import { subRubroService } from '../services/subRubroService';
import type { SubRubroModel, SubRubroUpdateModel } from '../models/subRubroModel';
import notificationService from '@/services/notificationService';

interface ABRInactivoInfo { id: string; campo: string; }

interface SubRubroState {
    subrubros: SubRubroModel[];
    subrubroSeleccionado: SubRubroModel | null;
    estadoCarga: boolean;
    // --- ESTADO ABR V12 ---
    subrubroInactivoParaReactivar: ABRInactivoInfo | null;
    // --- ESTADO FILTRO TRES VÍAS ---
    filtroEstado: string; // 'activos', 'inactivos', 'todos'
}

export const useSubRubroStore = defineStore('subrubro', {
    state: (): SubRubroState => ({
        subrubros: [],
        subrubroSeleccionado: null,
        estadoCarga: false,
        subrubroInactivoParaReactivar: null,
        filtroEstado: 'activos', // Default
    }),

    getters: {
        // Getter para la vista
        listaSubRubros: (state) => state.subrubros,
    },

    actions: {
        async fetchSubRubros() {
            this.estadoCarga = true;
            try {
                this.subrubros = await subRubroService.listarSubRubros(this.filtroEstado);
            } catch (err) { 
                notificationService.mostrarError("Error al cargar sub-rubros.");
            } finally { 
                this.estadoCarga = false; 
            }
        },
        
        setFiltroEstado(estado: string) {
            this.filtroEstado = estado;
            this.fetchSubRubros(); // Recargar datos al cambiar el filtro
        },

        async guardarSubRubro(data: SubRubroModel | SubRubroUpdateModel) {
            this.estadoCarga = true;
            let exito = false;
            try {
                if ('id' in data && data.id) { // Actualización
                    await subRubroService.actualizarSubRubro(data.id, data as SubRubroUpdateModel);
                    notificationService.mostrarExito('Sub-Rubro actualizado.');
                } else { // Creación
                    await subRubroService.crearSubRubro(data as SubRubroModel);
                    notificationService.mostrarExito('Sub-Rubro creado.');
                }
                await this.fetchSubRubros();
                exito = true;
            } catch (err: any) {
                // --- LÓGICA ABR V12 ---
                if (err.response && err.response.status === 409) {
                    const detail = err.response.data.detail;
                    if (detail && detail.status === 'EXISTE_INACTIVO') {
                        this.subrubroInactivoParaReactivar = { id: detail.id_inactivo, campo: detail.campo };
                    } else {
                        const msg = (typeof detail === 'string' ? detail : "El código ya existe.") || detail.message;
                        notificationService.mostrarError(msg);
                    }
                } else {
                    notificationService.mostrarError("Error al guardar el sub-rubro.");
                }
                // --- FIN LÓGICA ABR V12 ---
            } finally {
                this.estadoCarga = false;
            }
            return exito; // Devuelve true si la operación (guardar) fue exitosa
        },

        async eliminarSubRubro(id: string) {
            this.estadoCarga = true;
            try {
                await subRubroService.bajaLogicaSubRubro(id);
                notificationService.mostrarExito('Sub-Rubro dado de baja.');
                await this.fetchSubRubros();
            } catch (err) {
                notificationService.mostrarError("Error al eliminar el sub-rubro.");
            } finally {
                this.estadoCarga = false;
            }
        },

        async reactivarSubRubro() {
            if (!this.subrubroInactivoParaReactivar) return;
            const id = this.subrubroInactivoParaReactivar.id;
            this.estadoCarga = true;
            try {
                await subRubroService.reactivarSubRubro(id);
                notificationService.mostrarExito('Sub-Rubro reactivado.');
                await this.fetchSubRubros();
            } catch (err) {
                notificationService.mostrarError("Error al reactivar el sub-rubro.");
            } finally {
                this.estadoCarga = false;
                this.subrubroInactivoParaReactivar = null;
            }
        },

        cancelarReactivacion() {
            this.subrubroInactivoParaReactivar = null;
        },
        
        seleccionarSubRubro(subrubro: SubRubroModel | null) {
            this.subrubroSeleccionado = subrubro;
        }
    }
});