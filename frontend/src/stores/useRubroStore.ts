// frontend/src/stores/useRubroStore.ts (COMPLETO CON ACCIÓN PARA F7)
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { RubroModel } from '@/models/rubroModel';
import { rubroApiService } from '@/services/rubroService';
import notificationService from '@/services/notificationService';

export const useRubroStore = defineStore('rubro', () => {
  // --- Estado ---
  const rubros = ref<RubroModel[]>([]);
  const rubroSeleccionado = ref<RubroModel | null>(null);
  const estadoCarga = ref<boolean>(false);

  // --- Getters (Computados) ---
  const rubrosActivos = computed(() =>
    rubros.value.filter(r => !r.baja_logica)
  );

  // --- Acciones ---

  async function fetchRubros() {
    estadoCarga.value = true;
    try {
      const { data } = await rubroApiService.getAll(true); // Asume que true trae solo activos, ajustar si es necesario
      rubros.value = data;
    } catch (error) {
      notificationService.mostrarError('Error al cargar rubros', (error as Error).message);
    } finally {
      estadoCarga.value = false;
    }
  }

  async function guardarRubro(rubro: RubroModel): Promise<boolean> {
    estadoCarga.value = true;
    let success = false;
    try {
      if (rubro.id) {
        // --- Actualización ---
        const { data: updatedRubro } = await rubroApiService.update(
          rubro.id,
          { nombre: rubro.nombre, baja_logica: rubro.baja_logica } // Solo campos actualizables
        );
        const index = rubros.value.findIndex(r => r.id === updatedRubro.id);
        if (index !== -1) {
          rubros.value[index] = updatedRubro;
        } else {
          // Si no se encuentra, podría ser mejor recargar todo
          await fetchRubros();
        }
        notificationService.mostrarExito('Rubro actualizado');
        success = true;

      } else {
        // --- Creación (Manejo ABR) ---
        const response = await rubroApiService.create(rubro);
        if (response.status === 201) { // Creado exitosamente
          rubros.value.push(response.data);
          notificationService.mostrarExito('Rubro creado exitosamente');
          success = true;
        } else if (response.status === 200) { // Reactivado (ABR)
          // La API devuelve el rubro reactivado, actualizar localmente o recargar
           const index = rubros.value.findIndex(r => r.codigo === response.data.codigo);
           if (index !== -1) {
               rubros.value[index] = response.data; // Actualizar con datos reactivados
           } else {
               await fetchRubros(); // Recargar si no se encontró (inesperado)
           }
          notificationService.mostrarInfo('Rubro reactivado', 'El rubro ya existía y fue reactivado.');
          success = true;
        }
        // Nota: El backend ahora maneja el 409 internamente en la transacción
      }
    } catch (error: any) {
      if (error.response?.status === 409) {
        notificationService.mostrarAdvertencia('Error: Código duplicado', error.response.data.detail);
      } else {
        // Manejo genérico de otros errores (red, servidor, etc.)
        const mensajeError = error.response?.data?.detail || error.message || 'Error desconocido';
        notificationService.mostrarError('Error al guardar el rubro', mensajeError);
      }
      success = false;
    } finally {
      estadoCarga.value = false;
      if (success) {
        seleccionarRubro(null); // Limpia selección solo si fue exitoso
      }
    }
    return success;
  }


  async function eliminarRubro(id: string) {
    estadoCarga.value = true;
    try {
      const { data: rubroDadoDeBaja } = await rubroApiService.delete(id); // delete ahora es baja lógica en backend
      const index = rubros.value.findIndex(r => r.id === rubroDadoDeBaja.id);
      if (index !== -1) {
         // Reemplazar con la data devuelta que tiene baja_logica = true
        rubros.value[index] = rubroDadoDeBaja;
      } else {
        await fetchRubros(); // Recargar si no se encontró (inesperado)
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
    // Crear una copia para evitar mutaciones accidentales del estado original
    rubroSeleccionado.value = rubro ? { ...rubro } : null;
    console.log("Store: seleccionarRubro ejecutado, valor:", rubroSeleccionado.value);
  }

  // NUEVO: Acción para preparar clonación (F7)
  function seleccionarParaClonar(rubroOriginal: RubroModel) {
    const rubroClonado: RubroModel = {
      ...rubroOriginal, // Copiar todos los datos
      id: null,       // Borrar ID para indicar que es nuevo
      codigo: '',     // Borrar Código para forzar al usuario a ingresar uno nuevo
      baja_logica: false // Un clon siempre empieza activo
    };
    rubroSeleccionado.value = rubroClonado; // Establecer como selección actual
    console.log("Store: seleccionarParaClonar ejecutado, valor clonado:", rubroSeleccionado.value);
  }

  return {
    rubros,
    rubroSeleccionado,
    estadoCarga,
    rubrosActivos,
    fetchRubros,
    guardarRubro,
    eliminarRubro,
    seleccionarRubro,
    seleccionarParaClonar, // Exportar nueva acción
  };
});