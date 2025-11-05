# backend/app/modulos/subrubros/helpers/subrubro_helper.py
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import json # Importar json para la carga de detalles

# --- Excepciones Doctrinales (Replicación ABR V12) ---
class DuplicadoException(Exception):
    def __init__(self, detail): # Detail puede ser string o dict
        self.detail = detail

class DuplicadoActivoException(DuplicadoException):
    pass

class DuplicadoInactivoException(DuplicadoException):
    pass
# --- Fin Excepciones ---

@firestore.transactional
def _transaccion_crear_subrubro(transaction, subrubro_data: dict, db):
    """
    Helper transaccional (Patrón Rubros V12) para crear SubRubro.
    Asegura unicidad de 'codigo_subrubro' (Doctrina ABR).
    """

    codigo = subrubro_data.get('codigo_subrubro')

    # 1. Búsqueda de duplicados por 'codigo_subrubro'
    query_ref = db.collection('subrubros').where(filter=FieldFilter("codigo_subrubro", "==", codigo))
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
            # *** CORRECCIÓN CANON V2.3: Devolver JSON Estructurado ***
            raise DuplicadoInactivoException(
                detail={
                    "status": "EXISTE_INACTIVO",
                    "id_inactivo": doc_id,
                    "campo": "código" # El campo que causó el duplicado
                }
            )
        else:
            # 2.B. Duplicado ACTIVO (ABR V12)
            # *** CORRECCIÓN CANON V2.3: Devolver JSON Estructurado ***
            raise DuplicadoActivoException(
                detail={
                    "status": "EXISTE_ACTIVO",
                    "message": f"Código '{codigo}' ya está en uso activo."
                }
            )

    # 3. No hay duplicados. Creación (Doctrina VIL).
    nuevo_doc_ref = db.collection('subrubros').document()
    transaction.create(nuevo_doc_ref, subrubro_data)

    return nuevo_doc_ref.id, subrubro_data
