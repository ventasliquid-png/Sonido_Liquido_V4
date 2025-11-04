<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    :header="props.titulo"
    :style="{ width: '30rem' }"
    @update:visible="cerrar"
  >
    <div class="confirmation-content">
      <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
      <span v-html="props.message"></span>
    </div>

    <template #footer>
      <Button
        label="No"
        icon="pi pi-times"
        severity="secondary"
        @click="cancelar"
        :disabled="props.loading"
      />
      <Button
        label="Sí"
        icon="pi pi-check"
        autofocus
        @click="confirmar"
        :loading="props.loading"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';

interface Props {
  visible: boolean;
  titulo: string;
  message: string;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits(['update:visible', 'confirmado', 'cancelado']);

const dialogVisible = ref(props.visible);

watch(
  () => props.visible,
  (newVal) => {
    dialogVisible.value = newVal;
  },
);

function cerrar(value: boolean) {
  emit('update:visible', value);
}

function confirmar() {
  emit('confirmado');
  cerrar(false);
}

function cancelar() {
  emit('cancelado');
  cerrar(false);
}
</script>

<style scoped>
.confirmation-content {
  display: flex;
  align-items: center;
}
</style>
