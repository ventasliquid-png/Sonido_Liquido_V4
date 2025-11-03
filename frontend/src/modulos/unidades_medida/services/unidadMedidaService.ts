// frontend/src/modulos/unidades_medida/services/unidadMedidaService.ts
import apiClient from '@/services/apiClient'; // Importa el apiClient canónico
import type { UnidadMedidaModel } from '../models/unidadMedidaModel';

const API_URL = '/unidades-medida'; // Endpoint del router (Req 4)

export const unidadMedidaService = {
    
    // GET (Filtro VIL)
    getUnidades(estado: 'activos' | 'inactivos' | 'todos' = 'activos'): Promise<UnidadMedidaModel[]> {
        return apiClient.get(API_URL, { params: { estado } })
            .then(response => response.data);
    },

    // POST
    createUnidad(data: UnidadMedidaModel): Promise<UnidadMedidaModel> {
        return apiClient.post(API_URL, data)
            .then(response => response.data);
    },

    // PATCH (Doctrina DEOU - Actualización Parcial)
    updateUnidad(id: string, data: Partial<UnidadMedidaModel>): Promise<UnidadMedidaModel> {
        return apiClient.patch(`${API_URL}/${id}`, data)
            .then(response => response.data);
    },

    // DELETE (Baja Lógica - Doctrina VIL)
    deleteUnidad(id: string): Promise<void> {
        return apiClient.delete(`${API_URL}/${id}`)
            .then(response => response.data);
    }
};