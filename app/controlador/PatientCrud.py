# app/controlador/PatientCrud.py

# Importaciones necesarias

from pymongo import MongoClient
from pymongo.server\_api import ServerApi
from pymongo.errors import PyMongoError, ConnectionFailure
from bson.objectid import ObjectId
from fhir.resources.patient import Patient \# Asegúrate de tener 'fhir.resources' instalado

# \--- Configuración de la Conexión a MongoDB ---

# IMPORTANTE: La URI de conexión debe ser la tuya.

# Idealmente, esta URI debería venir de una variable de entorno por seguridad,

# pero la mantenemos aquí directamente como en tu estructura.

MONGODB\_URI = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true\&w=majority\&appName=Cluster0"
DB\_NAME = "SamplePatientService"
COLLECTION\_NAME = "patients"

# Variable global para el cliente de MongoDB y la colección

# Se inicializarán cuando este archivo sea importado por app.py.

db\_client = None
collection = None

# \--- Función interna para establecer la conexión a la DB ---

# Esta función es llamada una vez al cargar este módulo.

def \_setup\_db\_connection():
"""
Intenta establecer y retornar el objeto de colección de MongoDB y el cliente.
Asigna estos a las variables globales 'collection' y 'db\_client'.
"""
global db\_client, collection \# Indica que estamos modificando las variables globales
try:
client = MongoClient(MONGODB\_URI, server\_api=ServerApi('1'))
client.admin.command('ping') \# Prueba la conexión
print(f"Conexión a MongoDB a la colección '{COLLECTION\_NAME}' en DB '{DB\_NAME}' establecida con éxito\!")
