<!-- RUTA: frontend/src/components/TablaDatos.vue -->
<template>
  <div>
    <DataTable :value="datos" :loading="cargando" tableStyle="min-width: 50rem">
      <Column v-for="col in columnas" :key="col.field" :field="col.field" :header="col.header" :sortable="col.sortable !== false">
           <!-- Formateo básico para booleanos -->
           <template v-if="col.field === 'baja_logica'" #body="slotProps">
               {{ slotProps.data[col.field] ? 'No' : 'Sí' }}
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
// --- LÍNEAS ELIMINADAS (AHORA GLOBALES) ---
// import DataTable from 'primevue/datatable';
// import Column from 'primevue/column';
// import Button from 'primevue/button';
// ---

// Definimos los tipos para las props
interface Columna {
  field: string;
  header: string;
  sortable?: boolean;
}

defineProps<{
  datos: any[];
  columnas: Columna[];
  cargando?: boolean;
  textoVacio?: string;
}>();

// Definimos los eventos que puede emitir
defineEmits(['editar-item', 'eliminar-item']);
</script>