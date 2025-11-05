// frontend/src/modulos/subrubros/services/subRubroService.ts
import apiClient from '@/services/apiClient';
import type { SubRubroModel, SubRubroUpdateModel } from '../models/subRubroModel';

class SubRubroApiService {
    
    async crearSubRubro(data: SubRubroModel): Promise<SubRubroModel> {
        const response = await apiClient.post<SubRubroModel>('/subrubros/', data);
        return response.data;
    }

    async listarSubRubros(estado: string = 'activos'): Promise<SubRubroModel[]> {
        const response = await apiClient.get<SubRubroModel[]>('/subrubros/lista', { params: { estado } });
        return response.data;
    }

    async actualizarSubRubro(id: string, data: SubRubroUpdateModel): Promise<SubRubroModel> {
        const response = await apiClient.put<SubRubroModel>(`/subrubros/${id}`, data);
        return response.data;
    }

    async bajaLogicaSubRubro(id: string): Promise<void> {
        await apiClient.delete(`/subrubros/${id}`);
    }

    async reactivarSubRubro(id: string): Promise<SubRubroModel> {
        const updateData: SubRubroUpdateModel = { baja_logica: false };
        return this.actualizarSubRubro(id, updateData);
    }
}
export const subRubroService = new SubRubroApiService();
