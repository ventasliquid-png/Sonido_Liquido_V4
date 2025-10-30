<template>
  <div>
    <DataTable :value="datos" :loading="cargando" tableStyle="min-width: 50rem">
      <Column v-for="col in columnas" :key="col.field" :field="col.field" :header="col.header" :sortable="col.sortable !== false">
        <template v-if="col.field === 'baja_logica'" #body="slotProps">
            <Tag :value="slotProps.data[col.field] ? 'No' : 'Sí'"
                :severity="slotProps.data[col.field] ? 'danger' : 'success'" />
        </template>
        <template v-else #body="slotProps">
            {{ slotProps.data[col.field] }}
        </template>
      </Column>
      
      <Column header="Acciones" style="width: 10rem">
        <template #body="slotProps">
          <template v-if="!slotProps.data.baja_logica">
            <Button icon="pi pi-pencil" severity="info" rounded @click="$emit('editar-item', slotProps.data)" class="mr-2"/>
            <Button icon="pi pi-trash" severity="danger" rounded @click="$emit('eliminar-item', slotProps.data)" />
          </template>
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