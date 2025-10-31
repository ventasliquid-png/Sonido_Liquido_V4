// frontend/src/modulos/subrubros/models/subRubroModel.ts
export interface SubRubroModel {
  id?: string | null;
  codigo_subrubro: string;
  nombre: string;
  baja_logica: boolean;
}

export interface SubRubroUpdateModel {
  nombre?: string;
  baja_logica?: boolean;
}