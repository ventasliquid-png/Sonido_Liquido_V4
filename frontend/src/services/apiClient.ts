// frontend/src/services/apiClient.ts (VERSIÓN REAL CON FETCH)
import notificationService from './notificationService';

// URL base de tu API backend (asegúrate que sea correcta)
// Si frontend y backend corren en el mismo dominio/puerto en producción,
// podrías usar una ruta relativa como '/api/v1'. Para desarrollo local,
// es común usar la URL completa.
const API_BASE_URL = 'http://127.0.0.1:8000'; // O http://localhost:8000

// Función helper para manejar respuestas y errores comunes
async function handleResponse<T>(response: Response): Promise<{ data: T; status: number }> {
    const status = response.status;
    if (response.ok) {
        // Si la respuesta es 204 No Content, no hay JSON para parsear
        if (status === 204) {
            return { data: null as T, status }; // O podrías devolver un objeto vacío
        }
        try {
            const data = await response.json();
            return { data, status };
        } catch (error) {
            // Error si la respuesta OK no es JSON válido (inesperado)
            console.error("Error al parsear JSON de respuesta OK:", error);
            throw new Error('Respuesta inválida del servidor.');
        }
    } else {
        // Intentar parsear el cuerpo del error si existe
        let errorDetail = `Error ${status}: ${response.statusText}`;
        try {
            const errorData = await response.json();
            errorDetail = errorData.detail || errorDetail; // FastAPI suele usar 'detail'
        } catch (e) {
            // No hacer nada si el cuerpo del error no es JSON
        }
        console.error("Error en API:", status, errorDetail);

        // Lanzar un error estructurado que useRubroStore pueda atrapar
        const error: any = new Error(errorDetail);
        error.response = { status: status, data: { detail: errorDetail } }; // Simular estructura Axios
        throw error;
    }
}

const apiClient = {
    async get<T>(url: string, config?: RequestInit): Promise<{ data: T; status: number }> {
        console.log(`API GET: ${API_BASE_URL}${url}`, config);
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(config?.headers || {}), // Permite añadir/sobrescribir headers
            },
            ...config, // Permite pasar otras opciones de fetch (signal para abortar, etc.)
        });
        return handleResponse<T>(response);
    },

    async post<T>(url: string, data?: any, config?: RequestInit): Promise<{ data: T; status: number }> {
        console.log(`API POST: ${API_BASE_URL}${url}`, data, config);
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(config?.headers || {}),
            },
            body: data ? JSON.stringify(data) : null,
            ...config,
        });
        // NO LLAMAR A NOTIFICATION SERVICE AQUÍ - El store se encargará
        return handleResponse<T>(response);
    },

    async patch<T>(url: string, data?: any, config?: RequestInit): Promise<{ data: T; status: number }> {
        console.log(`API PATCH: ${API_BASE_URL}${url}`, data, config);
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                ...(config?.headers || {}),
            },
            body: data ? JSON.stringify(data) : null,
            ...config,
        });
        // NO LLAMAR A NOTIFICATION SERVICE AQUÍ
        return handleResponse<T>(response);
    },

    // DELETE suele devolver 204 No Content
    async delete(url: string, config?: RequestInit): Promise<{ data: null; status: number }> {
        console.log(`API DELETE: ${API_BASE_URL}${url}`, config);
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'DELETE',
            headers: {
                ...(config?.headers || {}),
            },
            ...config,
        });
        // NO LLAMAR A NOTIFICATION SERVICE AQUÍ
        return handleResponse<null>(response); // Espera null como data si es 204
    }
    // Podrías añadir PUT aquí si lo necesitas
};

export default apiClient;