<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    :header="props.titulo"
    :style="{ width: '25rem' }"
    @keydown.esc.prevent="cancelar"
    @keydown.f10.prevent="confirmar"
  >
    <div class="flex items-center gap-4">
      <i class="pi pi-exclamation-triangle text-4xl text-yellow-500"></i>
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

interface Props {
  visible: boolean;
  titulo?: string;
  mensaje: string;
}

const props = withDefaults(defineProps<Props>(), {
  titulo: 'Confirmar Acción'
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

// Listeners @keydown en el <Dialog> manejan F10 y Esc.
// El código manual con watch/onMounted/onUnmounted puede eliminarse si los listeners del Dialog son suficientes.
/*
const handleKeyPress = (event: KeyboardEvent) => {
 // ... código anterior ...
};
watch(() => props.visible, (newValue) => {
  // ... código anterior ...
});
onMounted(() => {
 // ... código anterior ...
});
onUnmounted(() => {
  // ... código anterior ...
});
*/

</script>

<style scoped>
p {
  margin: 0; /* Asegurar que no haya márgenes extraños */
}
.p-dialog .p-dialog-footer button {
  margin-left: 0.5rem; /* Asegurar espacio entre botones del footer */
}
</style> ```

Guarda este cambio y el servidor Vite debería compilar correctamente. 👍