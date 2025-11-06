// INICIO REPARACIÓN MANUAL G-U-11 (R2) (UTF-8 y ABR V12)
// frontend/src/modulos/unidades_medida/services/unidadMedidaService.ts
import apiClient from '@/services/apiClient'; // Importa el apiClient canónico
import type { UnidadMedidaModel } from '../models/unidadMedidaModel';
import type { AxiosResponse } from 'axios'; // <-- REPARACIÓN: Importar AxiosResponse

const API_URL = '/unidades-medida'; // Endpoint del router (Req 4)

export const unidadMedidaService = {

    // GET (Filtro VIL)
    getUnidades(estado: 'activos' | 'inactivos' | 'todos' = 'activos'): Promise<UnidadMedidaModel[]> {
        // REPARACIÓN: Se añade / al final para evitar redirect 307
        return apiClient.get(`${API_URL}/`, { params: { estado } })
            .then(response => response.data);
    },

    // POST
    // REPARACIÓN: Debe devolver la Promise<AxiosResponse> completa para el manejo de 409
    createUnidad(data: UnidadMedidaModel): Promise<AxiosResponse<UnidadMedidaModel>> {
        return apiClient.post(`${API_URL}/`, data);
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
// FIN REPARACIÓN MANUAL G-U-11 (R2)