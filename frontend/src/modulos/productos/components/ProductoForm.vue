<!-- RUTA: frontend/src/modulos/productos/components/ProductoForm.vue -->
<template>
  <Dialog v-model:visible="dialogVisible" :header="tituloFormulario" modal :style="{ width: '50vw' }">
    <div class="p-fluid grid">
      <div class="field col-12 md:col-6">
        <label for="sku">SKU</label>
        <InputText id="sku" v-model="formState.sku" :maxlength="8" />
      </div>
      <div class="field col-12 md:col-6">
        <label for="nombre">Nombre</label>
        <InputText id="nombre" v-model="formState.nombre" :maxlength="30" />
      </div>
      <div class="field col-12">
        <label for="observaciones">Observaciones</label>
        <Textarea id="observaciones" v-model="formState.observaciones" :maxlength="60" autoResize rows="3" />
      </div>
      <!-- NOTA: El código original de CC8 no incluía los campos de precio y stock en el formulario, 
           así que no se importó InputNumber. Lo mantenemos así por ahora. -->
    </div>

    <template #footer>
      <Button label="Cancelar" icon="pi pi-times" @click="cerrar" text />
      <Button label="Guardar" icon="pi pi-check" @click="guardar" autofocus />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import type { ProductoModel } from '../models/productoModel';

// --- LÍNEAS ELIMINADAS (AHORA GLOBALES) ---
// import Dialog from 'primevue/dialog';
// import InputText from 'primevue/inputtext';
// import Textarea from 'primevue/textarea';
// import Button from 'primevue/button';
// ---

const props = defineProps<{
  visible: boolean;
  producto: ProductoModel | null;
}>();

const emit = defineEmits(['update:visible', 'guardar']);

const formState = ref<Partial<ProductoModel>>({});

const tituloFormulario = computed(() => props.producto ? 'Editar Producto' : 'Nuevo Producto');

// Sincroniza el prop con el estado local del formulario
watch(() => props.producto, (newVal) => {
  if (newVal) {
    formState.value = { ...newVal };
  } else {
    formState.value = { baja_logica: false, es_kit: false }; // Defaults
  }
}, { immediate: true }); // Asegura que se ejecute al inicio

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
});

const cerrar = () => {
  dialogVisible.value = false;
};

const guardar = () => {
  // Aquí iría la lógica de validación
  emit('guardar', formState.value);
  cerrar();
};
</script>