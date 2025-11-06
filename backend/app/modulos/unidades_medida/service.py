# backend/app/modulos/unidades_medida/service.py (CORRECCIÓN DE ESTABILIDAD)

from typing import List, Optional
from fastapi import HTTPException, status
from google.cloud.firestore_v1.base_query import FieldFilter
from .models import UnidadMedidaModel, UnidadMedidaUpdateModel
from .helpers.unidad_helper import (
    _transaccion_crear_unidad,
    DuplicadoActivoException,
    DuplicadoInactivoException
)

# --- INICIO: Conexión a DB Real (Patrón Canónico) ---
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

class UnidadMedidaService:
    # REFUERZO DE DOCTRINA: Constructor explícito para evitar AttributeError: 'XyzService' object has no attribute 'db'
    def __init__(self, db_instance):
        self.db = db_instance

    def crear_unidad(self, data: UnidadMedidaModel) -> UnidadMedidaModel:
        if self.db is None: # Uso de self.db
            raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")

        try:
            unidad_dict = data.model_dump(exclude={'id'}, exclude_unset=True)

            transaction = self.db.transaction() # Uso de self.db

            nuevo_id, datos_creados = _transaccion_crear_unidad(
                transaction,
                unidad_data=unidad_dict,
                db=self.db # Uso de self.db
            )

            datos_creados['id'] = nuevo_id
            return UnidadMedidaModel.model_validate(datos_creados)

        except DuplicadoActivoException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)
        except DuplicadoInactivoException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

    def listar_unidades(self, estado: str = 'activos') -> List[UnidadMedidaModel]:
        if self.db is None: # Uso de self.db
            raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")

        try:
            query = self.db.collection('unidades_medida') # Uso de self.db

            # Doctrina VIL (Filtro de Tres Vías)
            if estado == 'activos':
                query = query.where(filter=FieldFilter("baja_logica", "==", False))
            elif estado == 'inactivos':
                query = query.where(filter=FieldFilter("baja_logica", "==", True))

            docs = query.stream()
            lista = []
            for doc in docs:
                datos = doc.to_dict()
                datos['id'] = doc.id
                lista.append(UnidadMedidaModel.model_validate(datos))
            return lista

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al listar unidades: {e}")

    def actualizar_unidad(self, id: str, data: UnidadMedidaUpdateModel) -> Optional[UnidadMedidaModel]:
        if self.db is None: # Uso de self.db
            raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")

        try:
            doc_ref = self.db.collection('unidades_medida').document(id) # Uso de self.db
            update_data = data.model_dump(exclude_unset=True)

            doc_ref.update(update_data)

            doc = doc_ref.get()
            if doc.exists:
                datos = doc.to_dict()
                datos['id'] = doc.id
                return UnidadMedidaModel.model_validate(datos)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar: {e}")

    def baja_logica_unidad(self, id: str) -> bool:
        if self.db is None: # Uso de self.db
            raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")

        try:
            doc_ref = self.db.collection('unidades_medida').document(id) # Uso de self.db

            # Doctrina VIL (Baja)
            doc_ref.update({"baja_logica": True})
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al dar de baja: {e}")

# Instancia Singleton del Servicio: Ahora se pasa la instancia 'db'
unidad_medida_service = UnidadMedidaService(db)
