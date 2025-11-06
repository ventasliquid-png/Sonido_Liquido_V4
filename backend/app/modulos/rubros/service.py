from typing import List, Optional
from fastapi import HTTPException, status
from google.cloud.firestore_v1.base_query import FieldFilter
from .models import RubroModel, RubroUpdateModel
from .helpers.rubro_helper import _transaccion_crear_rubro, DuplicadoActivoException, DuplicadoInactivoException

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

# --- FIN: Conexión a DB Real ---


class RubroService:
    # CORRECCIÓN DE ESTABILIDAD: Asegurar que la instancia DB esté siempre disponible
    def __init__(self, db_instance):
        self.db = db_instance

    # --- CORREGIDO: Se aplica la Doctrina V12.13 (Patrón SubRubros) ---
    def crear_rubro(self, data: RubroModel) -> RubroModel:
        if self.db is None:
              raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")

        try:
            rubro_dict = data.model_dump(exclude={'id'}, exclude_unset=True)

            # 1. Se crea el objeto de transacción
            transaction = self.db.transaction()

            # 2. Se llama al helper DECORADO, pasándole la 'transaction'
            nuevo_rubro = _transaccion_crear_rubro(
                transaction,
                rubro_data=rubro_dict,
                db=self.db
            )

            return nuevo_rubro

        except DuplicadoActivoException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)
        except DuplicadoInactivoException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

    # --- Síncrono (def) y 'await' eliminado ---
    def listar_rubros(self, estado: str = 'activos') -> List[RubroModel]:
        if self.db is None:
              raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")

        try:
            query = self.db.collection('rubros')
            if estado == 'activos':
                query = query.where(filter=FieldFilter("baja_logica", "==", False))
            elif estado == 'inactivos':
                query = query.where(filter=FieldFilter("baja_logica", "==", True))

            docs = query.stream()
            lista = []
            
            # --- INICIO REPARACIÓN DOCTRINAL (FALLO CRÍTICO ID) ---
            # Se debe adjuntar el ID del documento al diccionario antes de validar
            # para que el frontend pueda operar (Editar/Baja).
            for doc in docs:
                datos = doc.to_dict()
                datos['id'] = doc.id 
                lista.append(RubroModel.model_validate(datos))
            # --- FIN REPARACIÓN DOCTRINAL ---
                
            return lista

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al listar rubros: {e}")

    # --- Síncrono (def) y 'await' eliminados ---
    def actualizar_rubro(self, id: str, data: RubroUpdateModel) -> Optional[RubroModel]:
        if self.db is None:
              raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")

        try:
            doc_ref = self.db.collection('rubros').document(id)
            update_data = data.model_dump(exclude_unset=True)

            doc_ref.update(update_data)

            doc = doc_ref.get()
            if doc.exists:
                # --- REPARACIÓN DOCTRINAL (FALLO ID): Asegurar retorno de ID ---
                datos = doc.to_dict()
                datos['id'] = doc.id
                return RubroModel.model_validate(datos)
                # --- FIN REPARACIÓN DOCTRINAL ---
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar: {e}")

    # --- Síncrono (def) y 'await' eliminado ---
    def baja_logica_rubro(self, id: str) -> bool:
        if self.db is None:
              raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")

        try:
            doc_ref = self.db.collection('rubros').document(id)
            doc_ref.update({"baja_logica": True})
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al dar de baja: {e}")

# Instancia Singleton del Servicio
rubro_service = RubroService(db)
