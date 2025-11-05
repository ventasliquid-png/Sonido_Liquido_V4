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
          @keydown.enter.prevent="focusNombre" 
        />
        <small v-if="!formData.id && !props.modoClon">El código debe ser único (máx. 10 caracteres).</small>
        <small v-if="props.modoClon">Ingrese el NUEVO código para el clon (máx. 10 caracteres).</small>
        <small v-if="!!formData.id">El código no se puede modificar.</small>
      </div>

      <div class="field col-12">
        <label for="nombre">Nombre</label>
        <InputText 
            id="nombre" 
            ref="nombreInput" 
            v-model="formData.nombre" 
            :maxlength="30" 
            @keydown.enter.prevent="intentarGuardar"
        />
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
import InputText from 'primevue/inputtext'; // Importar InputText
import Button from 'primevue/button'; // Importar Button
import Dialog from 'primevue/dialog'; // Importar Dialog

// --- Props y Emits ---
const props = defineProps<{
  visible: boolean;
  subrubro: SubRubroModel | null; // Adaptado
  modoClon: boolean;
}>();

const emit = defineEmits(['update:visible', 'guardar']);

// --- Estado Interno ---
const formData = ref<Partial<SubRubroModel>>({}); // Adaptado
const datosOriginalesParaClon = ref<string>('');

// --- INICIO CORRECCIÓN DIRECTIVA 82 (Fallo 5) ---
const nombreInput = ref<InstanceType<typeof InputText> | null>(null);
// --- FIN CORRECCIÓN DIRECTIVA 82 (Fallo 5) ---

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
    if (props.modoClon) {
      datosOriginalesParaClon.value = newVal.nombre || '';
    }
  } else {
    formData.value = { codigo_subrubro: '', nombre: '', baja_logica: false }; // Adaptado
    datosOriginalesParaClon.value = '';
  }
}, { immediate: true });

// --- Lógica de Acciones (F10 / Esc) ---
const cerrar = () => {
  dialogVisible.value = false;
};

// --- INICIO CORRECCIÓN DIRECTIVA 82 (Fallo 5) ---
const focusNombre = () => {
    // Usamos $el (DOM element) para hacer focus
    nombreInput.value?.$el.focus();
};
// --- FIN CORRECCIÓN DIRECTIVA 82 (Fallo 5) ---

// --- DOCTRINA F10 (Validación) y F7 (Anti-Duplicados) ---
const intentarGuardar = () => {
  const codigo_subrubro = (formData.value.codigo_subrubro || '').trim(); // Adaptado
  const nombre = (formData.value.nombre || '').trim();

  if (!codigo_subrubro || !nombre) { // Adaptado
    notificationService.showError("El Código y el Nombre son obligatorios.");
    return;
  }

  if (props.modoClon) {
    if (nombre === datosOriginalesParaClon.value) {
      notificationService.showWarn("No se puede guardar un clon exacto. Modifique el nombre.");
      return;
    }
  }

  emit('guardar', { ...formData.value, codigo_subrubro, nombre }); // Adaptado
};
</script>
