# backend/app/modulos/subrubros/service.py (V12.6 - Patrón V11 Restaurado)
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
    
    # Esta función NO es async, porque llama a la transacción (sync)
    def crear_subrubro(self, data: SubRubroModel) -> SubRubroModel:
        if db is None:
             raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            # --- INICIO: CORRECCIÓN V12.6 (Patrón V11) ---
            # Convertimos a dict para evitar el error '_read_only' del decorador
            subrubro_dict = data.model_dump(exclude={'id'}, exclude_unset=True) 
            
            # Creamos el objeto de transacción
            transaction = db.transaction() 
            
            # Llamamos a la función helper (decorada)
            nuevo_subrubro = _transaccion_crear_subrubro(
                transaction, # <-- Pasamos la transacción
                subrubro_data=subrubro_dict,
                db=db 
            )
            # --- FIN: CORRECCIÓN V12.6 ---
            
            return nuevo_subrubro
        
        except DuplicadoActivoException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)
        except DuplicadoInactivoException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

    # Esta función NO es async (corrige el error 'object generator')
    def listar_subrubros(self, estado: str = 'activos') -> List[SubRubroModel]:
        if db is None:
             raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            query = db.collection('subrubros')
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

    # Esta SÍ es async
    async def actualizar_subrubro(self, id: str, data: SubRubroUpdateModel) -> Optional[SubRubroModel]:
        if db is None:
             raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            doc_ref = db.collection('subrubros').document(id)
            update_data = data.model_dump(exclude_unset=True) 
            await doc_ref.update(update_data)
            
            doc = await doc_ref.get()
            if doc.exists:
                return SubRubroModel.model_validate(doc.to_dict()) 
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar: {e}")

    # Esta SÍ es async
    async def baja_logica_subrubro(self, id: str) -> bool:
        if db is None:
             raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            doc_ref = db.collection('subrubros').document(id)
            await doc_ref.update({"baja_logica": True})
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al dar de baja: {e}")

subrubro_service = SubRubroService()