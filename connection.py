from pymongo import MongoClient
from pymongo.server_api import ServerApi

def connect_to_mongodb():
    uri = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Nombre de la base de datos y colección ya puestos
    db = client["SamplePatientService"]
    collection = db["patients"]

    return collection

# Inserta un ejemplo de paciente
if __name__ == "__main__":
    collection = connect_to_mongodb()

    paciente = {
        "nombreCompleto": "Juan Pérez García",
        "tipoIdentificacion": "CC",
        "numeroIdentificacion": "1234567890",
        "fechaNacimiento": "1990-05-10",
        "genero": "Masculino",
        "telefono": "+573001234567",
        "correoElectronico": "juan.perez@example.com",
        "direccion": "Calle 10 # 20-30",
        "epsAseguradora": "SURA EPS",
        "tipoServicio": "Toma de Muestra",
        "fechaCita": "2025-06-01",
        "horaCita": "08:30",
        "examenes": ["Hemograma Completo", "Glicemia en Ayunas"],
        "notasPaciente": "Ninguna observación."
    }

    result = collection.insert_one(paciente)
    print("Paciente guardado con ID:", result.inserted_id)
