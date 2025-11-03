// frontend/src/services/notificationService.ts (CANON V2.3)
// Patrón: Singleton con Lazy Loading (Resuelve el error 'is not a function')

let toastInstance: any = null;

const notificationService = {

    /**
     * Inicializa la instancia del ToastService, debe llamarse una sola vez en main.ts.
     * @param instance La instancia del $toast de PrimeVue.
     */
    initialize(instance: any) {
        if (!toastInstance) {
            toastInstance = instance;
            console.log("NotificationService: ToastService inicializado.");
        }
    },

    /**
     * Retorna la instancia de toast. Lanza un error si no está inicializada.
     */
    getToastInstance() {
        if (!toastInstance) {
            console.error("CRÍTICO: Intentando usar NotificationService antes de inicializar.");
            // Esto evita que la aplicación falle completamente, pero lanza la advertencia
        }
        return toastInstance;
    },

    // Métodos de conveniencia
    showSuccess(summary: string, detail: string = 'Operación completada.') {
        const toast = this.getToastInstance();
        if (toast) {
            toast.add({ severity: 'success', summary: summary, detail: detail, life: 3000 });
        }
    },
    
    showInfo(summary: string, detail: string) {
        const toast = this.getToastInstance();
        if (toast) {
            toast.add({ severity: 'info', summary: summary, detail: detail, life: 3000 });
        }
    },
    
    showWarn(summary: string, detail: string) {
        const toast = this.getToastInstance();
        if (toast) {
            toast.add({ severity: 'warn', summary: summary, detail: detail, life: 5000 });
        }
    },
    
    showError(summary: string, error: any) {
        const toast = this.getToastInstance();
        let detail = "Error desconocido.";

        if (error && error.response && error.response.data && error.response.data.detail) {
            detail = error.response.data.detail; // Errores FastAPI/HTTP
        } else if (typeof error === 'string') {
            detail = error;
        } else if (error instanceof Error) {
            detail = error.message;
        }

        if (toast) {
            toast.add({ severity: 'error', summary: summary, detail: detail, life: 8000 });
        } else {
             // Fallback de Consola si el toast no está montado
             console.error(`ERROR: ${summary} - Detalle: ${detail}`, error);
        }
    }
};

export default notificationService;