from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from typing import Optional, Dict, Any, List, Tuple
from datetime import date
from connection import get_db # Importamos la función de conexión a la base de datos
from bson import ObjectId # Necesario para trabajar con los _id de MongoDB
from fhir.resources.patient import Patient as FHIRPatient # Renombrado para evitar conflicto
from pydantic import ValidationError # Para capturar errores de validación de Pydantic/FHIR

class PatientCrud:
    def __init__(self):
        # La conexión a la base de datos se obtiene a través de get_db()
        # Esto asegura que se usa la misma instancia de DB que en app.py
        self.db = get_db()
        if self.db is None:
            raise Exception("No se pudo establecer conexión a la base de datos MongoDB.")
        # Aseguramos que la colección sea 'patients' en la DB 'LIS'
        self.patients_collection = self.db.patients 

    def create_or_update_patient_fhir_resource(self, patient_dict: dict) -> Tuple[str, Optional[str]]:
        """
        Valida un diccionario como un recurso FHIR Patient y lo inserta o actualiza
        en la colección 'patients' de MongoDB.
        Utiliza los identificadores FHIR (system y value) o el 'id' de FHIR para buscar y hacer upsert.
        
        Retorna: ("success", _id_mongo_str) si es exitoso, 
                 ("errorValidating", error_message) si falla la validación,
                 ("errorInserting", error_message) si falla la inserción/actualización.
        """
        try:
            # 1. Validar el diccionario como un recurso FHIR Patient
            pat = FHIRPatient.model_validate(patient_dict)
            validated_patient_data = pat.model_dump(exclude_unset=True, exclude_none=True)
            
        except ValidationError as e:
            print(f"Error de validación FHIR: {e}")
            return "errorValidating", str(e)
        except Exception as e:
            print(f"Error inesperado durante la validación FHIR: {e}")
            return "errorValidating", f"Error inesperado: {str(e)}"

        try:
            # 2. Construir la query para el upsert
            # Priorizamos el 'id' de FHIR si está presente, luego los 'identifier'
            mongo_query = {}
            if 'id' in validated_patient_data and validated_patient_data['id']:
                # Si el recurso FHIR ya tiene un 'id' asignado por el servicio FHIR externo,
                # lo usamos como el criterio principal de búsqueda para nuestro almacenamiento local.
                # Esto asume que el 'id' del servicio FHIR es único y persistente.
                mongo_query = {"id": validated_patient_data['id']}
            elif 'identifier' in validated_patient_data and isinstance(validated_patient_data['identifier'], list):
                # Si no hay 'id' de FHIR, usamos los 'identifier' (system y value)
                query_identifiers = []
                for identifier in validated_patient_data['identifier']:
                    if 'system' in identifier and 'value' in identifier:
                        query_identifiers.append({
                            "identifier.system": identifier['system'],
                            "identifier.value": identifier['value']
                        })
                if query_identifiers:
                    if len(query_identifiers) == 1:
                        mongo_query = query_identifiers[0]
                    else:
                        mongo_query = {"$or": query_identifiers}
            
            if not mongo_query:
                return "errorInserting", "El recurso FHIR Patient no contiene 'id' ni 'identifier' válidos para upsert."

            # 3. Realizar la operación de upsert (insertar o actualizar)
            result: UpdateResult = self.patients_collection.update_one(
                mongo_query,
                {"$set": validated_patient_data},
                upsert=True
            )
            
            if result.upserted_id:
                print(f"Paciente FHIR insertado con _id: {result.upserted_id}")
                return "success", str(result.upserted_id)
            elif result.matched_count > 0:
                print(f"Paciente FHIR actualizado basado en query: {mongo_query}")
                # Recuperar el _id del documento actualizado
                existing_patient = self.patients_collection.find_one(mongo_query, {"_id": 1})
                return "success", str(existing_patient["_id"]) if existing_patient else None
            else:
                return "errorInserting", "No se insertó ni actualizó el paciente FHIR (posiblemente no hubo cambios)."

        except PyMongoError as e:
            print(f"Error de PyMongo al insertar/actualizar paciente FHIR en MongoDB: {e}")
            return "errorInserting", str(e)
        except Exception as e:
            print(f"Error inesperado al insertar/actualizar paciente FHIR en MongoDB: {e}")
            return "errorInserting", str(e)

    def get_patient_by_object_id(self, object_id: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Obtiene un paciente de la colección 'patients' por su ObjectId de MongoDB.
        Retorna: ("success", patient_dict) si encontrado, ("notFound", None) si no,
                 ("error", error_message) si hay un error.
        """
        try:
            patient = self.patients_collection.find_one({"_id": ObjectId(object_id)})
            if patient:
                patient["_id"] = str(patient["_id"]) # Convertir ObjectId a string para JSON
                return "success", patient
            return "notFound", None
        except Exception as e:
            print(f"Error al obtener paciente por ObjectId: {e}")
            return "error", str(e)

    def get_patient_by_fhir_identifier(self, system: str, value: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Obtiene un paciente de la colección 'patients' por su identificador FHIR (system y value).
        Retorna: ("success", patient_dict) si encontrado, ("notFound", None) si no,
                 ("error", error_message) si hay un error.
        """
        try:
            query = {
                "identifier": {
                    "$elemMatch": {
                        "system": system,
                        "value": value
                    }
                }
            }
            patient = self.patients_collection.find_one(query)
            if patient:
                patient["_id"] = str(patient["_id"])
                return "success", patient
            return "notFound", None
        except Exception as e:
            print(f"Error al obtener paciente por identificador FHIR: {e}")
            return "error", str(e)
            
    def get_patient_by_fhir_id_field(self, fhir_id: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Obtiene un paciente de la colección 'patients' por el campo 'id' de su recurso FHIR.
        Retorna: ("success", patient_dict) si encontrado, ("notFound", None) si no,
                 ("error", error_message) si hay un error.
        """
        try:
            patient = self.patients_collection.find_one({"id": fhir_id})
            if patient:
                patient["_id"] = str(patient["_id"])
                return "success", patient
            return "notFound", None
        except Exception as e:
            print(f"Error al obtener paciente por ID de FHIR: {e}")
            return "error", str(e)

    def delete_patient(self, object_id: str) -> Tuple[str, Optional[str]]:
        """
        Elimina un paciente de la colección 'patients' por su ObjectId de MongoDB.
        Retorna: ("success", "message") si eliminado, ("notFound", None) si no encontrado,
                 ("error", error_message) si hay un error.
        """
        try:
            result: DeleteResult = self.patients_collection.delete_one({"_id": ObjectId(object_id)})
            if result.deleted_count > 0:
                return "success", "Paciente eliminado exitosamente."
            return "notFound", None
        except Exception as e:
            print(f"Error al eliminar paciente: {e}")
            return "error", str(e)

    def get_all_patients(self) -> List[Dict[str, Any]]:
        """
        Recupera todos los pacientes de la base de datos.
        """
        try:
            patients = []
            for doc in self.patients_collection.find():
                doc["_id"] = str(doc["_id"]) # Convertir ObjectId a string para JSON
                patients.append(doc)
            return patients
        except Exception as e:
            print(f"Error al obtener todos los pacientes: {e}")
            return []
