# backend/app/modulos/rubros/helpers/rubro_helper.py
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1 import Transaction
from ..models import RubroModel
# Importar la instancia real de la DB
# from core.database import db

# --- Excepciones personalizadas para el flujo ABR V12 ---
class DuplicadoActivoException(Exception):
    def __init__(self, campo: str, valor: str):
        self.detail = f"El campo {campo} con valor '{valor}' ya existe y está activo."
        super().__init__(self.detail)

class DuplicadoInactivoException(Exception):
    def __init__(self, id_inactivo: str, campo: str):
        self.id_inactivo = id_inactivo
        self.campo = campo
        # El JSON de la "Doble Aceptación"
        self.detail = {"status": "EXISTE_INACTIVO", "id_inactivo": id_inactivo, "campo": campo}
        super().__init__("Duplicado inactivo encontrado")

# @firestore.transactional # Decorador aplicado por la función que llama
def _transaccion_crear_rubro(transaction: Transaction, rubro_data: dict, db):
    """
    Función helper que corre DENTRO de una transacción de Firestore.
    Implementa ABR V12 y la Doctrina de Contadores.
    """
    rubros_ref = db.collection('rubros')
    contadores_ref = db.collection('contadores') # Requerido por Doctrina Rubros
    
    codigo_buscado = rubro_data.get('codigo')

    # 1. Chequeo de duplicados (ABR V12)
    query = rubros_ref.where(filter=FieldFilter("codigo", "==", codigo_buscado)).limit(1)
    docs = list(query.stream(transaction=transaction))

    if docs:
        doc_existente = docs[0]
        datos_existentes = doc_existente.to_dict()
        
        if datos_existentes.get('baja_logica') == True:
            # 2.A. Existe INACTIVO -> Lanzar Doctrina de Reactivación
            raise DuplicadoInactivoException(id_inactivo=doc_existente.id, campo="codigo")
        else:
            # 2.B. Existe ACTIVO -> Lanzar Conflicto
            raise DuplicadoActivoException(campo="codigo", valor=codigo_buscado)

    # 3. Creación (si no hay duplicados)
    
    # 3.A. Crear el Rubro
    nuevo_rubro_ref = rubros_ref.document()
    nuevo_id = nuevo_rubro_ref.id
    rubro_data['id'] = nuevo_id
    transaction.set(nuevo_rubro_ref, rubro_data)
    
    # 3.B. Crear el Contador (Doctrina ID Soberano Universal)
    contador_ref = contadores_ref.document(nuevo_id)
    transaction.set(contador_ref, {'ultimo_valor': 0})
    
    return RubroModel(**rubro_data)