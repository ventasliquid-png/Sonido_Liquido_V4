// frontend/src/modulos/productos/models/productoModel.ts

// --- Sub-interfaces (Reflejo de models.py) ---
export interface UnidadMinimaEmpaque {
  descripcion: string;
  unidades: number; // float -> number
}

export interface StockDeposito {
  deposito_id: string;
  stock_real: number; // float -> number
}

export interface ComponenteKit {
  producto_id: string;
  cantidad: number; // float -> number
}

// --- Interfaz Principal (Reflejo de ProductoModel v2.0) ---
export interface ProductoModel {
  // 1. Identificación
  id?: string | null; // Opcional en creación, presente en lectura
  sku: string;
  nombre: string;
  codigo_bas: string | null;
  observaciones: string | null;
  baja_logica: boolean;

  // 2. Costos y Precios (Decimal -> string para precisión JSON)
  precio_costo: string;  
  moneda_costo: string;
  precio_base_venta: string;  

  // 3. Logística
  unidad_medida: string;
  unidad_minima_pedido: number; // float -> number
  unidad_minima_empaque: UnidadMinimaEmpaque;

  // 4. Stock
  stock_minimo_pedido: number; // float -> number
  stock_depositos: StockDeposito[];
  stock_comprometido: number; // float -> number
  stock_entrante: number; // float -> number

  // 5. Kits
  es_kit: boolean;
  componentes_kit: ComponenteKit[];
}

// --- Interfaz de Actualización (Reflejo de ProductoUpdateModel v2.0) ---
export interface ProductoUpdateModel {
  sku?: string;
  nombre?: string;
  codigo_bas?: string | null;
  observaciones?: string | null;
  baja_logica?: boolean;

  precio_costo?: string; // Decimal -> string
  moneda_costo?: string;
  precio_base_venta?: string; // Decimal -> string

  unidad_medida?: string;
  unidad_minima_pedido?: number;
  unidad_minima_empaque?: UnidadMinimaEmpaque;
  stock_minimo_pedido?: number;
  stock_depositos?: StockDeposito[];
  stock_comprometido?: number;
  stock_entrante?: number;
  es_kit?: boolean;
  componentes_kit?: ComponenteKit[];
}