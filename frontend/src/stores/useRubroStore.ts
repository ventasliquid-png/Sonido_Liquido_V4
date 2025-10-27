// frontend/src/stores/useRubroStore.ts (LLAMADAS A NOTIFICATION CORREGIDAS A ESPAÑOL)
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { RubroModel } from '@/models/rubroModel';
import { rubroApiService } from '@/services/rubroService';
import notificationService from '@/services/notificationService'; // Correcta importación por defecto

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
      const { data } = await rubroApiService.getAll(true);
      rubros.value = data;
    } catch (error) {
      // CORREGIDO: Usar mostrarError
      notificationService.mostrarError('Error al cargar rubros', (error as Error).message);
    } finally {
      estadoCarga.value = false;
    }
  }

  async function guardarRubro(rubro: RubroModel): Promise<boolean> { // Devolver boolean para indicar éxito/fallo
    estadoCarga.value = true;
    let success = false; // Flag para saber si cerrar el modal
    try {
      if (rubro.id) {
        // --- Actualización ---
        const { data: updatedRubro } = await rubroApiService.update(
          rubro.id,
          { nombre: rubro.nombre, baja_logica: rubro.baja_logica }
        );
        const index = rubros.value.findIndex(r => r.id === updatedRubro.id);
        if (index !== -1) {
          rubros.value[index] = updatedRubro;
        }
        // CORREGIDO: Usar mostrarExito
        notificationService.mostrarExito('Rubro actualizado');
        success = true;

      } else {
        // --- Creación (Manejo ABR) ---
        const response = await rubroApiService.create(rubro);
        if (response.status === 201) {
          rubros.value.push(response.data);
          // CORREGIDO: Usar mostrarExito
          notificationService.mostrarExito('Rubro creado exitosamente');
          success = true;
        } else if (response.status === 200) {
          fetchRubros(); // Recargar lista para ver el reactivado
          // CORREGIDO: Usar mostrarInfo
          notificationService.mostrarInfo('Rubro reactivado', 'El rubro ya existía y fue reactivado.');
          success = true;
        }
      }
    } catch (error: any) {
      if (error.response?.status === 409) {
        // CORREGIDO: Usar mostrarAdvertencia
        notificationService.mostrarAdvertencia('Error: Código duplicado', error.response.data.detail);
      } else {
        // CORREGIDO: Usar mostrarError
        notificationService.mostrarError('Error al guardar el rubro', error.message);
      }
      success = false; // Guardado falló
    } finally {
      estadoCarga.value = false;
      if (success) { // Solo limpiar selección si fue exitoso
          seleccionarRubro(null); // Limpia selección (esto debería ayudar a resetear el form)
      }
    }
    return success; // Devolver estado
  }


  async function eliminarRubro(id: string) {
    estadoCarga.value = true;
    try {
      const { data: rubroDadoDeBaja } = await rubroApiService.delete(id);
      // Actualizar la lista localmente en lugar de hacer fetchRubros completo
      const index = rubros.value.findIndex(r => r.id === rubroDadoDeBaja.id);
      if (index !== -1) {
        // En lugar de eliminarlo, lo marcamos como baja_logica = true
        // y lo dejamos en la lista principal, el getter 'rubrosActivos' lo filtrará.
        // Si la API ya devuelve el objeto actualizado con baja_logica: true, mejor aún.
        // Asumamos que la API devuelve el objeto con baja_logica: true
         rubros.value[index] = rubroDadoDeBaja;
         // Si la API solo devuelve un 204 o similar, hacemos la actualización manual:
         // rubros.value[index].baja_logica = true;
      }
      // CORREGIDO: Usar mostrarExito
      notificationService.mostrarExito('Rubro dado de baja');
       // Opcional: Recargar la lista completa si la lógica anterior falla
       // await fetchRubros();
    } catch (error) {
      // CORREGIDO: Usar mostrarError
      notificationService.mostrarError('Error al dar de baja', (error as Error).message);
    } finally {
      estadoCarga.value = false;
      seleccionarRubro(null); // Limpia selección
    }
  }

  function seleccionarRubro(rubro: RubroModel | null) {
    rubroSeleccionado.value = rubro ? { ...rubro } : null;
    console.log("Store: seleccionarRubro ejecutado, valor:", rubroSeleccionado.value);
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
  };
});