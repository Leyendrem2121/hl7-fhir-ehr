from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError, ConnectionFailure
from bson.objectid import ObjectId
from fhir.resources.patient import Patient

# --- Configuración de la Conexión a MongoDB ---
MONGODB_URI = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "SamplePatientService"
COLLECTION_NAME = "patients"

# Variables globales para el cliente y la colección
db_client = None
collection = None

# --- Función interna para establecer la conexión a la DB ---
def _setup_db_connection():
    """
    Establece y retorna el objeto de colección de MongoDB.
    """
    global db_client, collection
    try:
        client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        client.admin.command('ping')
        print(f"Conexión a MongoDB a la colección '{COLLECTION_NAME}' en DB '{DB_NAME}' establecida con éxito!")
        db_client = client
        db = db_client[DB_NAME]
        collection = db[COLLECTION_NAME]
    except (PyMongoError, ConnectionFailure) as e:
        print("Error conectando a MongoDB:", e)
        raise

_setup_db_connection()

# --- Funciones CRUD ---
def get_patient_by_id_fhir(patient_id):
    """
    Obtiene un paciente por su ID de FHIR (almacenado como _id en la base de datos).
    """
    try:
        document = collection.find_one({"_id": ObjectId(patient_id)})
        if document:
            document["id"] = str(document["_id"])
            del document["_id"]
            return Patient(**document)
        return None
    except Exception as e:
        print(f"Error obteniendo paciente por ID: {e}")
        return None

def write_patient(patient: Patient):
    """
    Escribe un paciente FHIR en la base de datos MongoDB.
    """
    try:
        patient_dict = patient.dict()
        if "id" in patient_dict:
            del patient_dict["id"]
        result = collection.insert_one(patient_dict)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error escribiendo paciente: {e}")
        return None
