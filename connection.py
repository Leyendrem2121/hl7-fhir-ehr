from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure

def get_db(db_name, collection_name):
    uri = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Probar la conexión (ping)
        client.admin.command('ping')
        print("Conexión a MongoDB exitosa.")
        db = client[db_name]
        collection = db[collection_name]
        return collection
    except ConnectionFailure as e:
        print(f"Error de conexión a MongoDB: {e}")
        return None
