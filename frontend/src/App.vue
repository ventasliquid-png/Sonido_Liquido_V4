<template>
  <Toast />
  <div class="card">
    <h1>Integración de Activos de CC8</h1>
    <div class="flex gap-2">
      <Button @click="openModal" label="Abrir Modal de Confirmación" />
      <Button @click="testSuccessNotification" label="Notificación de Éxito" severity="danger" />
    </div>
  </div>
  <ConfirmationModal
    v-model:visible="isModalVisible"
    mensaje="¿Estás seguro de que deseas eliminar este registro? Esta acción es irreversible."
    @confirmado="onConfirmed"
    @cancelado="onCancelled"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Button from 'primevue/button';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';
import ConfirmationModal from './components/modals/ConfirmationModal.vue';
import notificationService from './services/notificationService.ts';

const toast = useToast();
onMounted(() => { notificationService.inicializar(toast); });
const testSuccessNotification = () => { notificationService.mostrarExito('La operación se completó correctamente.'); };
const isModalVisible = ref(false);
const openModal = () => { isModalVisible.value = true; };
const onConfirmed = () => { notificationService.mostrarAdvertencia('El registro ha sido eliminado.', 'Acción Realizada'); };
const onCancelled = () => { notificationService.mostrarError('La operación fue cancelada.', 'Cancelado'); };
</script>

<style>
body { font-family: sans-serif; background-color: #f8f9fa; }
.card { max-width: 600px; margin: 5rem auto; padding: 2rem; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 1.5rem; }
</style>