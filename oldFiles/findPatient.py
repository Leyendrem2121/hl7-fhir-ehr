# oldFiles/findPatient.py

from connection import get_db
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId

def find_patient_by_identifier(collection, identifier_system_code: str, identifier_value: str):
    """
    Busca un paciente en la colección de MongoDB por un identificador FHIR específico.
    """
    try:
        if '|' not in identifier_system_code:
            print(f"Error: El formato de 'identifier_system_code' '{identifier_system_code}' no es 'system|code'.")
            return None
        
        system, code = identifier_system_code.split('|', 1)

        query = {
            "identifier": {
                "$elemMatch": {
                    "type.coding": {
                        "$elemMatch": {
                            "system": system,
                            "code": code
                        }
                    },
                    "value": identifier_value
                }
            }
        }

        patient = collection.find_one(query)
        
        if patient and '_id' in patient and isinstance(patient['_id'], ObjectId):
            patient['_id'] = str(patient['_id'])
            
        return patient
    except PyMongoError as e:
        print(f"Error al buscar en MongoDB (PyMongoError): {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al buscar en MongoDB: {e}")
        return None

def display_patient(patient):
    """
    Muestra los datos formateados de un paciente a partir de un recurso FHIR Patient.
    """
    if patient:
        print("\n--- Paciente encontrado ---")
        print(f"  ID de MongoDB: {patient.get('_id', 'N/A')}")
        print(f"  ID FHIR: {patient.get('id', 'N/A')}")
        
        names = patient.get('name', [])
        if names:
            official_name = next((n for n in names if n.get('use') == 'official'), names[0] if names else {})
            given_name = official_name.get('given', [''])[0] if official_name.get('given') else ''
            family_name = official_name.get('family', '')
            print(f"  Nombre Completo: {given_name} {family_name}".strip())
        else:
            print("  Nombre: No disponible")

        print(f"  Género: {patient.get('gender', 'Desconocido')}")
        print(f"  Fecha de Nacimiento: {patient.get('birthDate', 'Desconocida')}")
        
        print("  Identificadores:")
        identifiers = patient.get("identifier", [])
        if identifiers:
            for identifier in identifiers:
                id_type_coding = identifier.get('type', {}).get('coding', [])
                id_type_text = identifier.get('type', {}).get('text', 'N/A')
                id_system = id_type_coding[0].get('system') if id_type_coding else 'N/A'
                id_code = id_type_coding[0].get('code') if id_type_coding else 'N/A'
                id_value = identifier.get('value')
                print(f"    Tipo: {id_type_text} (System: {id_system}, Code: {id_code}), Valor: {id_value}")
        else:
            print("    No se encontraron identificadores.")

        telecoms = patient.get('telecom', [])
        if telecoms:
            print("  Información de Contacto:")
            for tc in telecoms:
                system = tc.get('system', 'N/A')
                value = tc.get('value', 'N/A')
                use = tc.get('use', 'N/A')
                print(f"    {system.capitalize()}: {value} (Uso: {use})")

        addresses = patient.get('address', [])
        if addresses:
            print("  Dirección:")
            for addr in addresses:
                line = addr.get('line', [])
                city = addr.get('city', 'N/A')
                state = addr.get('state', 'N/A')
                postal_code = addr.get('postalCode', 'N/A')
                country = addr.get('country', 'N/A')
                print(f"    Línea(s): {', '.join(line)}")
                print(f"    Ciudad: {city}, Estado: {state}, CP: {postal_code}, País: {country}")
    else:
        print("No se encontró ningún paciente con el identificador especificado.")

if __name__ == "__main__":
    db = get_db()
uri = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    if db is None:
        print("ERROR: No se pudo establecer la conexión a MongoDB. No se puede buscar pacientes.")
    else:
        collection = db["patients"]

        identifier_to_search_type = "http://terminology.hl7.org/CodeSystem/v2-0203|ID"
        identifier_to_search_value = "1234567890"  # Cambia este valor según tu base de datos

        print(f"\nBuscando paciente con Tipo de ID '{identifier_to_search_type}' y Valor '{identifier_to_search_value}'...")
        patient_found = find_patient_by_identifier(collection, identifier_to_search_type, identifier_to_search_value)
        
        display_patient(patient_found)

