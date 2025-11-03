<template>
    <div class="form-container">
        <div class="field">
            <label for="codigo_unidad">Código</label>
            <InputText 
                id="codigo_unidad" 
                v-model.trim="entidadLocal.codigo_unidad" 
                required 
                autofocus 
                :disabled="!!entidadLocal.id"
                :maxlength="4"
                :invalid="submitted && !entidadLocal.codigo_unidad"
            />
            <small v-if="submitted && !entidadLocal.codigo_unidad" class="p-error">El código es requerido.</small>
        </div>

        <div class="field">
            <label for="nombre">Nombre</label>
            <InputText 
                id="nombre" 
                v-model.trim="entidadLocal.nombre" 
                required 
                :maxlength="30"
                :invalid="submitted && !entidadLocal.nombre"
            />
            <small v-if="submitted && !entidadLocal.nombre" class="p-error">El nombre es requerido.</small>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits, onMounted } from 'vue';
import type { UnidadMedidaModel } from '../models/unidadMedidaModel';
import InputText from 'primevue/inputtext';

// --- Props y Emits (Patrón DEOU) ---
const props = defineProps<{
    modelValue: UnidadMedidaModel;
    submitted: boolean;
}>();

const emits = defineEmits<{
    (e: 'update:modelValue', value: UnidadMedidaModel): void;
}>();

// --- State ---
// Usamos una copia local para evitar mutaciones directas.
const entidadLocal = ref<UnidadMedidaModel>({ ...props.modelValue });

// --- Watchers ---
watch(() => props.modelValue, (newValue) => {
    // Sincronizar solo si la referencia ha cambiado (optimización)
    if (newValue.id !== entidadLocal.value.id) {
        entidadLocal.value = { ...newValue };
    }
}, { deep: false }); 

watch(entidadLocal, (newValue) => {
    // Asegurar que el código siempre esté en mayúsculas y notificar al padre
    const updatedValue = { ...newValue, codigo_unidad: newValue.codigo_unidad.toUpperCase() };
    emits('update:modelValue', updatedValue);
}, { deep: true });

onMounted(() => {
    // Inicialización al montar
    entidadLocal.value = { ...props.modelValue };
});
</script>

<style scoped>
/* Estilos canónicos (Patrón Rubros) */
.form-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
</style>