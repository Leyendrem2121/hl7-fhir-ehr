# oldFiles/readPatient.py

from connection import get_db
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
import json

def read_patients_from_mongodb(collection):
    """
    Lee todos los documentos de paciente de la colección de MongoDB.
    """
    try:
        patients_cursor = collection.find()
        patient_list = []
        for patient in patients_cursor:
            if '_id' in patient and isinstance(patient['_id'], ObjectId):
                patient['_id'] = str(patient['_id'])
            patient_list.append(patient)
        return patient_list
    except PyMongoError as e:
        print(f"Error al leer desde MongoDB (PyMongoError): {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al leer desde MongoDB: {e}")
        return None

def display_patients(patient_list):
    """
    Muestra los datos formateados de una lista de pacientes a partir de recursos FHIR Patient.
    """
    if patient_list:
        print(f"\n--- Se encontraron {len(patient_list)} paciente(s) ---")
        for i, patient in enumerate(patient_list):
            print(f"\n--- Paciente {i + 1} ---")
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
            print("-" * 30)
    else:
        print("No se encontraron pacientes en la base de datos.")

if __name__ == "__main__":
    db = get_db()

    if db is None:
        print("ERROR: No se pudo establecer la conexión a MongoDB. No se puede leer pacientes.")
    else:
        collection = db["patients"]
        
        print("\nLeyendo todos los pacientes de la base de datos...")
        patients = read_patients_from_mongodb(collection)
        display_patients(patients)
