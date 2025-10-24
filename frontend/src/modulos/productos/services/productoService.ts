import apiClient from '@/services/apiClient'; // Mantenemos el alias, crearemos apiClient.ts
import type { ProductoModel, ProductoUpdateModel } from '../models/productoModel'; // Asume que los modelos se importan

class ProductoApiService {

    async crearProducto(data: ProductoModel): Promise<ProductoModel> {
        const response = await apiClient.post<ProductoModel>('/productos/', data);
        return response.data;
    }

    async listarProductos(activos: boolean = true): Promise<ProductoModel[]> {
        const response = await apiClient.get<ProductoModel[]>('/productos/', { params: { activos } });
        return response.data;
    }

    async actualizarProducto(id: string, data: ProductoUpdateModel): Promise<ProductoModel> {
        const response = await apiClient.patch<ProductoModel>(`/productos/${id}`, data);
        return response.data;
    }

    async bajaLogicaProducto(id: string): Promise<void> {
        await apiClient.delete(`/productos/${id}`);
    }

    async obtenerProductoPorId(id: string): Promise<ProductoModel> {
        const response = await apiClient.get<ProductoModel>(`/productos/id/${id}`);
        return response.data;
    }
}

export const productoService = new ProductoApiService();