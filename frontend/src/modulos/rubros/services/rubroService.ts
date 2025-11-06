// --- INICIO REPARACIÓN G-R-12 (Refactorización) ---
import apiClient from '@/services/apiClient'; // Ruta global no cambia
import type { RubroModel, RubroUpdateModel } from '../models/rubroModel';
// --- FIN REPARACIÓN G-R-12 ---
import type { AxiosResponse } from 'axios';

/**
 * Servicio de API para consumir los endpoints /rubros del backend.
 */
class RubroApiService {

  /**
   * Obtiene todos los rubros, con filtro opcional de 'estado'.
   * REPARACIÓN G-R-04: Se alinea con la Doctrina VIL (Filtro de Tres Vías).
   * El parámetro 'activos?: boolean' se reemplaza por 'estado: string'.
   */
  getAll(estado: string = 'activos'): Promise<AxiosResponse<RubroModel[]>> {
    // El backend (service.py) espera un query param llamado 'estado'
    const params = { estado: estado };
    
    // Se añade el / final para consistencia con FastAPI (evita Redirect 307)
    return apiClient.get<RubroModel[]>('/rubros/', { params });
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
    // Se añade el / final para consistencia con FastAPI
    return apiClient.post<RubroModel>('/rubros/', rubro);
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
  delete(id: string): Promise<AxiosResponse<void>> {
    // REPARACIÓN G-R-04: La API de baja lógica (DELETE) no debe devolver datos (204 No Content).
    // Cambiamos el tipo de retorno esperado a 'void' para alinear con el backend.
    return apiClient.delete<void>(`/rubros/${id}`);
  }
}

export const rubroApiService = new RubroApiService();
