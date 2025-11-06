// --- INICIO BLOQUE IVA-F-02 ---
// frontend/src/modulos/condiciones_iva/services/ivaService.ts
import apiClient from '@/services/apiClient'; 
import type { IvaModel } from '../models/ivaModel';
import type { AxiosResponse } from 'axios'; // Importar para manejo de 409

const API_URL = '/condiciones-iva'; 

export const ivaService = {
    
    // GET (Filtro VIL)
    getIvas(estado: 'activos' | 'inactivos' | 'todos' = 'activos'): Promise<IvaModel[]> {
        // Añadido '/' para evitar redirect 307
        return apiClient.get(`${API_URL}/`, { params: { estado } })
            .then(response => response.data);
    },

    // POST
    // Modificado para devolver AxiosResponse (Doctrina ABR V12)
    createIva(data: IvaModel): Promise<AxiosResponse<IvaModel>> {
        return apiClient.post(`${API_URL}/`, data);
    },

    // PATCH (Doctrina data.id!)
    updateIva(id: string, data: Partial<IvaModel>): Promise<IvaModel> {
        return apiClient.patch(`${API_URL}/${id}`, data)
            .then(response => response.data);
    },

    // DELETE (Baja Lógica)
    deleteIva(id: string): Promise<void> {
        return apiClient.delete(`${API_URL}/${id}`)
            .then(response => response.data);
    }
};
// --- FIN BLOQUE IVA-F-02 ---