// frontend/src/services/notificationService.ts (CORREGIDO PARA INICIALIZACIÓN)
import type { ToastServiceMethods } from 'primevue/toastservice';
import type { ToastMessageOptions } from 'primevue/toast';

/**
 * Servicio centralizado para mostrar notificaciones Toast.
 * NECESITA SER INICIALIZADO con la instancia de ToastService de PrimeVue.
 */
class NotificationService {
    private toast?: ToastServiceMethods; // Almacena la instancia de PrimeVue ToastService

    /**
     * Inicializa el servicio con la instancia de ToastService de PrimeVue.
     * DEBE llamarse en main.ts después de app.use(ToastService).
     * @param service Instancia de ToastService obtenida con useToast() en main.ts o App.vue
     */
    initialize(service: ToastServiceMethods): void {
        if (!this.toast) {
            console.log("NotificationService: Inicializado.");
            this.toast = service;
        } else {
            console.warn("NotificationService: Ya estaba inicializado.");
        }
    }

    private show(options: ToastMessageOptions): void {
        if (!this.toast) {
            console.error('NotificationService no ha sido inicializado. Las notificaciones no se mostrarán.', options);
            // Podríamos usar alert como fallback extremo, pero es mejor evitarlo.
            // alert(`[${options.severity || 'info'}] ${options.summary}: ${options.detail}`);
            return;
        }
        this.toast.add(options);
    }

    showSuccess(summary: string, detail?: string, life: number = 3000): void {
        this.show({ severity: 'success', summary: summary, detail: detail, life: life });
    }

    showInfo(summary: string, detail?: string, life: number = 3000): void {
        this.show({ severity: 'info', summary: summary, detail: detail, life: life });
    }

    showWarn(summary: string, detail?: string, life: number = 5000): void {
        this.show({ severity: 'warn', summary: summary, detail: detail, life: life });
    }

    showError(summary: string, detail?: string, life: number = 7000): void {
        this.show({ severity: 'error', summary: summary, detail: detail, life: life });
    }
}

// Exportamos una única instancia (Singleton)
const notificationService = new NotificationService();
export default notificationService; // Asegurar exportación por defecto