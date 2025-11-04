// frontend/src/modulos/subrubros/services/subRubroService.ts
import apiClient from '@/services/apiClient';
import type { SubRubroModel, SubRubroUpdateModel } from '../models/subRubroModel';

class SubRubroApiService {
    
    async crearSubRubro(data: SubRubroModel): Promise<SubRubroModel> {
        // Endpoint corregido (POST /subrubros/) - Estaba correcto
        const response = await apiClient.post<SubRubroModel>('/subrubros/', data);
        return response.data;
    }

    async listarSubRubros(estado: string = 'activos'): Promise<SubRubroModel[]> {
        // Adaptado para Filtro de Tres Vías
        // *** CORRECCIÓN: Endpoint alineado con el router del backend ***
        const response = await apiClient.get<SubRubroModel[]>('/subrubros/lista', { params: { estado } });
        return response.data;
    }

    async actualizarSubRubro(id: string, data: SubRubroUpdateModel): Promise<SubRubroModel> {
        // *** CORRECCIÓN: Método alineado con el router del backend (PATCH -> PUT) ***
        const response = await apiClient.put<SubRubroModel>(/subrubros/, data);
        return response.data;
    }

    async bajaLogicaSubRubro(id: string): Promise<void> {
        // Endpoint corregido (DELETE /subrubros/{id}) - Estaba correcto
        await apiClient.delete(/subrubros/);
    }

    // --- FUNCIÓN ABR V12 ---
    async reactivarSubRubro(id: string): Promise<SubRubroModel> {
        const updateData: SubRubroUpdateModel = { baja_logica: false };
        return this.actualizarSubRubro(id, updateData);
    }
}

export const subRubroService = new SubRubroApiService();
