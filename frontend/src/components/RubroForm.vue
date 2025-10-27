<template>
  <Dialog
    :visible="visible"
    modal
    :header="formTitle"
    :style="{ width: '30rem' }"
    @update:visible="cerrarModal"
    @keydown.enter.prevent="enviarFormulario"
    @keydown.f10.prevent="enviarFormulario"
    @keydown.esc.prevent="cerrarModal"
  >
    <div class="p-fluid grid formgrid">
      <div class="field col-12 md:col-6">
        <label for="codigo">Código</label>
        <InputText
          id="codigo"
          v-model.trim="formData.codigo"
          maxlength="3"
          :disabled="esEdicion"
          aria-describedby="codigo-help"
          @input="formatCodigo($event)"
        />
        <small id="codigo-help">Máx 3 caracteres. No se puede cambiar si edita.</small>
      </div>
      <div class="field col-12 md:col-6">
        <label for="nombre">Nombre</label>
        <InputText
          id="nombre"
          v-model.trim="formData.nombre"
          maxlength="30"
          @input="formatNombre($event)"
        />
      </div>
    </div>

    <template #footer>
      <Button label="Cancelar (Esc)" icon="pi pi-times" @click="cerrarModal" text />
      <Button label="Guardar (F10/Enter)" icon="pi pi-check" @click="enviarFormulario" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import type { RubroModel } from '@/models/rubroModel';
import notificationService from '@/services/notificationService';

// --- Props y Emits ---
const props = defineProps<{
  visible: boolean;
  rubro: RubroModel | null; // Puede ser null para nuevo, o un objeto para editar/clonar
}>();

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void;
  (e: 'guardar', rubro: RubroModel): void;
}>();

// --- Estado local ---
const getInitialFormData = (): RubroModel => ({
  id: null, codigo: '', nombre: '', baja_logica: false,
});
const formData = ref<RubroModel>(getInitialFormData());
const esClonado = ref(false); // Flag para detectar modo clonación

// --- Lógica ---
const esEdicion = computed(() => !!props.rubro?.id); // Verdadero solo si hay un ID (edición real)
const formTitle = computed(() => {
    if (esEdicion.value) return 'Editar Rubro';
    if (esClonado.value) return 'Clonar Rubro (Nuevo Código Requerido)'; // Título específico para clon
    return 'Nuevo Rubro';
});


watch(
  () => props.rubro,
  (nuevoRubro) => {
    // Si viene un rubro (editar o clonar), copiar sus datos. Si no (nuevo), usar valores iniciales.
    formData.value = nuevoRubro
     ? { ...nuevoRubro, codigo: nuevoRubro.codigo || '', nombre: nuevoRubro.nombre || '' } // Asegurar strings
     : { ...getInitialFormData(), codigo: '', nombre: '' }; // Garantizar strings vacíos

    // Detectar modo clonación: viene un rubro SIN ID, SIN código, PERO con nombre inicial
    esClonado.value = !!(nuevoRubro && nuevoRubro.id === null && nuevoRubro.codigo === '' && !!nuevoRubro.nombre);

    console.log(`RubroForm Watch: formData actualizado. EsEdicion=${esEdicion.value}, EsClonado=${esClonado.value}`, formData.value);
  },
  { immediate: true, deep: true } // immediate:true para cargar datos al abrir, deep:true por si acaso
);

// --- Funciones de formato ---
function formatCodigo(event: Event) {
  const input = event.target as HTMLInputElement;
  let value = input.value || '';
  value = value.toUpperCase();
  input.value = value;
  formData.value.codigo = value;
}

function capitalize(str: string | null | undefined): string {
  if (!str) return '';
  const firstChar = str.charAt(0).toUpperCase();
  const rest = str.slice(1);
  return firstChar + (rest ? rest.toLowerCase() : '');
}

function formatNombre(event: Event) {
    const input = event.target as HTMLInputElement;
    let value = input.value || '';
    value = capitalize(value);
    input.value = value;
    formData.value.nombre = value;
}
// ---

function cerrarModal() {
  emit('update:visible', false);
}

function enviarFormulario() {
  const codigoTrimmed = (formData.value.codigo || '').trim().toUpperCase();
  const nombreTrimmed = capitalize((formData.value.nombre || '').trim());

  // --- Validación F10 ---
  if (!codigoTrimmed) {
    notificationService.mostrarAdvertencia("Validación Fallida", "El campo 'Código' es requerido.");
    return;
  }
   if (codigoTrimmed.length > 3) { // Añadir validación de longitud si no la hace el InputText
    notificationService.mostrarAdvertencia("Validación Fallida", "El campo 'Código' no puede exceder los 3 caracteres.");
    return;
  }
  if (!nombreTrimmed) {
    notificationService.mostrarAdvertencia("Validación Fallida", "El campo 'Nombre' es requerido.");
    return;
  }
   if (nombreTrimmed.length > 30) { // Añadir validación de longitud
    notificationService.mostrarAdvertencia("Validación Fallida", "El campo 'Nombre' no puede exceder los 30 caracteres.");
    return;
  }
  // --- Fin Validación F10 ---

  // --- Validación Anti-Duplicados (F7) ---
  // Si estamos en modo clon (detectado por el flag 'esClonado') y el código sigue vacío
  // (aunque la validación anterior ya lo cubre, es una doble verificación semántica)
  // O si el código no ha cambiado respecto al original (en este caso, forzamos que sea distinto de vacío)
  if (esClonado.value && !codigoTrimmed) {
      notificationService.mostrarAdvertencia("Validación Clon", "Debe ingresar un nuevo Código para el rubro clonado.");
      return;
  }
  // Podríamos añadir una validación más estricta si el nombre tampoco cambió,
  // pero forzar un código nuevo diferente del original (que ahora es vacío) es suficiente.
  // --- FIN Validación Anti-Duplicados ---

  // Crear copia limpia para emitir (asegurando tipos correctos)
  const dataToEmit: RubroModel = {
    id: formData.value.id, // Será null para nuevo o clon, o tendrá valor para editar
    codigo: codigoTrimmed,
    nombre: nombreTrimmed,
    baja_logica: formData.value.baja_logica // Mantenemos el estado de baja si se está editando
  };

  emit('guardar', dataToEmit);
  // El cierre del modal lo maneja RubrosView SI el guardado fue exitoso
}

</script>

<style scoped>
.p-dialog .p-dialog-footer button {
  margin-left: 0.5rem;
}
</style>