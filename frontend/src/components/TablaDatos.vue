<!-- RUTA: frontend/src/components/TablaDatos.vue (BODY CORREGIDO) -->
<template>
  <div>
    <DataTable :value="datos" :loading="cargando" tableStyle="min-width: 50rem">
      <Column v-for="col in columnas" :key="col.field" :field="col.field" :header="col.header" :sortable="col.sortable !== false">
          <!-- Slot específico para baja_logica -->
          <template v-if="col.field === 'baja_logica'" #body="slotProps">
             <!-- Usamos Tag aquí directamente para consistencia con RubrosView -->
             <Tag :value="slotProps.data[col.field] ? 'No' : 'Sí'"
                  :severity="slotProps.data[col.field] ? 'danger' : 'success'" />
          </template>
          <!-- CORREGIDO: Slot #body por defecto para TODAS las demás columnas -->
          <template v-else #body="slotProps">
              {{ slotProps.data[col.field] }}
          </template>
      </Column>
      <Column header="Acciones" style="width: 10rem">
        <template #body="slotProps">
          <Button icon="pi pi-pencil" severity="info" rounded text @click="$emit('editar-item', slotProps.data)" class="mr-2"/>
          <Button icon="pi pi-trash" severity="danger" rounded text @click="$emit('eliminar-item', slotProps.data)" />
        </template>
      </Column>
      <template #empty> {{ textoVacio || 'No hay datos disponibles.' }} </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
// Añadido Tag si no es global
import Tag from 'primevue/tag';
// PrimeVue components (assumed global)
interface Columna { field: string; header: string; sortable?: boolean; }
defineProps<{ datos: any[]; columnas: Columna[]; cargando?: boolean; textoVacio?: string; }>();
defineEmits(['editar-item', 'eliminar-item']);
</script>