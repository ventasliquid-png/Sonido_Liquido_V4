<template>
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
        autofocus 
        @keydown.enter.prevent="focusNombre" />
      <small id="codigo-help">Máx 3 caracteres. No se puede cambiar si edita.</small>
    </div>
    <div class="field col-12 md:col-6">
      <label for="nombre">Nombre</label>
      <InputText
        id="nombre"
        v-model.trim="formData.nombre"
        maxlength="30"
        @input="formatNombre($event)"
        ref="nombreInput" @keydown.enter.prevent="emit('guardar')" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'; 
import InputText from 'primevue/inputtext'; // ⬅️ CAMBIO v10.3: Importar para el Ref
import type { RubroModel } from '../models/rubroModel';
import notificationService from '@/services/notificationService';

// --- Props y Emits ---
const props = defineProps<{
  modelValue: RubroModel; 
  esEdicion: boolean;
  esClonado: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: RubroModel): void;
  (e: 'guardar'): void; // ⬅️ CAMBIO v10.3: Definir el emit 'guardar'
}>();

// --- Estado local ---
const formData = ref<RubroModel>({ ...props.modelValue });
const nombreInput = ref<InstanceType<typeof InputText> | null>(null); // ⬅️ CAMBIO v10.3: Ref

// --- Lógica ---
watch(
  () => props.modelValue,
  (nuevoRubro) => {
    formData.value = { ...nuevoRubro };
    console.log(`RubroForm Watch: formData actualizado.`, formData.value);
  },
  { immediate: true, deep: true }
);

// (El watcher 2 'formData' se mantiene eliminado, como en v10.2)

// --- Funciones de formato y Foco ---

// ⬅️ CAMBIO v10.3: Función para saltar foco
function focusNombre() {
  nombreInput.value?.$el.focus();
}

function formatCodigo(event: Event) {
  const input = event.target as HTMLInputElement;
  let value = input.value || '';
  value = value.toUpperCase();
  
  input.value = value; 
  formData.value.codigo = value;
  
  emit('update:modelValue', formData.value);
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
    
    emit('update:modelValue', formData.value);
}
// ---

</script>

<style scoped>
/* (Estilo v10... sin cambios) */
.p-inputtext:focus {
    outline: 0 none;
    outline-offset: 0;
    box-shadow: 0 0 0 0.2rem var(--primary-shadow-color, rgba(0, 123, 255, 0.25)); 
    border-color: var(--primary-color, #007bff);
}
</style>