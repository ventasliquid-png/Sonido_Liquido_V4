// frontend/src/modulos/rubros/store/useRubroStore.ts (VERSIÓN 2.3.2 - Doctrina VIL + Reactivación Directa)
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
// --- INICIO REPARACIÓN G-R-11 (Refactorización) ---
import type { RubroModel, RubroUpdateModel } from '../models/rubroModel';
import { rubroApiService } from '../services/rubroService';
// Componentes globales (rutas @/) no cambian
import notificationService from '@/services/notificationService';
// --- FIN REPARACIÓN G-R-11 ---

export const useRubroStore = defineStore('rubro', () => {
  // --- Estado ---
  const rubros = ref<RubroModel[]>([]);
  const rubroSeleccionado = ref<RubroModel | null>(null);
  const estadoCarga = ref<boolean>(false);
  
  // --- INICIO DOCTRINA VIL (Filtro de Tres Vías) ---
  const filtroEstado = ref<string>('activos');
  // --- FIN DOCTRINA VIL ---

  // --- INICIO V2: Estado para el modal de reactivación (ABR) ---
  const confirmarReactivacionVisible = ref(false);
  const idParaReactivar = ref<string | null>(null);
  const nombreParaReactivar = ref<string | null>(null);
  // --- FIN V2 ---


  // --- Getters (Computados) ---
  const todosLosRubros = computed(() => rubros.value);

  // --- Acciones ---
  
  // --- INICIO DOCTRINA VIL (Filtro de Tres Vías) ---
  async function fetchRubros() {
    estadoCarga.value = true;
    try {
      // Se pasa el 'filtroEstado' del store al backend
      const { data } = await rubroApiService.getAll(filtroEstado.value);
      rubros.value = data;
      console.log(`Store: fetchRubros ejecutado [${filtroEstado.value}], rubros cargados: ${rubros.value.length}`);
    } catch (error) {
      notificationService.showError('Error al cargar rubros', (error as Error).message);
    } finally {
      estadoCarga.value = false;
    }
  }

  function setFiltroEstado(estado: string) {
    filtroEstado.value = estado;
    fetchRubros(); // Vuelve a cargar los datos con el nuevo filtro
  }
  // --- FIN DOCTRINA VIL ---

  async function guardarRubro(rubro: RubroModel): Promise<boolean> {
    estadoCarga.value = true;
    let success = false;
    try {
      if (rubro.id) {
        // --- Actualización (PATCH) ---
        const updatePayload: RubroUpdateModel = {
          nombre: rubro.nombre,
          baja_logica: rubro.baja_logica
        };
        const { data: updatedRubro } = await rubroApiService.update(rubro.id, updatePayload);

        const index = rubros.value.findIndex(r => r.id === updatedRubro.id);
        if (index !== -1) {
          rubros.value[index] = updatedRubro;
        } else {
          await fetchRubros();
        }
        notificationService.showSuccess('Rubro actualizado');
        success = true;

      } else {
        // --- Creación (POST) ---
        const response = await rubroApiService.create(rubro);

        if (response.status === 201) { // Creado
          rubros.value.push(response.data);
          notificationService.showSuccess('Rubro creado exitosamente');
          success = true;
        }
      }
    } catch (error: any) {
      if (error.response?.status === 409 && error.response.data.detail) {
        const detail = error.response.data.detail;

        if (detail.status === "EXISTE_INACTIVO") {
          idParaReactivar.value = detail.id_inactivo;
          nombreParaReactivar.value = rubro.nombre; 
          confirmarReactivacionVisible.value = true;

        } else if (detail.status === "EXISTE_ACTIVO") {
          notificationService.showWarn('Error: Código duplicado', detail.message);
        } else {
          notificationService.showError('Error de Conflicto', detail.message || 'Error desconocido');
        }

      } else {
        const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
        notificationService.showError('Error al guardar el rubro', mensajeError);
      }
      success = false;
    } finally {
      estadoCarga.value = false;
      if (success) {
        seleccionarRubro(null);
        await fetchRubros();
      }
    }
    return success;
  }


  // --- INICIO REPARACIÓN DOCTRINAL (DEOU V2) ---
  // Modificado para aceptar un ID opcional (para Reactivación Directa)
  async function ejecutarReactivacion(id: string | null = null) {
    const idTarget = id || idParaReactivar.value; // Usa el ID de la fila o el del ABR
    
    if (!idTarget) {
      notificationService.showError('Error', 'No se encontró ID para reactivar.');
      return;
    }

    estadoCarga.value = true;
    try {
      const updatePayload: RubroUpdateModel = {
        baja_logica: false
      };

      // REPARACIÓN G-R-11: El 'rubroApiService' ya no existe en 'delete',
      // pero el 'update' sí devuelve el objeto actualizado.
      const { data: updatedRubro } = await rubroApiService.update(idTarget, updatePayload);
      
      await fetchRubros(); // Recargar la lista actual
      notificationService.showSuccess('Rubro reactivado');

    } catch (error: any) {
      const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
      notificationService.showError('Error al reactivar el rubro', mensajeError);
    } finally {
      // Si estábamos en un ABR, cerramos todo. Si fue directo, esto no hace nada.
      cancelarReactivacionABR(); 
      estadoCarga.value = false;
    }
  }

  // Esta función es solo para el flujo ABR (conflicto 409)
  function cancelarReactivacionABR() {
    confirmarReactivacionVisible.value = false;
    idParaReactivar.value = null;
    nombreParaReactivar.value = null;
    seleccionarRubro(null); // Limpiar el formulario
  }
  // --- FIN REPARACIÓN DOCTRINAL ---


  async function eliminarRubro(id: string) {
    estadoCarga.value = true;
    try {
      // REPARACIÓN G-R-11: La API 'delete' (corregida en G-R-04) ahora devuelve 204 (void)
      await rubroApiService.delete(id);
      await fetchRubros(); 
      notificationService.showSuccess('Rubro dado de baja');

    } catch (error: any) {
        const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
      notificationService.showError('Error al dar de baja', mensajeError);
    } finally {
      estadoCarga.value = false;
      seleccionarRubro(null);
    }
  }

  function seleccionarRubro(rubro: RubroModel | null) {
    rubroSeleccionado.value = rubro ? { ...rubro } : null;
    console.log("Store: seleccionarRubro ejecutado, valor:", rubroSeleccionado.value);
  }

  function seleccionarParaClonar(rubroOriginal: RubroModel) {
    const rubroClonado: RubroModel = {
      ...rubroOriginal,
      id: null,
      codigo: '',
      baja_logica: false
    };
    rubroSeleccionado.value = rubroClonado;
    console.log("Store: seleccionarParaClonar ejecutado, valor clonado:", rubroSeleccionado.value);
  }

  return {
    rubros,
    rubroSeleccionado,
    estadoCarga,
    todosLosRubros,
    fetchRubros,
    guardarRubro,
    eliminarRubro,
    seleccionarRubro,
    seleccionarParaClonar,

    // --- INICIO VIL ---
    filtroEstado,
    setFiltroEstado,
    // --- FIN VIL ---

    // --- INICIO V2: Exportar estado y acciones del modal ---
    confirmarReactivacionVisible,
    nombreParaReactivar,
    ejecutarReactivacion,
    cancelarReactivacion: cancelarReactivacionABR, // Renombrado para claridad
    // --- FIN V2 ---
  };
});
