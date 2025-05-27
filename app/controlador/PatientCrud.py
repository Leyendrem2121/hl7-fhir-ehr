from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError, ConnectionFailure
from bson.objectid import ObjectId
from fhir.resources.patient import Patient

MONGODB_URI = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "SamplePatientService"
COLLECTION_NAME = "patients"

class PatientCrud:
    def __init__(self):
        try:
            client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
            client.admin.command('ping')
            print("Conexión a MongoDB exitosa")
            db = client["SamplePatientService"]
            self.collection = db["patients"]
        except (PyMongoError, ConnectionFailure) as e:
            print("Error conectando a MongoDB:", e)
            raise

    def get_patient_by_object_id(self, object_id):
        try:
            document = self.collection.find_one({"_id": ObjectId(object_id)})
            if document:
                document["id"] = str(document["_id"])
                del document["_id"]
                return "success", Patient(**document)
            return "notFound", None
        except Exception as e:
            print(f"Error al buscar paciente: {e}")
            return "error", str(e)

    def create_or_update_patient_fhir_resource(self, patient_data):
        try:
            patient = Patient(**patient_data)
            patient_dict = patient.dict()
            if "id" in patient_dict:
                del patient_dict["id"]
            result = self.collection.insert_one(patient_dict)
            return "success", str(result.inserted_id)
        except Exception as e:
            print(f"Error creando paciente: {e}")
            return "error", str(e)

    def get_all_patients(self):
        try:
            patients = []
            for doc in self.collection.find():
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                patients.append(doc)
            return patients
        except Exception as e:
            print(f"Error obteniendo pacientes: {e}")
            raise


