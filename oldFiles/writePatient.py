# oldFiles/writePatient.py

# Importar la función get_db desde tu archivo connection.py
from connection import get_db
from pymongo.errors import PyMongoError
from fhir.resources.patient import Patient
import json

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
    if collection is None:
        print("Error: La conexión a la base de datos no está establecida. No se puede guardar el paciente.")
        return None

    try:
        pat = Patient.model_validate(patient_data_dict)
    except Exception as e:
        print(f"Error de validación FHIR para el paciente: {e}")
        return None

    try:
        validated_patient_for_db = pat.model_dump(by_alias=True, exclude_unset=True)
        result = collection.insert_one(validated_patient_for_db)

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

if __name__ == "__main__":
    # Usar get_db para obtener la base de datos
    db = get_db()

    if db is None:
        print("ERROR: No se pudo establecer la conexión a MongoDB. No se puede guardar el paciente.")
    else:
        # Obtener la colección 'patients' explícitamente
        collection = db["patients"]

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

