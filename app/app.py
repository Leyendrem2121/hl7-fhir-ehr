from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.results import InsertOneResult
from pymongo.errors import PyMongoError
from datetime import datetime

# Configuración conexión MongoDB para appointments
MONGODB_URI = "mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
appointments_collection = client["SamplePatientService"]["appointments"]

@app.post("/api/appointments", response_model=dict, status_code=201)
async def create_appointment(appointment: AppointmentCreate):
    try:
        # Combina fecha y hora en un solo datetime
        fecha_hora_cita = datetime.combine(appointment.fechaCita, appointment.horaCita)
        
        # Prepara datos para guardar
        appointment_data_for_db = appointment.dict()
        appointment_data_for_db["fechaCita"] = fecha_hora_cita
        appointment_data_for_db["createdAt"] = datetime.utcnow()
        appointment_data_for_db["estadoCita"] = "Pendiente"

        # Campo opcional datosPacienteLite, si no viene en el request
        if "datosPacienteLite" not in appointment_data_for_db:
            appointment_data_for_db["datosPacienteLite"] = {
                "nombreCompleto": "", 
                "numeroIdentificacion": "",
                "correoElectronico": "",
                "telefono": ""
            }
        
        # Debug: imprime datos a insertar
        print("Insertando en MongoDB (appointments):", appointment_data_for_db)

        # Inserta en la colección appointments
        result: InsertOneResult = appointments_collection.insert_one(appointment_data_for_db)

        return {
            "message": "Cita creada exitosamente",
            "appointmentId": str(result.inserted_id),
            "data": appointment_data_for_db
        }

    except PyMongoError as e:
        print(f"Error de PyMongo al crear la cita: {e}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    except Exception as e:
        print(f"Error inesperado al crear la cita: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.get("/api/appointments")
async def get_all_appointments():
    try:
        appointments = []
        for doc in appointments_collection.find():
            doc["_id"] = str(doc["_id"])
            appointments.append(doc)
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/patients", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_or_update_patient_in_lis(patient_data: dict):
    status_code, result = patient_crud.create_or_update_patient_fhir_resource(patient_data)
    if status_code == "success":
        return {"message": "Paciente FHIR procesado exitosamente", "patientId": result}
    else:
        raise HTTPException(status_code=500, detail=f"Error al procesar paciente: {result}")

@app.get("/api/patients/{object_id}", response_model=dict)
async def get_patient_by_mongodb_id(object_id: str):
    status_code, patient = patient_crud.get_patient_by_object_id(object_id)
    if status_code == "success":
        return patient.dict()
    elif status_code == "notFound":
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")
    else:
        raise HTTPException(status_code=500, detail=patient)

@app.get("/api/patients")
async def get_all_patients_from_lis():
    try:
        return patient_crud.get_all_patients()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
