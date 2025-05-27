# app/controlador/PatientCrud.py

# Importaciones necesarias
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError, ConnectionFailure
from bson.objectid import ObjectId
from fhir.resources.patient import Patient  # Asegúrate de tener 'fhir.resources' instalado

# --- Configuración de la Conexión a MongoDB ---

# IMPORTANTE: La URI de conexión debe ser la tuya.
# Idealmente, esta URI debería venir de una variable de entorno por seguridad,
# pero la mantenemos aquí directamente como en tu estructura.

MONGODB_URI = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "SamplePatientService"
COLLECTION_NAME = "patients"

# Variable global para el cliente de MongoDB y la colección
# Se inicializarán cuando este archivo sea importado por app.py.

db_client = None
collection = None

# --- Función interna para establecer la conexión a la DB ---
# Esta función es llamada una vez al cargar este módulo.

def _setup_db_connection():
    """
    Intenta establecer y retornar el objeto de colección de MongoDB y el cliente.
    Asigna estos a las variables globales 'collection' y 'db_client'.
    """
    global db_client, collection  # Indica que estamos modificando las variables globales
    try:
        client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        client.admin.command('ping')  # Prueba la conexión
        print(f"Conexión a MongoDB a la colección '{COLLECTION_NAME}' en DB '{DB_NAME}' establecida con éxito!")
        db_client = client
        collection = client[DB_NAME][COLLECTION_NAME]
    except ConnectionFailure as e:
        print(f"Error al conectar con MongoDB: {e}")
        db_client = None
        collection = None

# Llamar a la función de conexión cuando el módulo sea cargado
_setup_db_connection()
