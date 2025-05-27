# oldFiles/readPatient.py

# Importar la función de conexión desde tu archivo connection.py
# Asumiendo que connection.py está en el mismo nivel que la carpeta 'app' o en un nivel superior accesible.
from connection import connect_to_mongodb
from pymongo.errors import PyMongoError # Para un manejo de errores más específico de PyMongo
from bson.objectid import ObjectId # Para convertir el _id de MongoDB a string para mostrar
import json # Para imprimir el JSON de forma legible

# --- La función original 'connect_to_mongodb' se elimina de aquí ---
# --- porque ahora la importamos desde connection.py ---

# Función para leer todos los pacientes de la colección
def read_patients_from_mongodb(collection):
    """
    Lee todos los documentos de paciente de la colección de MongoDB.

    Args:
        collection: El objeto de la colección de MongoDB.

    Returns:
        list or None: Una lista de diccionarios de pacientes (con _id como string),
                      o None si ocurre un error.
    """
    try:
        # Consultar todos los documentos en la colección
        patients_cursor = collection.find()
        
        # Convertir los documentos a una lista de diccionarios
        patient_list = []
        for patient in patients_cursor:
            # Convertir el ObjectId de MongoDB a string para que sea serializable a JSON
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

# Función para mostrar los datos de los pacientes
def display_patients(patient_list):
    """
    Muestra los datos formateados de una lista de pacientes a partir de recursos FHIR Patient.
    """
    if patient_list:
        print(f"\n--- Se encontraron {len(patient_list)} paciente(s) ---")
        for i, patient in enumerate(patient_list):
            print(f"\n--- Paciente {i + 1} ---")
            print(f"  ID de MongoDB: {patient.get('_id', 'N/A')}")
            print(f"  ID FHIR: {patient.get('id', 'N/A')}") # Mostrar el ID FHIR del recurso
            
            # Extraer y mostrar el nombre
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

            # Mostrar información de contacto (telecom)
            telecoms = patient.get('telecom', [])
            if telecoms:
                print("  Información de Contacto:")
                for tc in telecoms:
                    system = tc.get('system', 'N/A')
                    value = tc.get('value', 'N/A')
                    use = tc.get('use', 'N/A')
                    print(f"    {system.capitalize()}: {value} (Uso: {use})")

            # Mostrar información de dirección
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

# Ejemplo de uso (se ejecuta solo cuando el script es el principal)
if __name__ == "__main__":
    # Cadena de conexión a MongoDB (se usa la URI interna de connection.py)
    # Ya no se pasa la URI directamente aquí, ya que connect_to_mongodb la tiene internamente.
    
    db_name = "SamplePatientService"
    collection_name = "patients"

    # Conectar a MongoDB usando la función de connection.py
    # La función connect_to_mongodb ahora retorna None si hay un error.
    collection = connect_to_mongodb(db_name, collection_name)
    
    if collection is None:
        print("ERROR: No se pudo establecer la conexión a MongoDB. No se puede leer pacientes.")
    else:
        print("\nLeyendo todos los pacientes de la base de datos...")
        # Leer los pacientes de la colección
        patients = read_patients_from_mongodb(collection)
        
        # Mostrar los datos de los pacientes
        display_patients(patients)
