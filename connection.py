from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, PyMongoError # Importar ConnectionFailure y PyMongoError para manejo de errores

# URI de conexión a MongoDB Atlas
# Esta URI debe ser la de tu clúster 'brayanruiz'
MONGODB_URI = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "LIS" # El nombre de la base de datos que queremos usar en toda la aplicación

def get_db():
    """
    Establece y devuelve una conexión a la base de datos MongoDB (el objeto 'db').
    Esta función no toma argumentos, ya que la URI y el nombre de la DB están definidos aquí.
    """
    try:
        # Crea un nuevo cliente y una nueva conexión al servidor
        client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        
        # Haz ping a tu implementación para confirmar una conexión exitosa
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
        # Devuelve la base de datos específica (en este caso, 'LIS')
        # Esto es lo que app.py espera (el objeto 'db' para hacer db.appointments, db.patients)
        return client[DB_NAME] 
    except (ConnectionFailure, PyMongoError) as e:
        print(f"ERROR: Falló la conexión a MongoDB: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Ocurrió un error inesperado al conectar a MongoDB: {e}")
        return None
