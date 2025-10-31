<template>
  <Dialog 
    v-model:visible="dialogVisible" 
    :header="tituloFormulario" 
    modal 
    :style="{ width: '30vw' }"
    @keydown.f10.prevent="intentarGuardar"
    @keydown.esc.prevent="cerrar"
  >
    <div class="p-fluid grid">
      
      <div class="field col-12">
        <label for="codigo_subrubro">Código</label>
        <InputText 
          id="codigo_subrubro" 
          v-model="formData.codigo_subrubro" 
          :maxlength="10" 
          :disabled="!!formData.id"
          autofocus 
          @input="formData.codigo_subrubro = (formData.codigo_subrubro || '').toUpperCase()"
        />
        <small v-if="!formData.id && !props.modoClon">El código debe ser único (máx. 10 caracteres).</small>
        <small v-if="props.modoClon">Ingrese el NUEVO código para el clon (máx. 10 caracteres).</small>
        <small v-if="!!formData.id">El código no se puede modificar.</small>
      </div>

      <div class="field col-12">
        <label for="nombre">Nombre</label>
        <InputText id="nombre" v-model="formData.nombre" :maxlength="30" />
      </div>

      <input type="hidden" :value="datosOriginalesParaClon" />

    </div>
    <template #footer>
      <Button label="Cancelar (Esc)" icon="pi pi-times" @click="cerrar" text />
      <Button :label="labelBotonGuardar" icon="pi pi-check" @click="intentarGuardar" autofocus />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import type { SubRubroModel } from '../models/subRubroModel';
import notificationService from '@/services/notificationService';

// --- Props y Emits ---
const props = defineProps<{
  visible: boolean;
  subrubro: SubRubroModel | null; // Adaptado
  modoClon: boolean;
}>();

const emit = defineEmits(['update:visible', 'guardar']);

// --- Estado Interno ---
const formData = ref<Partial<SubRubroModel>>({}); // Adaptado
// Usado para la validación Anti-Clon F7
const datosOriginalesParaClon = ref<string>(''); 

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
});

// --- Títulos y Labels Dinámicos ---
const tituloFormulario = computed(() => {
  if (props.modoClon) return 'Clonar Sub-Rubro';
  return props.subrubro && props.subrubro.id ? 'Editar Sub-Rubro' : 'Nuevo Sub-Rubro';
});
const labelBotonGuardar = computed(() => {
  return props.modoClon ? 'Guardar Clon (F10)' : 'Guardar (F10)';
});

// --- Sincronización (Watch) ---
watch(() => props.subrubro, (newVal) => { // Adaptado
  if (newVal) {
    formData.value = { ...newVal };
    // Si es modo clon, guardar el 'nombre' original para la validación F7
    if (props.modoClon) {
      datosOriginalesParaClon.value = newVal.nombre || '';
    }
  } else {
    // Es un Alta Nueva (F4)
    formData.value = { codigo_subrubro: '', nombre: '', baja_logica: false }; // Adaptado
    datosOriginalesParaClon.value = '';
  }
}, { immediate: true });

// --- Lógica de Acciones (F10 / Esc) ---
const cerrar = () => {
  dialogVisible.value = false;
};

// --- DOCTRINA F10 (Validación) y F7 (Anti-Duplicados) ---
const intentarGuardar = () => {
  // 1. Validación de Campos
  const codigo_subrubro = (formData.value.codigo_subrubro || '').trim(); // Adaptado
  const nombre = (formData.value.nombre || '').trim();

  if (!codigo_subrubro || !nombre) { // Adaptado
    notificationService.mostrarError("El Código y el Nombre son obligatorios.");
    return;
  }
  
  // [OMISIÓN DOCTRINAL: Se omite la validación de longitud fija (length !== 3)]
  // La validación de max_length=10 la maneja el InputText y el Modelo Pydantic.

  // 2. Validación Anti-Clon F7
  if (props.modoClon) {
    if (nombre === datosOriginalesParaClon.value) {
      notificationService.mostrarAdvertencia("No se puede guardar un clon exacto. Modifique el nombre.");
      return;
    }
  }

  // 3. Emisión (Si pasa todas las validaciones)
  emit('guardar', { ...formData.value, codigo_subrubro, nombre }); // Adaptado
};
</script>