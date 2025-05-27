from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Función para conectar a la base de datos MongoDB
def connect_to_mongodb(uri, db_name, collection_name):
    """
    Establece una conexión con una colección específica en MongoDB.
    """
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client[db_name]
        collection = db[collection_name]
        print(f"Conexión a MongoDB a la colección '{collection_name}' en DB '{db_name}' establecida con éxito!")
        return collection
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None

# Función para buscar pacientes por un identifier específico (ajustado a 'system' en lugar de 'type')
def find_patient_by_identifier(collection, identifier_system, identifier_value):
    """
    Busca un documento paciente en la colección que coincida con el sistema y valor de un identificador.
    """
    try:
        query = {
            "identifier": {
                "$elemMatch": {
                    "system": identifier_system, # <-- CAMBIO CLAVE: de "type" a "system"
                    "value": identifier_value
                }
            }
        }
        patient = collection.find_one(query)
        return patient
    except Exception as e:
        print(f"Error al buscar en MongoDB: {e}")
        return None

# Función para mostrar los datos de un paciente
def display_patient(patient):
    """
    Imprime de forma legible los datos de un paciente.
    """
    if patient:
        print("\n--- Paciente encontrado ---")
        print(f"  ID de MongoDB: {patient.get('_id')}")
        
        # Acceder de forma segura a nombre y apellido
        names = patient.get('name', [{}])
        given_name = names[0].get('given', [''])[0] if names else ''
        family_name = names[0].get('family', '') if names else ''
        print(f"  Nombre: {given_name} {family_name}")
        
        print(f"  Género: {patient.get('gender', 'Desconocido')}")
        print(f"  Fecha de nacimiento: {patient.get('birthDate', 'Desconocida')}")
        
        print("  Identificadores:")
        identifiers = patient.get("identifier", [])
        if identifiers:
            for identifier in identifiers:
                print(f"    - System: {identifier.get('system')}, Valor: {identifier.get('value')}")
        else:
            print("    No tiene identificadores.")
        
        # Mostrar telecom (teléfono/email)
        telecoms = patient.get("telecom", [])
        if telecoms:
            print("  Información de Contacto:")
            for telecom in telecoms:
                print(f"    - {telecom.get('system').capitalize()}: {telecom.get('value')} ({telecom.get('use')})")
        
        # Mostrar dirección
        addresses = patient.get("address", [])
        if addresses:
            print("  Dirección:")
            for address in addresses:
                line = address.get('line', [])
                city = address.get('city', '')
                postal_code = address.get('postalCode', '')
                country = address.get('country', '')
                full_address = ', '.join(line)
                if city: full_address += f", {city}"
                if postal_code: full_address += f" ({postal_code})"
                if country: full_address += f", {country}"
                print(f"    - {full_address} ({address.get('use')})")
        
        print("---------------------------\n")
    else:
        print("No se encontró ningún paciente con el identificador especificado.")

# Ejemplo de uso
if __name__ == "__main__":
    # Cadena de conexión a MongoDB (¡Reemplaza con tu propia cadena de conexión si es diferente!)
    # Asegúrate de que las credenciales y el nombre de la base de datos sean correctos.
    uri = "mongodb+srv://mardugo:clave@sampleinformationservic.t2yog.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"

    # Nombre de la base de datos y la colección donde se guardan los pacientes FHIR
    db_name = "SamplePatientService" # La base de datos donde PatientCrud guarda
    collection_name = "patients"     # La colección que PatientCrud usa

    # Conectar a MongoDB
    patients_collection = connect_to_mongodb(uri, db_name, collection_name)
    
    if patients_collection:
        # Identifier específico a buscar (¡Asegúrate de que 'system' coincida con lo que usas en FHIR!)
        # Por ejemplo, 'CC' para Cédula de Ciudadanía si así lo guardas.
        # Y '1020713756' es un valor de ejemplo.
        identifier_system_to_search = "CC" # Ejemplo: "CC", "TI", "DNI", "SSN"
        identifier_value_to_search = "1020713756" # Valor de ejemplo

        # Buscar el paciente por identifier
        patient_found = find_patient_by_identifier(patients_collection, identifier_system_to_search, identifier_value_to_search)
        
        # Mostrar los datos del paciente encontrado
        display_patient(patient_found)
    else:
        print("No se pudo establecer la conexión a la base de datos.")

