from typing import List, Optional
from fastapi import HTTPException, status
from google.cloud.firestore_v1.base_query import FieldFilter
from ..condiciones_iva.models import CondicionIvaModel, CondicionIvaUpdateModel
from ..condiciones_iva.helpers.iva_helper import (
    _transaccion_crear_iva, 
    DuplicadoActivoException, 
    DuplicadoInactivoException,
    DuplicadoException
)
# --- INICIO: Adaptación ST2 (Patrón de Conexión T82) ---
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
# --- FIN: Adaptación ST2 ---


class CondicionIvaService:
    """Implementa la lógica de negocio para Condiciones IVA."""
    
    # [CANON V2.4.1] Doctrina Singleton __init__ (Obligatoria)
    def __init__(self, db_instance: firestore.Client):
        self.db = db_instance
    
    # --- CRUD BASE ---
    
    def crear_iva(self, data: CondicionIvaModel) -> CondicionIvaModel:
        if self.db is None: 
            raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            # Convertimos Decimal a float para Firestore
            iva_dict = data.model_dump(exclude={'id'}, exclude_unset=True) 
            iva_dict['alicuota'] = float(iva_dict['alicuota'])
            
            transaction = self.db.transaction() 
            
            nuevo_id, datos_creados = _transaccion_crear_iva(
                transaction, 
                iva_data=iva_dict, 
                db=self.db
            )
            
            datos_creados['id'] = nuevo_id
            return CondicionIvaModel.model_validate(datos_creados)
        
        except DuplicadoException as e:
            # [CANON V2.4.1] Canon de Separación: Devuelve el status JSON de conflicto
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail={"status": e.status, 
                                        "id_inactivo": e.id_inactivo,
                                        "campo": e.campo})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

    def listar_ivas(self, estado: str = 'activos') -> List[CondicionIvaModel]:
        if self.db is None: 
            raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        try:
            query = self.db.collection('condiciones_iva') 
            
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
                lista.append(CondicionIvaModel.model_validate(datos))
            return lista
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al listar condiciones IVA: {e}")

    def actualizar_iva(self, id: str, data: CondicionIvaUpdateModel) -> Optional[CondicionIvaModel]:
        if self.db is None: 
            raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
            
        try:
            doc_ref = self.db.collection('condiciones_iva').document(id)
            update_data = data.model_dump(exclude_unset=True) 
            
            # Convertimos Decimal a float para Firestore
            if 'alicuota' in update_data and update_data['alicuota'] is not None:
                update_data['alicuota'] = float(update_data['alicuota'])

            doc_ref.update(update_data)
            
            doc = doc_ref.get()
            if doc.exists:
                datos = doc.to_dict()
                datos['id'] = doc.id
                return CondicionIvaModel.model_validate(datos)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar: {e}")

    def baja_logica_iva(self, id: str) -> bool:
        if self.db is None: 
            raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible")
        
        # [CANON V2.4.1] Integridad VIL (Anti-Orfandad)
        # 1. Chequeo de Módulos Hijos (Simulado: Asumo que 'productos' es el hijo)
        hijos_activos_query = self.db.collection('productos').where(filter=FieldFilter("condicion_iva_id", "==", id)).where(filter=FieldFilter("baja_logica", "==", False)).limit(1)
        hijos_activos = list(hijos_activos_query.stream()) # Ejecutar la consulta

        if len(hijos_activos) > 0:
            # 2. Bloqueo de la baja por orfandad.
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail={"status": "TIENE_HIJOS_ACTIVOS",
                                        "message": "No se puede dar de baja la Condición IVA porque tiene Productos activos asociados."})

        try:
            doc_ref = self.db.collection('condiciones_iva').document(id)
            
            # Doctrina VIL (Baja)
            doc_ref.update({"baja_logica": True})
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al dar de baja: {e}")

# Instancia Singleton del Servicio (Adaptación ST2)
condicion_iva_service = CondicionIvaService(db)
