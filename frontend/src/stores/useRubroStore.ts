// frontend/src/stores/useRubroStore.ts (VERSIÓN 2 - Lógica de "Preguntar")
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { RubroModel, RubroUpdateModel } from '@/models/rubroModel';
import { rubroApiService } from '@/services/rubroService';
import notificationService from '@/services/notificationService';

export const useRubroStore = defineStore('rubro', () => {
  // --- Estado ---
  const rubros = ref<RubroModel[]>([]);
  const rubroSeleccionado = ref<RubroModel | null>(null);
  const estadoCarga = ref<boolean>(false);
  
  // --- INICIO V2: Estado para el modal de reactivación ---
  const confirmarReactivacionVisible = ref(false);
  // Guardará el ID del rubro inactivo que el backend nos envió
  const idParaReactivar = ref<string | null>(null); 
  // Guardará el nombre para mostrar en el mensaje de confirmación
  const nombreParaReactivar = ref<string | null>(null);
  // --- FIN V2 ---


  // --- Getters (Computados) ---
  const todosLosRubros = computed(() => rubros.value);

  // --- Acciones ---
  async function fetchRubros() {
    estadoCarga.value = true;
    try {
      const { data } = await rubroApiService.getAll(undefined);
      rubros.value = data;
      console.log('Store: fetchRubros ejecutado, rubros cargados:', rubros.value.length);
    } catch (error) {
      notificationService.showError('Error al cargar rubros', (error as Error).message);
    } finally {
      estadoCarga.value = false;
    }
  }

  // --- INICIO V2: MODIFICADO guardarRubro ---
  async function guardarRubro(rubro: RubroModel): Promise<boolean> {
    estadoCarga.value = true;
    let success = false;
    try {
      if (rubro.id) {
        // --- Actualización (PATCH) ---
        // (Esta lógica no cambia, solo se usa para editar)
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
        notificationService.mostrarExito('Rubro actualizado');
        success = true;

      } else {
        // --- Creación (POST) ---
        // El backend V12 ya NO devuelve 200 (reactivado).
        // Solo devuelve 201 (creado) o 409 (conflicto).
        const response = await rubroApiService.create(rubro);
        
        // (La lógica del 'else if (response.status === 200)' se elimina)
        if (response.status === 201) { // Creado
          rubros.value.push(response.data);
          notificationService.mostrarExito('Rubro creado exitosamente');
          success = true;
        }
      }
    } catch (error: any) {
      // --- AQUI MANEJAMOS EL 409 ---
      if (error.response?.status === 409 && error.response.data.detail) {
        const detail = error.response.data.detail;

        if (detail.status === "EXISTE_INACTIVO") {
          // ¡Encontramos uno inactivo!
          // Guardamos los datos para el modal de confirmación
          idParaReactivar.value = detail.id_inactivo;
          nombreParaReactivar.value = detail.nombre;
          // Abrimos el modal (la vista se encargará de mostrarlo)
          confirmarReactivacionVisible.value = true;

        } else if (detail.status === "EXISTE_ACTIVO") {
          // El código ya existe y está activo
          notificationService.mostrarAdvertencia('Error: Código duplicado', detail.message);
        } else {
          // Otro tipo de 409 (inesperado)
          notificationService.showError('Error de Conflicto', detail.message || 'Error desconocido');
        }

      } else {
        // Otro tipo de error (500, 404, etc.)
        const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
        notificationService.showError('Error al guardar el rubro', mensajeError);
      }
      success = false;
    } finally {
      estadoCarga.value = false;
      if (success) {
        seleccionarRubro(null); // Limpiar selección solo si fue exitoso
      }
    }
    return success;
  }
  // --- FIN V2: MODIFICADO guardarRubro ---


  // --- INICIO V2: Nuevas acciones para el modal ---
  async function ejecutarReactivacion() {
    if (!idParaReactivar.value) {
      notificationService.showError('Error', 'No se encontró ID para reactivar.');
      return;
    }

    estadoCarga.value = true;
    try {
      // Usamos la lógica de 'update' para reactivar (PATCH)
      const updatePayload: RubroUpdateModel = { 
        baja_logica: false 
        // Opcional: podríamos también actualizar el nombre si quisiéramos
        // nombre: rubroParaReactivar.value.nombre 
      };

      const { data: updatedRubro } = await rubroApiService.update(idParaReactivar.value, updatePayload);

      // Actualizar la lista local
      const index = rubros.value.findIndex(r => r.id === updatedRubro.id);
      if (index !== -1) {
        rubros.value[index] = updatedRubro;
      } else {
        await fetchRubros(); // Recargar todo si no se encontró
      }
      notificationService.mostrarExito('Rubro reactivado');

    } catch (error: any) {
      const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
      notificationService.showError('Error al reactivar el rubro', mensajeError);
    } finally {
      // Cerrar y limpiar el modal
      cancelarReactivacion();
      estadoCarga.value = false;
    }
  }

  function cancelarReactivacion() {
    confirmarReactivacionVisible.value = false;
    idParaReactivar.value = null;
    nombreParaReactivar.value = null;
    seleccionarRubro(null); // Limpiar el formulario
  }
  // --- FIN V2 ---


  async function eliminarRubro(id: string) {
    estadoCarga.value = true;
    try {
      const { data: rubroDadoDeBaja } = await rubroApiService.delete(id);
      const index = rubros.value.findIndex(r => r.id === rubroDadoDeBaja.id);
      if (index !== -1) {
        rubros.value[index] = rubroDadoDeBaja;
      } else {
        await fetchRubros();
      }
      notificationService.mostrarExito('Rubro dado de baja');
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

    // --- INICIO V2: Exportar estado y acciones del modal ---
    confirmarReactivacionVisible,
    nombreParaReactivar,
    ejecutarReactivacion,
    cancelarReactivacion,
    // --- FIN V2 ---
  };
});
