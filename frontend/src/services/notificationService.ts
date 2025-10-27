// frontend/src/services/notificationService.ts (CORREGIDO CON NOMENCLATURA ESPAÑOL)
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
     * @param service Instancia de ToastService obtenida globalmente en main.ts
     */
    initialize(service: ToastServiceMethods): void {
        if (!this.toast) {
            console.log("NotificationService: Inicializado.");
            this.toast = service;
        } else {
            console.warn("NotificationService: Ya estaba inicializado.");
        }
    }

    // Método privado para mostrar el toast, verifica inicialización
    private mostrar(options: ToastMessageOptions): void {
        if (!this.toast) {
            console.error('NotificationService no inicializado. Notificación perdida:', options);
            // Fallback MUY básico si todo falla (solo para depuración extrema)
            // alert(`[${options.severity || 'info'}] ${options.summary}: ${options.detail}`);
            return;
        }
        this.toast.add(options);
    }

    // --- Métodos Públicos con Nomenclatura Canónica (Español) ---

    /** Muestra una notificación de éxito. */
    mostrarExito(titulo: string, detalle?: string, duracion: number = 3000): void {
        this.mostrar({ severity: 'success', summary: titulo, detail: detalle, life: duracion });
    }

    /** Muestra una notificación informativa. */
    mostrarInfo(titulo: string, detalle?: string, duracion: number = 3000): void {
        this.mostrar({ severity: 'info', summary: titulo, detail: detalle, life: duracion });
    }

    /** Muestra una notificación de advertencia. */
    mostrarAdvertencia(titulo: string, detalle?: string, duracion: number = 5000): void {
        this.mostrar({ severity: 'warn', summary: titulo, detail: detalle, life: duracion });
    }

    /** Muestra una notificación de error. */
    mostrarError(titulo: string, detalle?: string, duracion: number = 7000): void {
        this.mostrar({ severity: 'error', summary: titulo, detail: detalle, life: duracion });
    }
}

// Exportamos una única instancia (Singleton)
const notificationService = new NotificationService();
export default notificationService;