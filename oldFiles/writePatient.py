# oldFiles/writePatient.py

# Importar la función de conexión desde tu archivo connection.py
# Asumiendo que connection.py está en un nivel accesible para este script.
from connection import connect_to_mongodb
from pymongo.errors import PyMongoError # Para un manejo de errores más específico de PyMongo
from fhir.resources.patient import Patient # Para la validación del modelo FHIR Patient
import json # Necesario para parsear el JSON de ejemplo y para imprimir legiblemente

# --- La función original 'connect_to_mongodb' se elimina de aquí ---
# --- porque ahora la importamos desde connection.py ---

# Función para guardar el diccionario del paciente en MongoDB
def save_patient_to_mongodb(patient_data_dict: dict, collection):
    """
    Valida un diccionario de datos de paciente contra el modelo FHIR Patient
    y lo guarda en una colección de MongoDB.

    Args:
        patient_data_dict (dict): El diccionario de datos del paciente (esperado en formato FHIR).
        collection: El objeto de la colección de MongoDB.

    Returns:
        str or None: El ID del documento insertado como string si tiene éxito,
                     o None si ocurre un error (validación o inserción).
    """
    # Verifica si la colección está disponible (si la conexión fue exitosa)
    if collection is None:
        print("Error: La conexión a la base de datos no está establecida. No se puede guardar el paciente.")
        return None

    try:
        # 1. Validar el diccionario contra el modelo FHIR Patient
        # Esto asegura que los datos cumplen con la estructura FHIR
        pat = Patient.model_validate(patient_data_dict)
    except Exception as e:
        print(f"Error de validación FHIR para el paciente: {e}")
        return None # Retorna None si la validación falla

    try:
        # 2. Convertir el objeto FHIR validado de nuevo a un diccionario
        # 'by_alias=True' asegura que los nombres de los campos FHIR (ej. 'resourceType')
        # se usen tal cual en la DB. 'exclude_unset=True' excluye campos que no fueron provistos.
        validated_patient_for_db = pat.model_dump(by_alias=True, exclude_unset=True)

        # 3. Insertar el documento validado en la colección
        result = collection.insert_one(validated_patient_for_db)

        # 4. Retornar el ID del documento insertado por MongoDB como string
        if result.inserted_id:
            return str(result.inserted_id)
        else:
            print("No se obtuvo un ID de inserción después de guardar el paciente.")
            return None
    except PyMongoError as e:
        print(f"Error de PyMongo al insertar paciente: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al insertar paciente: {e}")
        return None


# Ejemplo de uso (se ejecuta solo cuando el script es el principal)
if __name__ == "__main__":
    # Cadena de conexión a MongoDB (se usa la URI interna de connection.py)
    uri = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=SamplePatientService"
    # Ya no se pasa la URI directamente aquí, ya que connect_to_mongodb la tiene internamente.
    
    db_name = "SamplePatientService"
    collection_name = "patients"

    # Conectar a MongoDB usando la función de connection.py
    # La función connect_to_mongodb ahora retorna None si hay un error.
    collection = connect_to_mongodb(db_name, collection_name)
    
    if collection is None:
        print("ERROR: No se pudo establecer la conexión a MongoDB. No se puede guardar el paciente.")
    else:
        # JSON string correspondiente al artefacto Patient de HL7 FHIR.
        # IMPORTANTE: La estructura del 'identifier' se ha actualizado para coincidir
        # con el formato que tu frontend (app.js) genera y tu backend (PatientCrud.py) espera.
        patient_json_example = '''
        {
          "resourceType": "Patient",
          "id": "PacienteEjemploWriteOld",
          "identifier": [
            {
              "use": "official",
              "type": {
                "coding": [
                  {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "code": "ID"
                  }
                ],
                "text": "Cédula de Ciudadanía"
              },
              "value": "1000000001"
            }
          ],
          "name": [
            {
              "use": "official",
              "family": "Pérez",
              "given": [
                "Carlos",
                "Alberto"
              ]
            }
          ],
          "telecom": [
            {
              "system": "phone",
              "value": "3201112233",
              "use": "mobile"
            },
            {
              "system": "email",
              "value": "carlos.perez@example.com",
              "use": "home"
            }
          ],
          "gender": "male",
          "birthDate": "1975-01-15",
          "address": [
            {
              "use": "home",
              "line": [
                "Calle 1 # 2-3"
              ],
              "city": "Cali",
              "state": "Valle del Cauca",
              "postalCode": "760001",
              "country": "COL"
            }
          ]
        }
        '''
        
        try:
            # Convertir el JSON string a un diccionario de Python
            patient_data_dict = json.loads(patient_json_example)
            
            print("\nIntentando guardar el paciente de ejemplo...")
            inserted_id = save_patient_to_mongodb(patient_data_dict, collection)

            if inserted_id:
                print(f"Paciente de ejemplo guardado con ID: {inserted_id}")
            else:
                print("No se pudo guardar el paciente de ejemplo.")
        except json.JSONDecodeError as e:
            print(f"ERROR: El JSON de ejemplo es inválido. Detalles: {e}")
        except Exception as e:
            print(f"ERROR: Ocurrió un error inesperado al procesar el JSON de ejemplo: {e}")
