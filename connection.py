from pymongo import MongoClient
from pymongo.server_api import ServerApi

def get_db():
    uri = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["SamplePatientService"]  # Devuelve la base de datos completa, no solo una colección
    return db

# Solo para prueba local, puedes dejar o eliminar esta parte
if __name__ == "__main__":
    db = get_db()
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
    result = db.patients.insert_one(paciente)  # Aquí usas la colección desde db
    print("Paciente guardado con ID:", result.inserted_id)
