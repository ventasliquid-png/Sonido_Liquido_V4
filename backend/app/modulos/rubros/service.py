# backend/app/modulos/rubros/service.py (LLAMADA TRANSACCIONAL CORREGIDA)

# ... (importaciones y __init__ sin cambios respecto a la versión con logging detallado) ...
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from google.cloud import firestore
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.transaction import Transaction
from google.cloud.firestore_v1.document import DocumentReference
import google.auth
from google.oauth2 import service_account
from .models import RubroModel, RubroUpdateModel # <-- Ahora usa el model con Alias
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
CREDENTIALS_FILENAME = "service-account-v4.json"
CREDENTIALS_PATH = os.path.join(PROJECT_ROOT, CREDENTIALS_FILENAME)
logger.info(f"Ruta calculada para credenciales: {CREDENTIALS_PATH}")

class RubroService:
    def __init__(self):
        # ... (código __init__ sin cambios) ...
        try:
            logger.info(f"Intentando cargar credenciales desde: {CREDENTIALS_PATH}")
            if not os.path.exists(CREDENTIALS_PATH) or not os.path.isfile(CREDENTIALS_PATH): logger.error(f"¡¡¡Archivo de credenciales NO encontrado o no es un archivo!!!: {CREDENTIALS_PATH}"); raise FileNotFoundError(f"Archivo de credenciales no encontrado en {CREDENTIALS_PATH}")
            credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
            self.db: Client = firestore.Client(credentials=credentials)
            self.rubros_ref = self.db.collection("rubros"); self.contadores_ref = self.db.collection("counters")
            logger.info("Firestore client and collections initialized using explicit credentials.")
        except FileNotFoundError as fnf_error: logger.error(f"Error específico al buscar archivo credenciales: {fnf_error}", exc_info=True); raise RuntimeError(f"Error al inicializar Firestore: {fnf_error}")
        except Exception as e: logger.error(f"Error general al inicializar Firestore con credenciales explícitas: {e}", exc_info=True); raise RuntimeError(f"Error al inicializar Firestore ({type(e).__name__}): {e}")

    @firestore.transactional
    def _crear_rubro_atomic_transactional(self, transaction: Transaction, rubro: RubroModel) -> Tuple[DocumentReference, str]:
        # ... (código interno sin cambios) ...
        logger.info(f"Transaction: Checking existence for code {rubro.codigo}")
        query = self.rubros_ref.where("codigo", "==", rubro.codigo).limit(1) # IMPORTANTE: Firestore usa 'codigo' aquí si el alias en Pydantic es 'codigo'/'code'
        existentes = list(query.stream(transaction=transaction))
        if existentes:
            existente_doc = existentes[0]; existente_ref = existente_doc.reference; existente_data = existente_doc.to_dict()
            logger.info(f"Transaction: Found existing document {existente_ref.id} for code {rubro.codigo}")
            if existente_data.get("baja_logica"): # Asume que Firestore guarda 'baja_logica'
                logger.info(f"Transaction: Reactivating document {existente_ref.id}")
                transaction.update(existente_ref, {"baja_logica": False, "nombre": rubro.nombre}) # Usar 'nombre' para actualizar
                return existente_ref, "reactivated"
            else:
                logger.warning(f"Transaction: Conflict - Code {rubro.codigo} already active.")
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El código de rubro '{rubro.codigo}' ya existe y está activo.")
        logger.info(f"Transaction: Creating new document for code {rubro.codigo}")
        nuevo_rubro_ref = self.rubros_ref.document()
        # Usar model_dump(by_alias=False) para obtener dict con nombres de Pydantic ('codigo', 'nombre') para guardar consistentemente
        nuevo_data = rubro.model_dump(by_alias=False, exclude={"id"}, exclude_defaults=False)
        nuevo_data["id"] = nuevo_rubro_ref.id
        nuevo_data["baja_logica"] = nuevo_data.get("baja_logica", False)
        transaction.set(nuevo_rubro_ref, nuevo_data); logger.info(f"Transaction: Rubro document {nuevo_rubro_ref.id} set.")
        nuevo_contador_ref = self.contadores_ref.document(nuevo_rubro_ref.id); datos_nuevo_contador = {'ultimo_valor': 0}
        transaction.set(nuevo_contador_ref, datos_nuevo_contador); logger.info(f"Transaction: Counter document {nuevo_contador_ref.id} set.")
        return nuevo_rubro_ref, "created"


    # --- FUNCIÓN MODIFICADA ---
    def crear_rubro(self, rubro: RubroModel) -> Tuple[RubroModel, str]:
        """
        Crea un nuevo rubro o lo reactiva. Usa el método transaccional decorado.
        """
        logger.info(f"Attempting to create/reactivate rubro with code: {rubro.codigo}")
        try:
            transaction = self.db.transaction()
            # CORRECCIÓN: Pasar solo 'rubro'. El decorador maneja 'transaction'.
            doc_ref, status_str = self._crear_rubro_atomic_transactional(transaction, rubro) # Pasar transaction explícitamente si se usa transaction.run() o quitarlo si se llama al decorado directamente

            # --- AJUSTE: Si se usa el decorador directamente, la llamada sería ---
            # doc_ref, status_str = self._crear_rubro_atomic_transactional(rubro=rubro)
            # --> ¡Probemos esta versión simplificada! <--
            # doc_ref, status_str = self._crear_rubro_atomic_transactional(rubro=rubro) # Comentar la línea con transaction.run()

            # Necesitamos re-pensar cómo llamar al decorado o usar transaction.run() correctamente
            # Usando transaction.run() explícitamente (más seguro):
            doc_ref, status_str = transaction.run(self._crear_rubro_atomic_transactional, rubro) # Pasar la función y el argumento adicional


            rubro_final_doc = doc_ref.get()
            if not rubro_final_doc.exists:
                 logger.error(f"CRITICAL: Document {doc_ref.id} not found post-transaction!")
                 raise HTTPException( status_code=500, detail="Error crítico: Documento no encontrado post-transacción.")
            logger.info(f"Rubro {doc_ref.id} successfully {status_str}.")
            # Usar model_validate_json si Firestore devuelve JSON, o model_validate si devuelve dict
            return RubroModel.model_validate(rubro_final_doc.to_dict()), status_str

        except HTTPException as http_exc:
            logger.warning(f"HTTPException during rubro creation/reactivation: {http_exc.status_code} - {http_exc.detail}")
            raise http_exc
        except Exception as e:
            logger.error(f"Transactional error creating/reactivating rubro: {e}", exc_info=True)
            # Devolver el TypeError específico si ocurre
            if isinstance(e, TypeError):
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"TypeError en transacción: {e}")
            raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error transaccional al crear rubro: {e}")
    # --- FIN FUNCIÓN MODIFICADA ---

    def obtener_rubro_por_id(self, id: str) -> RubroModel:
        # ... (código sin cambios, pero usa el modelo con alias) ...
        logger.info(f"Fetching rubro by ID: {id}")
        doc_ref = self.rubros_ref.document(id); doc = doc_ref.get()
        if not doc.exists: logger.warning(f"Rubro ID {id} not found."); raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado")
        logger.info(f"Rubro ID {id} found.")
        return RubroModel.model_validate(doc.to_dict())

    def obtener_rubro_por_codigo(self, codigo: str) -> RubroModel:
        # ... (código sin cambios, pero usa el modelo con alias) ...
        logger.info(f"Fetching rubro by code: {codigo}")
        # La consulta where sigue usando 'codigo' si ese es el alias o nombre en Firestore
        query = self.rubros_ref.where("codigo", "==", codigo).limit(1); resultados = list(query.stream())
        if not resultados: logger.warning(f"Rubro code {codigo} not found."); raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado")
        logger.info(f"Rubro code {codigo} found with ID: {resultados[0].id}")
        return RubroModel.model_validate(resultados[0].to_dict())

    def listar_rubros(self, activos: Optional[bool] = None) -> List[RubroModel]:
        # ... (código con logging detallado y validación individual sin cambios) ...
        logger.info(f"Listing rubros with filter activos={activos}")
        query = self.rubros_ref
        if activos is True: logger.info("Applying filter: baja_logica == False"); query = query.where("baja_logica", "==", False)
        elif activos is False: logger.info("Applying filter: baja_logica == True"); query = query.where("baja_logica", "==", True)
        else: logger.info("No filter applied (fetching all).")
        lista_rubros: List[RubroModel] = []
        try:
            docs = query.stream()
            logger.info("Firestore stream obtained. Iterating through documents...")
            doc_count = 0
            for doc in docs:
                doc_count += 1; doc_data = doc.to_dict(); doc_id = doc.id
                logger.info(f"  --> Processing doc ID: {doc_id}"); logger.info(f"      Data from Firestore (doc.to_dict()): {doc_data}")
                try:
                    rubro_model = RubroModel.model_validate(doc_data)
                    lista_rubros.append(rubro_model)
                except Exception as validation_error: logger.error(f"Pydantic validation failed for doc ID: {doc_id}, Data: {doc_data}", exc_info=True)
            logger.info(f"Firestore stream processed {doc_count} documents. Validation successful for {len(lista_rubros)} documents.")
            return lista_rubros
        except Exception as e:
            logger.error(f"Error streaming/processing documents from Firestore: {e}", exc_info=True)
            raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al listar rubros desde Firestore: {e}")

    def actualizar_rubro(self, id: str, rubro_update: RubroUpdateModel) -> RubroModel:
        # ... (código sin cambios, pero usa el modelo con alias) ...
        logger.info(f"Attempting to update rubro ID: {id} with data: {rubro_update}")
        doc_ref = self.rubros_ref.document(id); doc = doc_ref.get()
        if not doc.exists: logger.warning(f"Update failed: Rubro ID {id} not found."); raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado para actualizar")
        # Usar by_alias=False para obtener dict con nombres Pydantic ('nombre') para actualizar consistentemente
        update_data = rubro_update.model_dump(by_alias=False, exclude_defaults=True)
        if not update_data: logger.warning(f"Update aborted: No data provided for rubro ID {id}."); raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay datos para actualizar")
        if 'baja_logica' in rubro_update.model_fields_set: update_data['baja_logica'] = rubro_update.baja_logica
        logger.info(f"Applying update to {id}: {update_data}")
        doc_ref.update(update_data); doc_actualizado = doc_ref.get()
        logger.info(f"Rubro {id} updated successfully.")
        return RubroModel.model_validate(doc_actualizado.to_dict())

    def baja_logica_rubro(self, id: str) -> RubroModel:
        # ... (código sin cambios, pero usa el modelo con alias) ...
        logger.info(f"Attempting logical delete for rubro ID: {id}")
        doc_ref = self.rubros_ref.document(id); doc = doc_ref.get()
        if not doc.exists: logger.warning(f"Logical delete failed: Rubro ID {id} not found."); raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado")
        current_data = doc.to_dict()
        if current_data.get("baja_logica", False): logger.warning(f"Logical delete aborted: Rubro ID {id} already inactive."); raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rubro ya está dado de baja")
        doc_ref.update({"baja_logica": True}); doc_actualizado = doc_ref.get()
        logger.info(f"Rubro {id} marked as inactive.")
        return RubroModel.model_validate(doc_actualizado.to_dict())