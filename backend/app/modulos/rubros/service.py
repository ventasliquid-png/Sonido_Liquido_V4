# backend/app/modulos/rubros/service.py (VERSIÓN 10 - Saca la transacción de la clase)

from typing import List, Optional, Tuple
from fastapi import HTTPException, status # Necesario para lanzar errores HTTP
from google.cloud import firestore
# Importar referencias de tipo
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.transaction import Transaction
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.collection import CollectionReference
# --- INICIO: SOLUCIÓN HARCODED ---
# Importar el módulo para cargar credenciales desde un archivo
from google.oauth2 import service_account
# --- FIN: SOLUCIÓN HARCODED ---
from .models import RubroModel, RubroUpdateModel # Importación local correcta
import logging # Importar logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NO debe haber importación '.service' ni línea 'Depends' aquí.


# --- INICIO V10: FUNCIÓN HELPER TRANSACCIONAL (FUERA DE LA CLASE) ---
@firestore.transactional
def _transaccion_crear_rubro(
    transaction: Transaction, 
    rubro_data: dict, 
    rubros_ref: CollectionReference, 
    contadores_ref: CollectionReference
) -> Tuple[DocumentReference, str]:
    """
    Lógica transaccional AISLADA de la clase para evitar
    conflictos del decorador con 'self' y Pydantic.
    """
    
    # Convertimos el 'dict' de nuevo a 'RubroModel' DENTRO de la función.
    rubro = RubroModel.model_validate(rubro_data)
    
    logger.info(f"Transaction: Checking existence for code {rubro.codigo}")
    # Ya no usamos 'self.'
    query = rubros_ref.where("codigo", "==", rubro.codigo).limit(1)
    existentes = list(query.stream(transaction=transaction))

    if existentes:
        existente_doc = existentes[0]
        existente_ref = existente_doc.reference
        existente_data = existente_doc.to_dict()
        logger.info(f"Transaction: Found existing document {existente_ref.id} for code {rubro.codigo}")

        if existente_data.get("baja_logica"): # Si está inactivo
            logger.info(f"Transaction: Reactivating document {existente_ref.id}")
            transaction.update(existente_ref, {
                "baja_logica": False,
                "nombre": rubro.nombre # Actualizar nombre al reactivar
            })
            return existente_ref, "reactivated"
        else: # Si está activo
            logger.warning(f"Transaction: Conflict - Code {rubro.codigo} already active.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El código de rubro '{rubro.codigo}' ya existe y está activo."
            )

    # --- Creación Estándar ---
    logger.info(f"Transaction: Creating new document for code {rubro.codigo}")
    nuevo_rubro_ref = rubros_ref.document() # Ya no usamos 'self.'
    # Preparar datos, asegurando campos obligatorios
    nuevo_data = rubro.model_dump(exclude={"id"}) # Excluir ID si vino del payload
    nuevo_data["id"] = nuevo_rubro_ref.id # Usar el ID generado por Firestore
    nuevo_data["baja_logica"] = nuevo_data.get("baja_logica", False) # Asegurar valor False por defecto

    transaction.set(nuevo_rubro_ref, nuevo_data) # Guardar rubro
    logger.info(f"Transaction: Rubro document {nuevo_rubro_ref.id} set.")

    # Crear contador asociado
    nuevo_contador_ref = contadores_ref.document(nuevo_rubro_ref.id) # Ya no usamos 'self.'
    datos_nuevo_contador = {'ultimo_valor': 0}
    transaction.set(nuevo_contador_ref, datos_nuevo_contador) # Guardar contador
    logger.info(f"Transaction: Counter document {nuevo_contador_ref.id} set.")

    return nuevo_rubro_ref, "created"
# --- FIN V10: FUNCIÓN HELPER ---


