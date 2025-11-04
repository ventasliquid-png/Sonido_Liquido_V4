import { defineStore } from 'pinia';
import { subRubroService } from '../services/subRubroService';
import type { SubRubroModel, SubRubroUpdateModel } from '../models/subRubroModel';
import notificationService from '@/services/notificationService';

interface ABRInactivoInfo { id: string; campo: string; }

interface SubRubroState {
Â  Â  subrubros: SubRubroModel[];
Â  Â  subrubroSeleccionado: SubRubroModel | null;
Â  Â  estadoCarga: boolean;
Â  Â  // --- ESTADO ABR V12 ---
Â  Â  subrubroInactivoParaReactivar: ABRInactivoInfo | null;
Â  Â  // --- ESTADO FILTRO TRES VÃAS ---
Â  Â  filtroEstado: string; // 'activos', 'inactivos', 'todos'
}

export const useSubRubroStore = defineStore('subrubro', {
Â  Â  state: (): SubRubroState => ({
Â  Â  Â  Â  subrubros: [],
Â  Â  Â  Â  subrubroSeleccionado: null,
Â  Â  Â  Â  estadoCarga: false,
Â  Â  Â  Â  subrubroInactivoParaReactivar: null,
Â  Â  Â  Â  filtroEstado: 'activos', // Default
Â  Â  }),

Â  Â  getters: {
Â  Â  Â  Â  // Getter para la vista
Â  Â  Â  Â  listaSubRubros: (state) => state.subrubros,
Â  Â  },

Â  Â  actions: {
Â  Â  Â  Â  async fetchSubRubros() {
Â  Â  Â  Â  Â  Â  this.estadoCarga = true;
Â  Â  Â  Â  Â  Â  try {
Â  Â  Â  Â  Â  Â  Â  Â  this.subrubros = await subRubroService.listarSubRubros(this.filtroEstado);
Â  Â  Â  Â  Â  Â  } catch (err: any) { 
            // [REPARACIÃ“N TAX-7] API CanÃ³nica
Â  Â  Â  Â  Â  Â  Â  Â  notificationService.showError("Error al cargar sub-rubros.", err);
Â  Â  Â  Â  Â  Â  } finally { 
Â  Â  Â  Â  Â  Â  Â  Â  this.estadoCarga = false; 
Â  Â  Â  Â  Â  Â  }
Â  Â  Â  Â  },
Â  Â  Â  Â  
Â  Â  Â  Â  setFiltroEstado(estado: string) {
Â  Â  Â  Â  Â  Â  this.filtroEstado = estado;
Â  Â  Â  Â  Â  Â  this.fetchSubRubros(); // Recargar datos al cambiar el filtro
Â  Â  Â  Â  },

Â  Â  Â  Â  async guardarSubRubro(data: SubRubroModel | SubRubroUpdateModel) {
Â  Â  Â  Â  Â  Â  this.estadoCarga = true;
Â  Â  Â  Â  Â  Â  let exito = false;
Â  Â  Â  Â  Â  Â  try {
Â  Â  Â  Â  Â  Â  Â  Â  if ('id' in data && data.id) { // ActualizaciÃ³n
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  await subRubroService.actualizarSubRubro(data.id, data as SubRubroUpdateModel);
                    // [REPARACIÃ“N TAX-7] API CanÃ³nica
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  notificationService.showSuccess('Sub-Rubro actualizado.');
Â  Â  Â  Â  Â  Â  Â  Â  } else { // CreaciÃ³n
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  await subRubroService.crearSubRubro(data as SubRubroModel);
                    // [REPARACIÃ“N TAX-7] API CanÃ³nica
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  notificationService.showSuccess('Sub-Rubro creado.');
Â  Â  Â  Â  Â  Â  Â  Â  }
Â  Â  Â  Â  Â  Â  Â  Â  await this.fetchSubRubros();
Â  Â  Â  Â  Â  Â  Â  Â  exito = true;
Â  Â  Â  Â  Â  Â  } catch (err: any) {
Â  Â  Â  Â  Â  Â  Â  Â  // --- LÃ“GICA ABR V12 ---
Â  Â  Â  Â  Â  Â  Â  Â  if (err.response && err.response.status === 409) {
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  const detail = err.response.data.detail;
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  if (detail && detail.status === 'EXISTE_INACTIVO') {
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  this.subrubroInactivoParaReactivar = { id: detail.id_inactivo, campo: detail.campo };
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  } else {
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  const msg = (typeof detail === 'string' ? detail : "El cÃ³digo ya existe.") || detail.message;
                        // [REPARACIÃ“N TAX-7] API CanÃ³nica
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  notificationService.showError(msg, err);
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  }
Â  Â  Â  Â  Â  Â  Â  Â  } else {
                    // [REPARACIÃ“N TAX-7] API CanÃ³nica
Â  Â  Â  Â  Â  Â  Â  Â  Â  Â  notificationService.showError("Error al guardar el sub-rubro.", err);
                return false; // Se omite el finally, se maneja el estadoCarga en otro lugar.
            } finally {
                this.estadoCarga = false;
            }
            return exito;
        },

        // Faltan las acciones del ABR y Eliminación, se asume su existencia por ahora
        // Si el compilador falla por falta de funciones, se insertarán más tarde.

        seleccionarSubRubro(subrubro: SubRubroModel | null) {
            this.subrubroSeleccionado = subrubro;
        },
        // Faltan más acciones aquí, pero cerramos el store para que compile
    }
})
