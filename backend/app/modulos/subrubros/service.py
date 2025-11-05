from typing import List, Optional
from fastapi import HTTPException, status
from google.cloud.firestore_v1.base_query import FieldFilter
from .models import SubRubroModel, SubRubroUpdateModel
from .helpers.subrubro_helper import _transaccion_crear_subrubro, DuplicadoActivoException, DuplicadoInactivoException

# --- INICIO: Conexión a DB Real (Patrón Rubros Blindado) ---
from google.cloud import firestore
from google.oauth2 import service_account
import os 

ruta_llave_absoluta = "C:/dev/Sonido_Liquido_V4/service-account-v4.json"

try:
    credentials = service_account.Credentials.from_service_account_file(ruta_llave_absoluta)
    db = firestore.Client(credentials=credentials)
except Exception as e:
    print(f"ERROR CRÍTICO: No se pudo cargar la llave de Firestore desde {ruta_llave_absoluta}")
    print(f"Error: {e}")
    db = None 

# [Helper 'run_in_transaction' ELIMINADO]
# --- FIN: Conexión a DB Real ---


class SubRubroService:
    # CORRECCIÓN DE ESTABILIDAD: Asegurar que la instancia DB esté siempre disponible
    def __init__(self, db_instance):
        self.db = db_instance
    
    # Esta función NO es async, porque llama a la transacción (sync)
    def crear_subrubro(self, data: SubRubroModel) -> SubRubroModel:
        if self.db is None: # Uso de self.db
                raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            # Convertimos a dict para evitar el error '_read_only' del decorador
            subrubro_dict = data.model_dump(exclude={'id'}, exclude_unset=True) 
            
            # Creamos el objeto de transacción
            transaction = self.db.transaction() # Uso de self.db
            
            # === CORRECCIÓN DE ERROR 500 (Respuesta de Tupla) ===
            # El helper devuelve una tupla (doc_id, subrubro_data_dict)
            doc_id, subrubro_data_dict = _transaccion_crear_subrubro(
                transaction, # <-- Pasamos la transacción
                subrubro_data=subrubro_dict,
                db=self.db # Uso de self.db 
            )
            
            # Asignamos el ID de Firestore al dict ANTES de validar el modelo
            subrubro_data_dict['id'] = doc_id 
            
            # Validar y retornar el SubRubroModel completo
            return SubRubroModel.model_validate(subrubro_data_dict)
            # === FIN DE CORRECCIÓN ===
        
        except DuplicadoActivoException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)
        except DuplicadoInactivoException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

    # Esta función NO es async (corrige el error 'object generator')
    def listar_subrubros(self, estado: str = 'activos') -> List[SubRubroModel]:
        if self.db is None: # Uso de self.db
                raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            query = self.db.collection('subrubros') # Uso de self.db
            if estado == 'activos':
                query = query.where(filter=FieldFilter("baja_logica", "==", False))
            elif estado == 'inactivos':
                query = query.where(filter=FieldFilter("baja_logica", "==", True))
            
            docs = query.stream() # <-- 'await' ELIMINADO
            lista = []
            for doc in docs:
                lista.append(SubRubroModel.model_validate(doc.to_dict())) 
            return lista
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al listar subrubros: {e}")

    # Convertida a función síncrona (def) y 'await' eliminados
    def actualizar_subrubro(self, id: str, data: SubRubroUpdateModel) -> Optional[SubRubroModel]:
        if self.db is None: # Uso de self.db
                raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            doc_ref = self.db.collection('subrubros').document(id) # Uso de self.db
            update_data = data.model_dump(exclude_unset=True) 
            
            doc_ref.update(update_data) # <-- 'await' ELIMINADO
            
            doc = doc_ref.get() # <-- 'await' ELIMINADO
            if doc.exists:
                return SubRubroModel.model_validate(doc.to_dict()) 
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar: {e}")

    # Convertida a función síncrona (def) y 'await' eliminado
    def baja_logica_subrubro(self, id: str) -> bool:
        if self.db is None: # Uso de self.db
                raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            doc_ref = self.db.collection('subrubros').document(id) # Uso de self.db
            doc_ref.update({"baja_logica": True}) # <-- 'await' ELIMINADO
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al dar de baja: {e}")

# Instancia Singleton del Servicio
subrubro_service = SubRubroService(db)
