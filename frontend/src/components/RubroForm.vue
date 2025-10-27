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
          v-model.trim="formData.codigo" maxlength="3"
          :disabled="esEdicion"
          aria-describedby="codigo-help"
          @input="formatCodigo($event)"
        />
        <small id="codigo-help">Máx 3 caracteres. No se puede cambiar.</small>
      </div>
      <div class="field col-12 md:col-6">
        <label for="nombre">Nombre</label>
        <InputText
          id="nombre"
          v-model.trim="formData.nombre" maxlength="30"
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
import notificationService from '@/services/notificationService'; // Importar servicio

// --- Props y Emits ---
const props = defineProps<{
  visible: boolean;
  rubro: RubroModel | null;
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

// --- Lógica ---
const esEdicion = computed(() => !!props.rubro?.id);
const formTitle = computed(() => esEdicion.value ? 'Editar Rubro' : 'Nuevo Rubro');

watch(
  () => props.rubro,
  (nuevoRubro) => {
    // Asegurarse de que los valores sean siempre strings al inicializar/resetear
    formData.value = nuevoRubro
     ? { ...nuevoRubro, codigo: nuevoRubro.codigo || '', nombre: nuevoRubro.nombre || '' }
     : { ...getInitialFormData(), codigo: '', nombre: '' }; // Garantizar strings vacíos
    console.log("RubroForm Watch (Corregido): formData actualizado", formData.value);
  },
  { immediate: true, deep: true }
);

// --- Funciones de formato ---
function formatCodigo(event: Event) {
  const input = event.target as HTMLInputElement;
  let value = input.value || ''; // Asegurar string
  value = value.toUpperCase();
  input.value = value; // Actualizar el input visualmente
  formData.value.codigo = value; // Actualizar el ref
}

// --- FUNCIÓN CORREGIDA ---
function capitalize(str: string | null | undefined): string {
  if (!str) return ''; // Manejo seguro de null/undefined
  // Asegurar que str.slice(1) existe y es string antes de toLowerCase()
  const firstChar = str.charAt(0).toUpperCase();
  const rest = str.slice(1);
  return firstChar + (rest ? rest.toLowerCase() : ''); // Comprobar si 'rest' existe
}
// --- FIN CORRECCIÓN ---

function formatNombre(event: Event) {
    const input = event.target as HTMLInputElement;
    let value = input.value || ''; // Asegurar string
    value = capitalize(value);
    input.value = value; // Actualizar el input visualmente
    formData.value.nombre = value; // Actualizar el ref
}
// ---

function cerrarModal() {
  emit('update:visible', false);
}

function enviarFormulario() {
  // Usamos trim directamente en v-model, pero re-aseguramos aquí
  const codigoTrimmed = (formData.value.codigo || '').trim().toUpperCase();
  const nombreTrimmed = capitalize((formData.value.nombre || '').trim());

  // Validar ANTES de emitir
  if (!codigoTrimmed || !nombreTrimmed) {
    // Usar notificationService en lugar de alert
    notificationService.showError("Error de Validación", "Código y Nombre son requeridos.");
    // alert("Código y Nombre son requeridos"); // Reemplazado
    return;
  }

  // Crear copia limpia para emitir
  const dataToEmit: RubroModel = {
    ...formData.value,
    codigo: codigoTrimmed,
    nombre: nombreTrimmed
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