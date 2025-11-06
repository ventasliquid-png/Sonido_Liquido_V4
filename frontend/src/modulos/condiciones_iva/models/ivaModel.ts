// --- INICIO BLOQUE IVA-F-01 ---
// frontend/src/modulos/condiciones_iva/models/ivaModel.ts

// Define el tipo 'Decimal' para alicuota, alineado al Backend
type Decimal = string | number;

export interface IvaModel {
    id?: string;
    codigo_iva: string;
    nombre: string;
    alicuota: Decimal;
    baja_logica: boolean;
}
// --- FIN BLOQUE IVA-F-01 ---