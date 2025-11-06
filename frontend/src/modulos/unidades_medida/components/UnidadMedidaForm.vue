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
                
                @input="entidadLocal.codigo_unidad = entidadLocal.codigo_unidad.toUpperCase()"
                @keydown.enter.prevent="focusNombre"
            />
            <small v-if="submitted && !entidadLocal.codigo_unidad" class="p-error">El código es requerido.</small>
        </div>

        <div class="field">
            <label for="nombre">Nombre</label>
            <InputText
                id="nombre"
                ref="nombreInput" v-model.trim="entidadLocal.nombre"
                required
                :maxlength="30"
                :invalid="submitted && !entidadLocal.nombre"
                
                @keydown.enter.prevent="$emit('guardar')"
            />
            <small v-if="submitted && !entidadLocal.nombre" class="p-error">El nombre es requerido.</small>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import type { UnidadMedidaModel } from '../models/unidadMedidaModel';
import InputText from 'primevue/inputtext';

// --- Props y Emits (Patrón DEOU) ---
const props = defineProps<{
    modelValue: UnidadMedidaModel;
    submitted: boolean;
}>();

const emits = defineEmits<{
    (e: 'update:modelValue', value: UnidadMedidaModel): void;
    (e: 'guardar'): void; // Emit para el guardado (Fallo 2)
}>();

// --- State ---
const entidadLocal = ref<UnidadMedidaModel>({ ...props.modelValue });

// --- REPARACIÓN (Fallo 2) ---
const nombreInput = ref<InstanceType<typeof InputText> | null>(null);
const focusNombre = () => {
    nombreInput.value?.$el.focus();
};
// ---

// --- Watchers ---
watch(() => props.modelValue, (newValue) => {
    // Sincronizar solo si la referencia ha cambiado
    if (newValue.id !== entidadLocal.value.id) {
        entidadLocal.value = { ...newValue };
    }
}, { deep: false });

watch(entidadLocal, (newValue) => {
    // El @input maneja el uppercase.
    // El watch solo emite el cambio al padre.
    emits('update:modelValue', newValue);
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