class RubroService:
    """
    Capa de lógica de negocio para gestionar Rubros.
    Interactúa directamente con la base de datos Firestore.
    Implementa la "Doctrina de Contadores" atómica.
    """

    def __init__(self):
        """Inicializa el cliente de Firestore y la referencia a las colecciones."""
        try:
            
            # --- INICIO: SOLUCIACIÓN HARCODED ---
            # 1. Definir la ruta absoluta al archivo JSON
            #    (Usamos '/' para compatibilidad en Python)
            ruta_llave_absoluta = "C:/dev/Sonido_Liquido_V4/service-account-v4.json"

            # 2. Cargar las credenciales desde ese archivo
            credentials = service_account.Credentials.from_service_account_file(ruta_llave_absoluta)

            # 3. Pasar las credenciales explícitamente al cliente
            self.db: Client = firestore.Client(credentials=credentials)
            # --- FIN: SOLUCIACIÓN HARCODED ---
            
            self.rubros_ref = self.db.collection("rubros")
            self.contadores_ref = self.db.collection("counters") # Nombre correcto
            logger.info("Firestore client and collections initialized.")
        except Exception as e:
            logger.error(f"Error al inicializar Firestore: {e}", exc_info=True)
            # Este RuntimeError será capturado por get_rubro_service en router.py
            raise RuntimeError(f"Error al inicializar Firestore: {e}")

    # (Se elimina la función _crear_rubro_atomic_transactional de aquí)

    def crear_rubro(self, rubro: RubroModel) -> Tuple[RubroModel, str]:
        """
        Crea un nuevo rubro o lo reactiva si existe y está en baja_logica.
        """
        logger.info(f"Attempting to create/reactivate rubro with code: {rubro.codigo}")
        try:
            # --- INICIO: CORRECCIÓN TRANSACCIÓN (V10) ---
            
            # 1. Convertimos el modelo Pydantic a 'dict' ANTES de la llamada.
            rubro_data = rubro.model_dump()

            # 2. Creamos un objeto de transacción desde nuestro cliente de BD
            transaction = self.db.transaction()

            # 3. Llamamos a la función helper (externa)
            doc_ref, status_str = _transaccion_crear_rubro(
                transaction,        # El objeto de transacción
                rubro_data,         # Los datos
                self.rubros_ref,    # La referencia a la colección de rubros
                self.contadores_ref # La referencia a la colección de contadores
            )
            # --- FIN: CORRECCIÓN TRANSACCIÓN (V10) ---

            rubro_final_doc = doc_ref.get() # Obtener el doc después de la transacción
            if not rubro_final_doc.exists:
                 logger.error(f"CRITICAL: Document {doc_ref.id} not found post-transaction!")
                 raise HTTPException( status_code=500, detail="Error crítico: Documento no encontrado post-transacción.")

            logger.info(f"Rubro {doc_ref.id} successfully {status_str}.")
            # Usar model_validate para Pydantic v2
            return RubroModel.model_validate(rubro_final_doc.to_dict()), status_str

        except HTTPException as http_exc: # Capturar 409 u otros errores HTTP
            logger.warning(f"HTTPException during rubro creation/reactivation: {http_exc.status_code} - {http_exc.detail}")
            raise http_exc
        except Exception as e: # Capturar otros errores (conexión, etc.)
            logger.error(f"Transactional error creating/reactivating rubro: {e}", exc_info=True)
            raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error transaccional al crear rubro: {e}")

    def obtener_rubro_por_id(self, id: str) -> RubroModel:
        """Obtiene un rubro por su ID de Firestore."""
        logger.info(f"Fetching rubro by ID: {id}")
        doc_ref = self.rubros_ref.document(id)
        doc = doc_ref.get()
        if not doc.exists:
            logger.warning(f"Rubro ID {id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado")
        logger.info(f"Rubro ID {id} found.")
        return RubroModel.model_validate(doc.to_dict())

    def obtener_rubro_por_codigo(self, codigo: str) -> RubroModel:
        """Obtiene un rubro por su 'codigo' de negocio."""
        logger.info(f"Fetching rubro by code: {codigo}")
        # Firestore necesita índice para consultas !=
        query = self.rubros_ref.where("codigo", "==", codigo).limit(1)
        resultados = list(query.stream())
        if not resultados:
            logger.warning(f"Rubro code {codigo} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado")
        logger.info(f"Rubro code {codigo} found with ID: {resultados[0].id}")
        return RubroModel.model_validate(resultados[0].to_dict())

    def listar_rubros(self, activos: Optional[bool] = None) -> List[RubroModel]:
        """ Lista rubros desde Firestore, opcionalmente filtrados por estado. """
        logger.info(f"Listing rubros with filter activos={activos}")
        query = self.rubros_ref # Empezar con la referencia a la colección

        # Aplicar filtro si se especificó 'activos'
        if activos is True:
            logger.info("Applying filter: baja_logica == False")
            # Firestore necesita índice para consultas where
            query = query.where("baja_logica", "==", False)
        elif activos is False:
            logger.info("Applying filter: baja_logica == True")
            # Firestore necesita índice para consultas where
            query = query.where("baja_logica", "==", True)
        else:
             logger.info("No filter applied (fetching all).")

        # Opcional: Añadir ordenamiento si se desea
        # query = query.order_by("nombre", direction=firestore.Query.ASCENDING)

        try:
            docs = query.stream() # Ejecutar la consulta
            lista_rubros = []
            for doc in docs:
                try:
                    # Validar cada documento con Pydantic
                    rubro_model = RubroModel.model_validate(doc.to_dict())
                    lista_rubros.append(rubro_model)
                except Exception as validation_error:
                    logger.error(f"Validation error for doc ID {doc.id}: {validation_error}", exc_info=False)
                    # Decidir si saltar el documento inválido o lanzar un error mayor
            logger.info(f"Firestore stream processed. Returning {len(lista_rubros)} valid documents.")
            return lista_rubros
        except Exception as e: # Capturar errores de Firestore al hacer stream
            logger.error(f"Error streaming documents from Firestore: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al listar rubros desde Firestore: {e}"
            )

    def actualizar_rubro(self, id: str, rubro_update: RubroUpdateModel) -> RubroModel:
        """ Actualiza parcialmente un rubro (PATCH) en Firestore. """
        logger.info(f"Attempting to update rubro ID: {id} with data: {rubro_update}")
        doc_ref = self.rubros_ref.document(id)

        # Añadir log extra antes del get()
        logger.info(f"Fetching document with ID '{id}' before update...")
        doc = doc_get() # Leer el documento existente
        if not doc.exists:
            logger.warning(f"Update failed: Rubro ID {id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado para actualizar")

        # Preparar datos para actualizar, excluyendo valores no enviados (None)
        # y asegurando que 'baja_logica: False' se envíe si está presente
        update_data = rubro_update.model_dump(exclude_unset=True) # exclude_unset es bueno para PATCH

        if not update_data:
             logger.warning(f"Update aborted: No data provided for rubro ID {id}.")
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay datos para actualizar")

        # Asegurar que baja_logica se guarde si viene en el payload (incluso si es False)
        if 'baja_logica' in update_data:
             pass

        logger.info(f"Applying update to {id}: {update_data}")
        doc_ref.update(update_data) # Aplicar cambios

        doc_actualizado = doc_ref.get() # Releer para obtener estado final
        logger.info(f"Rubro {id} updated successfully.")
        return RubroModel.model_validate(doc_actualizado.to_dict())

    def baja_logica_rubro(self, id: str) -> RubroModel:
        """ Realiza baja lógica (setea baja_logica = True). """
        logger.info(f"Attempting logical delete for rubro ID: {id}")
        doc_ref = self.rubros_ref.document(id)

        doc = doc_ref.get()
        if not doc.exists:
            logger.warning(f"Logical delete failed: Rubro ID {id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubro no encontrado")

        current_data = doc.to_dict()
        # Verificar si ya está inactivo (usando .get con default False)
        if current_data.get("baja_logica", False):
            logger.warning(f"Logical delete aborted: Rubro ID {id} already inactive.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El rubro ya está dado de baja")

        # Actualizar solo el campo baja_logica a True
        doc_ref.update({"baja_logica": True})

        doc_actualizado = doc_ref.get() # Releer para confirmar
        logger.info(f"Rubro {id} marked as inactive.")
        return RubroModel.model_validate(doc_actualizado.to_dict())