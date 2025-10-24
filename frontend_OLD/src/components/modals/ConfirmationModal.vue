<!-- frontend/src/components/modals/ModalConfirmacion.vue -->
<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    :header="titulo"
    :style="{ width: '25rem' }"
  >
    <div class="flex items-center gap-4">
      <i class="pi pi-exclamation-triangle text-4xl text-yellow-500"></i>
      <p>{{ mensaje }}</p>
    </div>
    <template #footer>
      <Button
        label="Cancelar (Esc)"
        icon="pi pi-times"
        @click="cancelar"
        text
        severity="secondary"
      ></Button>
      <Button
        label="Confirmar (F10)"
        icon="pi pi-check"
        @click="confirmar"
        autofocus
        severity="danger"
      ></Button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, watch, onMounted, onUnmounted } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';

const props = defineProps({
  visible: { type: Boolean, required: true },
  titulo: { type: String, default: 'Confirmar Acción' },
  mensaje: { type: String, required: true },
});

const emit = defineEmits(['update:visible', 'confirmado', 'cancelado']);

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
});

const confirmar = () => {
  emit('confirmado');
  dialogVisible.value = false;
};

const cancelar = () => {
  emit('cancelado');
  dialogVisible.value = false;
};

const handleKeyPress = (event: KeyboardEvent) => {
  if (props.visible) {
    if (event.key === 'F10') { event.preventDefault(); confirmar(); }
    if (event.key === 'Escape') { event.preventDefault(); cancelar(); }
  }
};

watch(() => props.visible, (newValue) => {
  if (newValue) { document.addEventListener('keydown', handleKeyPress); }
  else { document.removeEventListener('keydown', handleKeyPress); }
});

onMounted(() => { if (props.visible) { document.addEventListener('keydown', handleKeyPress); } });
onUnmounted(() => { document.removeEventListener('keydown', handleKeyPress); });
</script>