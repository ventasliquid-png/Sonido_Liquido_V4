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
            } catch (err: any) {
                notificationService.showError("Error al cargar sub-rubros.", err);
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
                    notificationService.showSuccess('Sub-Rubro actualizado.');
                } else { // Creación
                    await subRubroService.crearSubRubro(data as SubRubroModel);
                    notificationService.showSuccess('Sub-Rubro creado.');
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
                        // --- CORRECCIÓN DE DIRECTIVA 67 ---
                        // El 409 por duplicado activo es un WARN (Aviso), no un ERROR.
                        const msg = (typeof detail === 'string' ? detail : "El código ya existe.") || detail.message;
                        notificationService.showWarn("Conflicto de Duplicado", msg);
                        // --- FIN DE CORRECCIÓN ---
                    }
                } else {
                    notificationService.showError("Error al guardar el sub-rubro.", err);
                }
            } finally {
                this.estadoCarga = false;
            }
            return exito;
        },

        seleccionarSubRubro(subrubro: SubRubroModel | null) {
            this.subrubroSeleccionado = subrubro;
        }
        
        // Aquí faltan (eliminarSubRubro, reactivarSubRubro, cancelarReactivacion)
        // Se agregarán en la próxima directiva si es necesario.
    }
})
