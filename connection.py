from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure

# Parámetros de conexión
uri = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
db_name = "SamplePatientService"
collection_name = "patient"

try:
    # Crear cliente y verificar conexión
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command('ping')
    print("✅ Conexión a MongoDB Atlas exitosa.")

    # Seleccionar base de datos y colección
    db = client["SamplePatientService"]
    collection = db["patient"]  # 👈 Esta es la variable que se importa desde app.py

except ConnectionFailure as e:
    print(f"❌ Error de conexión a MongoDB: {e}")
    collection = None  # Previene errores si se importa sin conexión

