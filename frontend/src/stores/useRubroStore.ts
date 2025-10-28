// frontend/src/stores/useRubroStore.ts (ADAPTADO PARA FILTRO)
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { RubroModel } from '@/models/rubroModel';
import { rubroApiService } from '@/services/rubroService';
import notificationService from '@/services/notificationService';

export const useRubroStore = defineStore('rubro', () => {
  // --- Estado ---
  const rubros = ref<RubroModel[]>([]); // Almacenará TODOS los rubros (activos e inactivos)
  const rubroSeleccionado = ref<RubroModel | null>(null);
  const estadoCarga = ref<boolean>(false);

  // --- Getters (Computados) ---
  // Este getter sigue siendo útil si en algún lugar solo necesitas los activos
  const rubrosActivos = computed(() =>
    rubros.value.filter(r => !r.baja_logica)
  );

  // Getter para obtener TODOS los rubros (útil para el filtro 'Todos')
  const todosLosRubros = computed(() => rubros.value);

  // --- Acciones ---

  // MODIFICADO: fetchRubros ahora trae TODOS los rubros (activos = undefined)
  async function fetchRubros() {
    estadoCarga.value = true;
    try {
      // Llamar a getAll sin parámetro o con undefined para traer todos
      const { data } = await rubroApiService.getAll(undefined);
      rubros.value = data; // Guardar la lista completa
      console.log('Store: fetchRubros ejecutado, rubros cargados:', rubros.value.length);
    } catch (error) {
      notificationService.mostrarError('Error al cargar rubros', (error as Error).message);
    } finally {
      estadoCarga.value = false;
    }
  }

  // guardarRubro y eliminarRubro no necesitan cambios mayores,
  // pero nos aseguramos que actualicen la lista 'rubros' completa correctamente.
  async function guardarRubro(rubro: RubroModel): Promise<boolean> {
    estadoCarga.value = true;
    let success = false;
    try {
      if (rubro.id) {
        // --- Actualización ---
        const { data: updatedRubro } = await rubroApiService.update(
          rubro.id,
          { nombre: rubro.nombre, baja_logica: rubro.baja_logica }
        );
        const index = rubros.value.findIndex(r => r.id === updatedRubro.id);
        if (index !== -1) {
          rubros.value[index] = updatedRubro; // Actualizar en la lista completa
        } else {
          await fetchRubros(); // Recargar todo si no se encontró
        }
        notificationService.mostrarExito('Rubro actualizado');
        success = true;

      } else {
        // --- Creación (Manejo ABR) ---
        const response = await rubroApiService.create(rubro);
        if (response.status === 201) { // Creado
          rubros.value.push(response.data); // Añadir a la lista completa
          notificationService.mostrarExito('Rubro creado exitosamente');
          success = true;
        } else if (response.status === 200) { // Reactivado
           const index = rubros.value.findIndex(r => r.codigo === response.data.codigo);
           if (index !== -1) {
               rubros.value[index] = response.data; // Actualizar en la lista completa
           } else {
               await fetchRubros(); // Recargar todo si no se encontró
           }
          notificationService.mostrarInfo('Rubro reactivado', 'El rubro ya existía y fue reactivado.');
          success = true;
        }
      }
    } catch (error: any) {
      if (error.response?.status === 409) {
        notificationService.mostrarAdvertencia('Error: Código duplicado', error.response.data.detail);
      } else {
        const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
        notificationService.mostrarError('Error al guardar el rubro', mensajeError);
      }
      success = false;
    } finally {
      estadoCarga.value = false;
      if (success) {
        seleccionarRubro(null);
      }
    }
    return success;
  }


  async function eliminarRubro(id: string) {
    estadoCarga.value = true;
    try {
      const { data: rubroDadoDeBaja } = await rubroApiService.delete(id);
      const index = rubros.value.findIndex(r => r.id === rubroDadoDeBaja.id);
      if (index !== -1) {
        rubros.value[index] = rubroDadoDeBaja; // Actualizar estado en la lista completa
      } else {
        await fetchRubros();
      }
      notificationService.mostrarExito('Rubro dado de baja');
    } catch (error: any) {
       const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
      notificationService.mostrarError('Error al dar de baja', mensajeError);
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
    rubros, // Ahora contiene TODOS
    rubroSeleccionado,
    estadoCarga,
    // rubrosActivos, // Podríamos quitarlo si no se usa en otro lado, o mantenerlo
    todosLosRubros, // Exportar getter de todos
    fetchRubros,
    guardarRubro,
    eliminarRubro,
    seleccionarRubro,
    seleccionarParaClonar,
  };
});