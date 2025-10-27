<!-- RUTA: frontend/src/components/modals/ConfirmationModal.vue (SCRIPT CORREGIDO) -->
<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    :header="props.titulo" <!-- Usar props.titulo -->
    :style="{ width: '25rem' }"
  >
    <div class="flex items-center gap-4">
      <i class="pi pi-exclamation-triangle text-4xl text-yellow-500"></i>
      <!-- Usar props.mensaje -->
      <p>{{ props.mensaje }}</p>
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
// Los componentes PrimeVue se asumen globales
// import Dialog from 'primevue/dialog';
// import Button from 'primevue/button';

// --- CORREGIDO: Sintaxis estándar de defineProps con TypeScript ---
interface Props {
  visible: boolean;
  titulo?: string; // Hacer opcional con valor por defecto
  mensaje: string; // Mantener requerido
}

// Define props con valores por defecto donde aplique
const props = withDefaults(defineProps<Props>(), {
  titulo: 'Confirmar Acción' // Valor por defecto para titulo
});
// --- FIN CORRECCIÓN ---

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

// Lógica de teclas (sin cambios)
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

<style scoped>
/* Añadir algún estilo si es necesario, por ejemplo, al párrafo del mensaje */
p {
  margin: 0; /* Asegurar que no haya márgenes extraños */
}
</style>