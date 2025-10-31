# backend/app/modulos/subrubros/helpers/subrubro_helper.py (V12.6)
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1 import Transaction
from ..models import SubRubroModel
# --- INICIO V12.6: Importar decorador ---
from google.cloud import firestore
# --- FIN V12.6 ---

# ... (Excepciones DuplicadoActivo/Inactivo sin cambios) ...
class DuplicadoActivoException(Exception):
    def __init__(self, campo: str, valor: str):
        self.detail = f"El campo {campo} con valor '{valor}' ya existe y está activo."
        super().__init__(self.detail)

class DuplicadoInactivoException(Exception):
    def __init__(self, id_inactivo: str, campo: str):
        self.id_inactivo = id_inactivo
        self.campo = campo
        self.detail = {"status": "EXISTE_INACTIVO", "id_inactivo": id_inactivo, "campo": campo}
        super().__init__("Duplicado inactivo encontrado")


# --- INICIO V12.6: Decorador restaurado ---
@firestore.transactional
def _transaccion_crear_subrubro(transaction: Transaction, subrubro_data: dict, db):
# --- FIN V12.6 ---
    """
    Función helper que corre DENTRO de una transacción de Firestore.
    Implementa ABR V12 (Adaptada para SubRubros).
    """
    subrubros_ref = db.collection('subrubros')
    
    # --- INICIO V12.6: Re-validar el Pydantic Model (V10) ---
    # Esto es crucial para que el decorador no falle con el error '_read_only'
    rubro = SubRubroModel.model_validate(subrubro_data) 
    codigo_buscado = rubro.codigo_subrubro
    # --- FIN V12.6 ---

    # 1. Chequeo de duplicados (ABR V12)
    query = subrubros_ref.where(filter=FieldFilter("codigo_subrubro", "==", codigo_buscado)).limit(1)
    docs = list(query.stream(transaction=transaction))

    if docs:
        doc_existente = docs[0]
        datos_existentes = doc_existente.to_dict()
        
        if datos_existentes.get('baja_logica') == True:
            # 2.A. Existe INACTIVO -> Lanzar Doctrina de Reactivación
            raise DuplicadoInactivoException(id_inactivo=doc_existente.id, campo="codigo_subrubro")
        else:
            # 2.B. Existe ACTIVO -> Lanzar Conflicto
            raise DuplicadoActivoException(campo="codigo_subrubro", valor=codigo_buscado)

    # 3. Creación (si no hay duplicados)
    
    # 3.A. Crear el SubRubro
    nuevo_subrubro_ref = subrubros_ref.document()
    nuevo_id = nuevo_subrubro_ref.id
    
    # Usar el 'rubro' validado por Pydantic
    nuevo_data = rubro.model_dump() 
    nuevo_data['id'] = nuevo_id
    
    transaction.set(nuevo_subrubro_ref, nuevo_data)
    
    # [OMISIÓN DOCTRINAL: Creación de Contador omitida]
    
    return SubRubroModel(**nuevo_data)