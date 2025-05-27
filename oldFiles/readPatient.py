import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId # Required to convert ObjectId to string for display
from pymongo.errors import PyMongoError # Import for specific MongoDB error handling

# Importamos la función de conexión a la base de datos que ya tenemos en 'connection.py'
# Esto asegura que usamos la misma lógica de conexión en todo el backend.
from connection import get_db

# Nota: La función 'connect_to_mongodb' que estaba en tu fragmento original
# ya no es necesaria aquí si usamos 'get_db()' de 'connection.py'
# para obtener la base de datos y luego acceder a la colección.
# Sin embargo, si este script fuera a ser ejecutado de forma independiente
# sin depender de 'connection.py', tu función original sería útil.
# Para mantener la consistencia con el resto del backend, usaremos get_db().

# Función para leer todos los pacientes de la colección
def read_patients_from_mongodb(collection):
    """
    Lee todos los documentos de paciente de la colección de MongoDB.
    Convierte los ObjectIds a strings para facilitar la visualización.
    Maneja errores específicos de PyMongo.
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
            print(f"  ID FHIR: {patient.get('id', 'N/A')}") # ID FHIR si el recurso lo tiene
            
            names = patient.get('name', [])
            if names:
                # Buscar el nombre oficial si existe, de lo contrario usar el primero
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
                    # Acceder de forma segura a los componentes del tipo de identificador FHIR
                    id_type_coding = identifier.get('type', {}).get('coding', [])
                    id_type_text = identifier.get('type', {}).get('text', 'N/A')
                    # Asumiendo que el primer coding es el relevante para system/code
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
        print("--- Fin del Listado ---")
    else:
        print("No se encontraron pacientes en la base de datos.")

# Ejemplo de uso
if __name__ == "__main__":
    # La URI de conexión y el nombre de la base de datos se obtienen de 'connection.py'
    uri = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # a través de la función get_db().
    # Aquí, solo necesitamos especificar la colección.
    
    db = get_db() # Obtener el objeto de la base de datos

    if db is None:
        print("ERROR: No se pudo establecer la conexión a MongoDB. No se puede leer pacientes.")
    else:
        collection = db["patients"] # Acceder a la colección 'patients'
        
        print("\nLeyendo todos los pacientes de la base de datos...")
        patients = read_patients_from_mongodb(collection)
        display_patients(patients)
