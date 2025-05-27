from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date, time, datetime
from pymongo.results import InsertOneResult
from pymongo.errors import PyMongoError
from app.controlador.PatientCrud import PatientCrud  # ✅ ahora sí existe y se puede importar


# --- Definición de Modelos Pydantic ---

class DatosPacienteLite(BaseModel):
    nombreCompleto: str
    numeroIdentificacion: str
    correoElectronico: EmailStr
    telefono: Optional[str] = None

class AppointmentCreate(BaseModel):
    idPacienteFHIR: str
    tipoServicio: str
    fechaCita: date
    horaCita: time
    examenesSolicitados: List[str] = Field(default_factory=list)
    notasPaciente: Optional[str] = None

# --- Configuración de la Aplicación FastAPI ---

app = FastAPI(
    title="Backend LIS - Agendamiento de Citas y Gestión de Pacientes",
    description="API para gestionar el agendamiento de citas de laboratorio y los datos de pacientes en el sistema LIS.",
    version="1.0.0",
)

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://hl7-fhir-ehr-brayan-9053.onrender.com",
    "https://hl7-fhir-ehr-brayan-123456.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Instancias y Configuración ---
patient_crud = PatientCrud()

from pymongo import MongoClient, ServerApi
# Conectar y obtener la colección de citas (appointments)
client = MongoClient("mongodb+srv://brayanruiz:Max2005@cluster0.xevyoo8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))
db = client["SamplePatientService"]
appointments_collection = db["appointments"]  # ✅ colección correcta

# --- Rutas (Endpoints) de la API ---

@app.get("/")
async def read_root():
    return {"message": "Backend del Sistema LIS funcionando con FastAPI. ¡Hola!"}

@app.post("/api/appointments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment: AppointmentCreate):
    try:
        fecha_hora_cita = datetime.combine(appointment.fechaCita, appointment.horaCita)
        appointment_data = appointment.dict()
        appointment_data["fechaCita"] = fecha_hora_cita
        appointment_data["createdAt"] = datetime.utcnow()
        appointment_data["estadoCita"] = "Pendiente"
        
        result: InsertOneResult = appointments_collection.insert_one(appointment_data)

        return {
            "message": "Cita creada exitosamente",
            "appointmentId": str(result.inserted_id),
            "data": appointment_data
        }

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

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
