# backend/app/modulos/unidades_medida/helpers/unidad_helper.py
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# --- Excepciones Doctrinales (Replicación ABR V12) ---
class DuplicadoException(Exception):
    def __init__(self, detail: str):
        self.detail = detail

class DuplicadoActivoException(DuplicadoException):
    pass

class DuplicadoInactivoException(DuplicadoException):
    pass
# --- Fin Excepciones ---

@firestore.transactional
def _transaccion_crear_unidad(transaction, unidad_data: dict, db):
    """
    Helper transaccional (Patrón Rubros V12) para crear Unidad de Medida.
    Asegura unicidad de 'codigo_unidad' (Doctrina ABR).
    """
    
    codigo = unidad_data.get('codigo_unidad')
    
    # 1. Búsqueda de duplicados por 'codigo_unidad'
    query_ref = db.collection('unidades_medida').where(filter=FieldFilter("codigo_unidad", "==", codigo))
    docs_existentes = query_ref.stream(transaction=transaction)
    
    duplicado_encontrado = None
    doc_id = None
    for doc in docs_existentes:
        duplicado_encontrado = doc.to_dict()
        doc_id = doc.id
        break 

    if duplicado_encontrado:
        if duplicado_encontrado.get('baja_logica', False):
            # 2.A. Duplicado INACTIVO (ABR V12)
            raise DuplicadoInactivoException(
                detail=f"Código '{codigo}' ya existe pero está inactivo (ID: {doc_id}). ¿Desea reactivarlo?"
            )
        else:
            # 2.B. Duplicado ACTIVO (ABR V12)
            raise DuplicadoActivoException(
                detail=f"Código '{codigo}' ya está en uso activo."
            )

    # 3. No hay duplicados. Creación (Doctrina VIL).
    nuevo_doc_ref = db.collection('unidades_medida').document()
    transaction.create(nuevo_doc_ref, unidad_data)
    
    return nuevo_doc_ref.id, unidad_data