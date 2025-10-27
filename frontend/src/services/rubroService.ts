import apiClient from './apiClient'; // Asume apiClient existente
import type { RubroModel } from '@/models/rubroModel';
import type { AxiosResponse } from 'axios';

/**
 * Servicio de API para consumir los endpoints /rubros del backend.
 */
class RubroApiService {

  /**
   * Obtiene todos los rubros, con filtro opcional de 'activos'.
   */
  getAll(activos?: boolean): Promise<AxiosResponse<RubroModel[]>> {
    const params = activos === undefined ? {} : { activos };
    return apiClient.get<RubroModel[]>('/rubros', { params });
  }

  /**
   * Obtiene un rubro por su ID de Firestore.
   */
  getById(id: string): Promise<AxiosResponse<RubroModel>> {
    return apiClient.get<RubroModel>(`/rubros/${id}`);
  }

  /**
   * Crea un nuevo rubro.
   * Devuelve la respuesta completa para manejar ABR (200 o 201).
   */
  create(rubro: RubroModel): Promise<AxiosResponse<RubroModel>> {
    // Enviamos el modelo completo, el backend maneja el 'id' nulo
    return apiClient.post<RubroModel>('/rubros', rubro);
  }

  /**
   * Actualiza parcialmente un rubro (PATCH).
   * Solo envía los campos permitidos (nombre, baja_logica).
   */
  update(id: string, rubroUpdate: Pick<RubroModel, 'nombre' | 'baja_logica'>): Promise<AxiosResponse<RubroModel>> {
    return apiClient.patch<RubroModel>(`/rubros/${id}`, rubroUpdate);
  }

  /**
   * Realiza la baja lógica (DELETE) de un rubro.
   */
  delete(id: string): Promise<AxiosResponse<RubroModel>> {
    return apiClient.delete<RubroModel>(`/rubros/${id}`);
  }
}

export const rubroApiService = new RubroApiService();