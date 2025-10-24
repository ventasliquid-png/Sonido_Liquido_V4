// frontend/src/services/apiClient.ts
// Placeholder básico para simular Axios o un wrapper similar
// En una implementación real, aquí configurarías Axios con la URL base, interceptors, etc.
import notificationService from './notificationService'; // Usa ruta relativa aquí

const apiClient = {
  async get<T>(url: string, config?: any): Promise<{ data: T }> {
    console.log(`API GET: ${url}`, config);
    // Simulación muy básica - ¡Reemplazar con llamada real!
    if (url.startsWith('/productos/')) { // Simula obtener un producto
          return Promise.resolve({ data: { id:'mock-id', sku: 'MOCK01', nombre: 'Producto Mock', precio_costo: "100.00", precio_base_venta: "150.00", baja_logica: false } as any });
    }
    // Simula obtener lista
    return Promise.resolve({ data: [] as any });
  },
  async post<T>(url: string, data?: any, config?: any): Promise<{ data: T }> {
     console.log(`API POST: ${url}`, data, config);
     notificationService.mostrarExito('Creación simulada exitosa.');
     // Simulación muy básica
     const mockId = `mock-${Date.now()}`;
     return Promise.resolve({ data: { ...data, id: mockId } as any });
  },
  async patch<T>(url: string, data?: any, config?: any): Promise<{ data: T }> {
      console.log(`API PATCH: ${url}`, data, config);
      notificationService.mostrarExito('Actualización simulada exitosa.');
      // Simulación muy básica
      return Promise.resolve({ data: { ...data } as any }); // Devuelve los datos enviados
  },
  async delete(url: string, config?: any): Promise<void> {
      console.log(`API DELETE: ${url}`, config);
      notificationService.mostrarExito('Eliminación simulada exitosa.');
       // Simulación muy básica
      return Promise.resolve();
  }
};

export default apiClient;