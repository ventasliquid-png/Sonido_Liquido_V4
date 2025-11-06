<template>
    <div class="form-container">
        <div class="field">
            <label for="codigo_iva">Código</label>
            <InputText 
                id="codigo_iva" 
                ref="codigoInput" v-model.trim="entidadLocal.codigo_iva" 
                required 
                :disabled="!!entidadLocal.id"
                :maxlength="4"
                :invalid="submitted && !entidadLocal.codigo_iva"
                
                @input="onCodigoInput"
                @keydown.enter.prevent="focusNombre"
            />
            <small v-if="submitted && !entidadLocal.codigo_iva" class="p-error">El código es requerido.</small>
        </div>

        <div class="field">
            <label for="nombre">Nombre</label>
            <InputText 
                id="nombre" 
                ref="nombreInput" 
                v-model.trim="entidadLocal.nombre" 
                required 
                :maxlength="30"
                :invalid="submitted && !entidadLocal.nombre"
                
                @input="emits('update:modelValue', entidadLocal)"
                @keydown.enter.prevent="focusAlicuota"
            />
            <small v-if="submitted && !entidadLocal.nombre" class="p-error">El nombre es requerido.</small>
        </div>

        <div class="field">
            <label for="alicuota">Alícuota (%)</label>
            <InputNumber
                id="alicuota"
                ref="alicuotaInput" 
                v-model="entidadLocal.alicuota"
                mode="decimal"
                :minFractionDigits="2"
                :maxFractionDigits="2"
                :invalid="submitted && entidadLocal.alicuota === null"
                required
                
                @input="emits('update:modelValue', entidadLocal)"
                @keydown.enter.prevent="$emit('guardar')"
            />
            <small v-if="submitted && entidadLocal.alicuota === null" class="p-error">La alícuota es requerida.</small>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'; 
import type { IvaModel } from '../models/ivaModel';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber'; 
import { Decimal } from 'decimal.js'; 

// --- Props y Emits (Patrón DEOU) ---
const props = defineProps<{
    modelValue: IvaModel;
    submitted: boolean;
}>();

const emits = defineEmits<{
    (e: 'update:modelValue', value: IvaModel): void;
    (e: 'guardar'): void; 
}>();

// --- State ---
const entidadLocal = ref<IvaModel>(parseModelValue(props.modelValue));

// --- Refs para Foco ---
const codigoInput = ref<InstanceType<typeof InputText> | null>(null); 
const nombreInput = ref<InstanceType<typeof InputText> | null>(null);
const alicuotaInput = ref<InstanceType<typeof InputNumber> | null>(null);

function focusNombre() {
    nombreInput.value?.$el.focus();
}
function focusAlicuota() {
    (alicuotaInput.value?.$input as HTMLInputElement)?.focus();
}
function focusCodigo() {
    codigoInput.value?.$el.focus();
}

function onCodigoInput(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    entidadLocal.value.codigo_iva = value.toUpperCase();
    emits('update:modelValue', entidadLocal.value);
}

// --- Funciones de Utilidad ---
function parseModelValue(model: IvaModel): IvaModel {
    const alicuotaNum = new Decimal(model.alicuota || 0).toNumber();
    return { 
        ...model, 
        alicuota: alicuotaNum
    };
}

// --- Watchers ---
watch(() => props.modelValue, (newValue) => {
    // Sincroniza datos, pero NO maneja el foco
    entidadLocal.value = parseModelValue(newValue);
}, { deep: true }); 

onMounted(() => {
    entidadLocal.value = parseModelValue(props.modelValue);
});

// --- REPARACIÓN G-U-34: Exponer las funciones de foco al Padre ---
defineExpose({
    focusCodigo,
    focusNombre
});
</script>

<style scoped>
/* Estilos canónicos */
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