// frontend/src/services/apiClient.ts
import axios from 'axios';
import notificationService from './notificationService';

// --- Ajuste Crítico CORS: Usar localhost para forzar la coincidencia de origen/destino ---
const API_URL = 'http://localhost:8000'; // FORZAR LOCALHOST

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interceptor de Solicitudes (Opcional: Agregar lógica de autenticación o logging)
apiClient.interceptors.request.use(
    (config) => {
        // console.log(`API ${config.method.toUpperCase()}: ${config.baseURL}${config.url}`, config.params || config.data);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor de Respuestas
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        const message = error.response?.data?.detail || error.message;
        const status = error.response?.status;

        // Manejo de errores específicos
        if (status === 409) {
            // Error de conflicto (ABR V12 - Duplicado)
            // Esto se maneja a nivel de Store para dar un mensaje más amigable
            return Promise.reject(error); 
        } else if (status === 404) {
            notificationService.showWarn("Error 404", "El recurso solicitado no fue encontrado.");
        } else if (status === 503) {
            notificationService.showError("Error Crítico", "El servicio de Backend no está disponible (503).");
        } else {
            notificationService.showError(`Error ${status || 'de red'}`, message);
        }

        return Promise.reject(error);
    }
);

export default apiClient;