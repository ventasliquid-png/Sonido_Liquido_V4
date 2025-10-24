// frontend/src/services/notificationService.ts
import { useToast } from 'primevue/usetoast';

// Definimos una interfaz para desacoplar de la implementación exacta de PrimeVue
interface ToastServiceMethods {
    add(options: any): void;
}

class NotificationService {
    private toast: ToastServiceMethods | null = null;

    public inicializar(toastInstance: ToastServiceMethods): void {
        this.toast = toastInstance;
    }

    private verificarInicializacion(): void {
        if (!this.toast) {
            // Usamos console.error en lugar de throw para no detener la app
            console.error("NotificationService no ha sido inicializado. Las notificaciones no se mostrarán.");
        }
    }

    public mostrarExito(mensaje: string, titulo: string = 'Éxito'): void {
        this.verificarInicializacion();
        this.toast?.add({ severity: 'success', summary: titulo, detail: mensaje, life: 3000 });
    }

    public mostrarError(mensaje: string, titulo: string = 'Error'): void {
        this.verificarInicializacion();
        this.toast?.add({ severity: 'error', summary: titulo, detail: mensaje, life: 3000 });
    }

    public mostrarAdvertencia(mensaje: string, titulo: string = 'Advertencia'): void {
        this.verificarInicializacion();
        this.toast?.add({ severity: 'warn', summary: titulo, detail: mensaje, life: 3000 });
    }
}

const notificationService = new NotificationService();
export default notificationService;