from typing import List, Optional, Tuple, Dict
import uuid
from fastapi import HTTPException, status
# Línea CORRECTA
from .models import RubroModel, RubroUpdateModel # Usa '.' para importar desde el directorio actual

# --- Mock DB ---
# Simulación de la colección de Firestore para Rubros
# Usamos un diccionario para búsqueda rápida por ID
MOCK_RUBROS_DB: Dict[str, RubroModel] = {
    "1": RubroModel(id="1", codigo="GEN", nombre="General", baja_logica=False),
    "2": RubroModel(id="2", codigo="VAR", nombre="Varios", baja_logica=True), # Rubro en baja
}
# -----------------

class RubroService:
    """
    Capa de lógica de negocio para gestionar Rubros.
    Simula la interacción con la base de datos (Firestore Mock).
    """

    def _get_by_id_mock(self, id: str) -> Optional[RubroModel]:
        """Auxiliar: Busca en el mock DB por ID."""
        return MOCK_RUBROS_DB.get(id)

    def _get_by_codigo_mock(self, codigo: str) -> Optional[RubroModel]:
        """Auxiliar: Busca en el mock DB por código."""
        for rubro in MOCK_RUBROS_DB.values():
            if rubro.codigo == codigo:
                return rubro
        return None

    def crear_rubro(self, rubro: RubroModel) -> Tuple[RubroModel, str]:
        """
        Crea un nuevo rubro o lo reactiva si existe y está en baja_logica.
        Implementa la Doctrina de Reactivación (ABR).
        Devuelve (RubroModel, "created" | "reactivated").
        """
        existente = self._get_by_codigo_mock(rubro.codigo)

        if existente:
            if existente.baja_logica:
                # --- Doctrina ABR: Reactivación ---
                # Actualiza el registro existente con los nuevos datos
                existente.baja_logica = False
                existente.nombre = rubro.nombre
                # (MOCK_RUBROS_DB se actualiza por referencia)
                return existente, "reactivated"
            else:
                # --- Doctrina ABR: Conflicto ---
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El código de rubro '{rubro.codigo}' ya existe y está activo."
                )
        
        # --- Creación Estándar ---
        nuevo_id = str(uuid.uuid4()) # Simula generación de ID de Firestore
        nuevo_rubro = RubroModel(
            id=nuevo_id,
            **rubro.model_dump(exclude={"id"}) # Usa datos del payload
        )
        MOCK_RUBROS_DB[nuevo_id] = nuevo_rubro
        return nuevo_rubro, "created"

    def obtener_rubro_por_id(self, id: str) -> RubroModel:
        """Obtiene un rubro por su ID (Firestore)."""
        rubro = self._get_by_id_mock(id)
        if not rubro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado")
        return rubro

    def obtener_rubro_por_codigo(self, codigo: str) -> RubroModel:
        """Obtiene un rubro por su 'codigo' (negocio)."""
        rubro = self._get_by_codigo_mock(codigo)
        if not rubro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado")
        return rubro

    def listar_rubros(self, activos: Optional[bool] = None) -> List[RubroModel]:
        """
        Lista todos los rubros.
        Si 'activos' es True, filtra solo los que no están en baja_logica.
        Si 'activos' es False, filtra solo los que están en baja_logica.
        """
        rubros = list(MOCK_RUBROS_DB.values())
        
        if activos is None:
            return rubros
        elif activos:
            return [r for r in rubros if not r.baja_logica]
        else:
            return [r for r in rubros if r.baja_logica]

    def actualizar_rubro(self, id: str, rubro_update: RubroUpdateModel) -> RubroModel:
        """Actualiza parcialmente un rubro (PATCH)."""
        rubro = self.obtener_rubro_por_id(id)
        
        update_data = rubro_update.model_dump(exclude_unset=True)
        
        if not update_data:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay datos para actualizar")

        for key, value in update_data.items():
            setattr(rubro, key, value)
            
        # (MOCK_RUBROS_DB se actualiza por referencia)
        return rubro

    def baja_logica_rubro(self, id: str) -> RubroModel:
        """Realiza una baja lógica de un rubro."""
        rubro = self.obtener_rubro_por_id(id)
        
        if rubro.baja_logica:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rubro ya está dado de baja")

        rubro.baja_logica = True
        # (MOCK_RUBROS_DB se actualiza por referencia)
        return rubro