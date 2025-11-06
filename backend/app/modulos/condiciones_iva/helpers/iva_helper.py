from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# --- Excepciones Doctrinales (Canon de Separación) ---
class DuplicadoException(Exception):
    def __init__(self, status: str, id_inactivo: str = None, campo: str = None):
        # El helper solo reporta el status JSON de conflicto.
        # El Frontend (store.ts) es responsable de construir el mensaje amigable.
        self.status = status 
        self.id_inactivo = id_inactivo
        self.campo = campo

class DuplicadoActivoException(DuplicadoException):
    pass # status: 'EXISTE_ACTIVO'

class DuplicadoInactivoException(DuplicadoException):
    pass # status: 'EXISTE_INACTIVO'
# --- Fin Excepciones ---

@firestore.transactional
def _transaccion_crear_iva(transaction, iva_data: dict, db):
    """
    Helper transaccional (Doctrina ABR) para crear Condición IVA.
    Asegura unicidad sobre 'codigo_iva'.
    """
    
    codigo = iva_data.get('codigo_iva')
    
    # 1. Búsqueda de duplicados por 'codigo_iva'
    query_ref = db.collection('condiciones_iva').where(filter=FieldFilter("codigo_iva", "==", codigo))
    docs_existentes = query_ref.stream(transaction=transaction)
    
    duplicado_encontrado = None
    doc_id = None
    for doc in docs_existentes:
        duplicado_encontrado = doc.to_dict()
        doc_id = doc.id
        break 

    if duplicado_encontrado:
        if duplicado_encontrado.get('baja_logica', False):
            # 2.A. Duplicado INACTIVO: Reporta status para reactivación (Canon V2.4.1)
            raise DuplicadoInactivoException(
                status='EXISTE_INACTIVO',
                id_inactivo=doc_id,
                campo='código'
            )
        else:
            # 2.B. Duplicado ACTIVO: Reporta status de conflicto (Canon V2.4.1)
            raise DuplicadoActivoException(
                status='EXISTE_ACTIVO',
                campo='código'
            )

    # 3. No hay duplicados. Creación (Doctrina VIL).
    nuevo_doc_ref = db.collection('condiciones_iva').document()
    transaction.create(nuevo_doc_ref, iva_data)
    
    return nuevo_doc_ref.id, iva_data
