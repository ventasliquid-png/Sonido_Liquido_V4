import { defineStore } from 'pinia';
import { productoService } from '../services/productoService';
import type { ProductoModel, ProductoUpdateModel } from '../models/productoModel';
import notificationService from '@/services/notificationService'; // Mantenemos el alias

interface ProductoState {
    productos: ProductoModel[];
    productoSeleccionado: ProductoModel | null;
    estadoCarga: boolean;
    error: string | null;
}

export const useProductoStore = defineStore('producto', {
    state: (): ProductoState => ({
        productos: [],
        productoSeleccionado: null,
        estadoCarga: false,
        error: null,
    }),

    actions: {
        async fetchProductos() {
            this.estadoCarga = true;
            this.error = null;
            try {
                this.productos = await productoService.listarProductos(true);
            } catch (err: any) {
                this.error = "Error al cargar productos.";
                notificationService.mostrarError(this.error);
            } finally {
                this.estadoCarga = false;
            }
        },

        async guardarProducto(data: ProductoModel | ProductoUpdateModel) {
            this.estadoCarga = true;
            try {
                if ('id' in data && data.id) {
                    // Actualización
                    const updateData = data as ProductoUpdateModel;
                    await productoService.actualizarProducto(data.id, updateData);
                    notificationService.mostrarExito('Producto actualizado correctamente.');
                } else {
                    // Creación
                    await productoService.crearProducto(data as ProductoModel);
                    notificationService.mostrarExito('Producto creado correctamente.');
                }
                await this.fetchProductos(); // Refrescar la lista
            } catch (err: any) {
                this.error = "Error al guardar el producto.";
                notificationService.mostrarError(this.error);
            } finally {
                this.estadoCarga = false;
            }
        },

        async eliminarProducto(id: string) {
            this.estadoCarga = true;
            try {
                await productoService.bajaLogicaProducto(id);
                notificationService.mostrarExito('Producto dado de baja.');
                await this.fetchProductos(); // Refrescar la lista
            } catch (err: any) {
                this.error = "Error al eliminar el producto.";
                notificationService.mostrarError(this.error);
            } finally {
                this.estadoCarga = false;
            }
        },

        seleccionarProducto(producto: ProductoModel | null) {
            this.productoSeleccionado = producto;
        }
    }
});