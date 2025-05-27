from fhir.resources.patient import Patient
import json

# Las importaciones de pymongo y connect_to_mongodb no son necesarias para la validación FHIR
# y se eliminan para mantener el script enfocado en su propósito.


# Este script se enfoca en la validación de un JSON contra el modelo FHIR Patient.
# No necesita funciones de base de datos aquí.

# Ejemplo de uso
if __name__ == "__main__":
    # JSON string correspondiente al artefacto Patient de HL7 FHIR.
    # IMPORTANTE: La estructura del 'identifier' se ha actualizado para coincidir
    # con el formato que tu frontend (app.js) genera y tu backend (PatientCrud.py) espera.
    patient_json = '''
    {
      "resourceType": "Patient",
      "id": "PacienteValidacionTest",  
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
          "value": "1020713756"
        },
        {
          "use": "usual",
          "type": {
            "coding": [
              {
                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                "code": "PPN"
              }
            ],
            "text": "Pasaporte"
          },
          "value": "AQ123456789"
        }
      ],
      "name": [
        {
          "use": "official",
          "text": "Mario Enrique Duarte",
          "family": "Duarte",
          "given": [
            "Mario",
            "Enrique"
          ]
        }
      ],
      "telecom": [
        {
          "system": "phone",
          "value": "3142279487",
          "use": "mobile"
        },
        {
          "system": "email",
          "value": "mardugo@gmail.com",
          "use": "home"
        }
      ],
      "gender": "male",
      "birthDate": "1986-02-25",
      "address": [
        {
          "use": "home",
          "line": [
            "Cra 55A # 167A - 30"
          ],
          "city": "Bogotá",
          "state": "Cundinamarca",
          "postalCode": "11156",
          "country": "COL"
        }
      ]
    }
    '''

    try:
        # Cargar el JSON string a un diccionario de Python
        patient_data_dict = json.loads(patient_json)
        
        # Validar el diccionario contra el modelo FHIR Patient
        pat = Patient.model_validate(patient_data_dict)
        
        print("--- Validación Exitosa ---")
        print("El JSON del paciente es un recurso FHIR Patient válido.")
        print("\n--- Datos del Paciente Validado (model_dump) ---")
        # Imprimir el diccionario del modelo validado (que puede incluir campos por defecto)
        print(json.dumps(pat.model_dump(by_alias=True, exclude_unset=True), indent=2))

    except json.JSONDecodeError as e:
        print(f"ERROR: El JSON proporcionado es inválido. Detalles: {e}")
    except Exception as e:
        print(f"ERROR: Falló la validación del paciente contra el modelo FHIR Patient. Detalles: {e}")
        print("\n--- JSON Original que intentó validar ---")
        print(patient_json)

