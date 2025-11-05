<template>
  <div>
    <DataTable :value="datos" :loading="cargando" tableStyle="min-width: 50rem" :rowClass="rowClass" :rowStyle="rowStyle">
      <Column v-for="col in columnas" :key="col.field" :field="col.field" :header="col.header" :sortable="col.sortable !== false">
        
        <template v-if="$slots[`body-${col.field}`]" #[`body-${col.field}`]="slotProps">
            <slot :name="`body-${col.field}`" :data="slotProps.data"></slot>
        </template>
        
        <template v-else-if="col.field === 'baja_logica'" #body="slotProps">
            <Tag :value="slotProps.data[col.field] ? 'Inactivo' : 'Activo'"
                 :severity="slotProps.data[col.field] ? 'danger' : 'success'" />
        </template>

        <template v-else #body="slotProps">
            {{ slotProps.data[col.field] }}
        </template>
      </Column>

      <Column header="Acciones" style="width: 10rem">
        <template #body="slotProps">
          
          <div class="flex-container" style="display: flex; justify-content: flex-start; gap: 0.5rem;">
            
            <slot name="actions-prepend" :data="slotProps.data"></slot>
            
            <slot name="actions" :data="slotProps.data">
                
                <Button v-if="!slotProps.data.baja_logica" 
                        icon="pi pi-pencil" 
                        severity="info" 
                        rounded 
                        @click="$emit('editar-item', slotProps.data)" 
                        v-tooltip.bottom="'Editar'"/>
                
                <Button v-if="!slotProps.data.baja_logica" 
                        icon="pi pi-trash" 
                        severity="danger" 
                        rounded 
                        @click="$emit('eliminar-item', slotProps.data)"
                        v-tooltip.bottom="'Dar de Baja'" />
                
                <Button v-if="showReactivateButton && slotProps.data.baja_logica" 
                        icon="pi pi-check" 
                        severity="warning" 
                        rounded 
                        @click="$emit('reactivar-item', slotProps.data)"
                        v-tooltip.bottom="'Reactivar'" />

            </slot>

          </div>
        </template>
      </Column>
      <template #empty> {{ textoVacio || 'No hay datos disponibles.' }} </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import Tag from 'primevue/tag';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Tooltip from 'primevue/tooltip'; // Añadido para v-tooltip

interface Columna { field: string; header: string; sortable?: boolean; }

defineProps<{ 
  datos: any[]; 
  columnas: Columna[]; 
  cargando?: boolean; 
  textoVacio?: string; 
  rowClass?: (data: any) => string | object; // Añadido (Canon Rubros)
  rowStyle?: (data: any) => string | object; // Añadido (Canon SubRubros)
  showReactivateButton?: boolean; // Añadido (Fallo 2)
  showDeleteButton?: boolean; // Añadido para compatibilidad (aunque no se usa si #actions está sobreescrito)
}>();

defineEmits(['editar-item', 'eliminar-item', 'reactivar-item']); // Añadido (Fallo 2)
</script>
