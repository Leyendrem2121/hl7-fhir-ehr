from pymongo import MongoClient
from pymongo.server_api import ServerApi

# URI de conexión a MongoDB Atlas - ¡Usando la que tú proporcionaste!
MONGODB_URI = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "LIS" # El nombre de la base de datos que queremos usar

def get_db(): # Renombrado a 'get_db' para que coincida con el import en app.py
    """
    Establece y devuelve una conexión a la base de datos MongoDB.
    """
    try:
        # Crea un nuevo cliente y una nueva conexión al servidor
        client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        
        # Haz ping a tu implementación para confirmar una conexión exitosa
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
        # Devuelve la base de datos específica (en este caso, 'LIS')
        # Esto es lo que app.py espera (el objeto 'db' para hacer db.appointments)
        return client[DB_NAME] 
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None
