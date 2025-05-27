# oldFiles/findPatient.py

# Importar la función de conexión desde tu archivo connection.py
# Asumiendo que connection.py está en el mismo nivel que la carpeta 'app' o en un nivel superior accesible.
from connection import connect_to_mongodb
from pymongo.errors import PyMongoError # Para un manejo de errores más específico de PyMongo
from bson.objectid import ObjectId # Para convertir el _id de MongoDB a string para mostrar

# --- La función original 'connect_to_mongodb' se elimina de aquí ---
# --- porque ahora la importamos desde connection.py ---

def find_patient_by_identifier(collection, identifier_system_code: str, identifier_value: str):
    """
    Busca un paciente en la colección de MongoDB por un identificador FHIR específico
    (sistema y código de tipo de identificador, y valor).

    Args:
        collection: El objeto de la colección de MongoDB.
        identifier_system_code (str): El sistema y código del identificador FHIR,
                                      en formato "http://system|code" (ej. "http://...|ID").
        identifier_value (str): El valor del identificador (ej. "1234567890").

    Returns:
        dict or None: El documento del paciente encontrado (con _id como string),
                      o None si no se encuentra o hay un error.
    """
    try:
        # --- ESTA ES LA PARTE CLAVE QUE DEBE CAMBIAR SÍ O SÍ ---
        # Dividir el string identifier_system_code en 'system' y 'code'
        # para que coincida con la estructura FHIR que estamos guardando.
        # Ejemplo: "http://terminology.hl7.org/CodeSystem/v2-0203|ID"
        if '|' not in identifier_system_code:
            print(f"Error: El formato de 'identifier_system_code' '{identifier_system_code}' "
                  "no es 'system|code'.")
            return None
        
        system, code = identifier_system_code.split('|', 1) # Divide solo en el primer '|'

        # Construir la consulta para que coincida con la estructura de identificadores FHIR
        # Buscamos un elemento en el array 'identifier' donde:
        # 1. El array 'type.coding' contenga un elemento con 'system' y 'code' específicos.
        # 2. El 'value' del identificador coincida.
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
        # --- FIN DE LA PARTE CLAVE ---

        patient = collection.find_one(query)
        
        # Convertir el ObjectId de MongoDB a string para consistencia si se encuentra
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
        
    else:
        print("No se encontró ningún paciente con el identificador especificado.")

# Ejemplo de uso (se ejecuta solo cuando el script es el principal)
if __name__ == "__main__":
    db_name = "SamplePatientService"
    collection_name = "patients"

    # Conectar a MongoDB usando la función de connection.py
    collection = connect_to_mongodb(db_name, collection_name)
    
    if collection is None:
        print("ERROR: No se pudo establecer la conexión a MongoDB. No se puede buscar pacientes.")
    else:
        # IMPORTANTE: Reemplaza estos valores con un identificador (system|code)
        # y un valor real de un paciente que hayas insertado a través de tu frontend.
        # Ejemplo de identificador de cédula de ciudadanía (el que usa tu frontend)
        identifier_to_search_type = "http://terminology.hl7.org/CodeSystem/v2-0203|ID"
        identifier_to_search_value = "1234567890" # Asegúrate que este valor exista en tu DB

        print(f"\nBuscando paciente con Tipo de ID '{identifier_to_search_type}' y Valor '{identifier_to_search_value}'...")
        patient_found = find_patient_by_identifier(collection, identifier_to_search_type, identifier_to_search_value)
        
        display_patient(patient_found)
