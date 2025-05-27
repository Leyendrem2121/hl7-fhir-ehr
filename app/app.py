from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, time, datetime

# Importamos la colección desde la conexión a MongoDB
from connection import collection as mongo_collection
from pymongo.results import InsertOneResult
from pymongo.errors import PyMongoError
from bson import ObjectId

# Importación de PatientCrud desde su ruta completa
from app.controlador.PatientCrud import PatientCrud, FHIRPatient, ValidationError

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

# Instancia de PatientCrud
patient_crud = PatientCrud()

# --- Rutas (Endpoints) de la API ---

@app.get("/")
async def read_root():
    return {"message": "Backend del Sistema LIS funcionando con FastAPI. ¡Hola!"}

@app.post("/api/appointments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment: AppointmentCreate):
    try:
        fecha_hora_cita = datetime.combine(appointment.fechaCita, appointment.horaCita)
        appointment_data_for_db = appointment.dict()
        appointment_data_for_db["fechaCita"] = fecha_hora_cita
        appointment_data_for_db["createdAt"] = datetime.utcnow()
        appointment_data_for_db["estadoCita"] = "Pendiente"

        if "datosPacienteLite" not in appointment_data_for_db:
             appointment_data_for_db["datosPacienteLite"] = {
                "nombreCompleto": "", 
                "numeroIdentificacion": "",
                "correoElectronico": "",
                "telefono": ""
             }

        result: InsertOneResult = mongo_collection.insert_one(appointment_data_for_db)

        return {
            "message": "Cita creada exitosamente",
            "appointmentId": str(result.inserted_id),
            "data": appointment_data_for_db
        }

    except PyMongoError as e:
        print(f"Error de PyMongo al crear la cita: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error de base de datos al crear la cita: {str(e)}")
    except Exception as e:
        print(f"Error inesperado al crear la cita: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error interno del servidor al crear la cita: {str(e)}")

@app.get("/api/appointments")
async def get_all_appointments():
    try:
        appointments = []
        for doc in mongo_collection.find():
            doc["_id"] = str(doc["_id"])
            appointments.append(doc)
        return appointments
    except PyMongoError as e:
        print(f"Error de PyMongo al obtener citas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error de base de datos al obtener citas: {str(e)}")
    except Exception as e:
        print(f"Error inesperado al obtener citas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error interno del servidor al obtener citas: {str(e)}")

@app.post("/api/patients", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_or_update_patient_in_lis(patient_data: dict):
    status_code, result_data = patient_crud.create_or_update_patient_fhir_resource(patient_data)

    if status_code == "success":
        return {"message": "Paciente FHIR procesado exitosamente en MongoDB LIS", "patientId": result_data}
    elif status_code == "errorValidating":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Error de validación FHIR: {result_data}")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al procesar el paciente en MongoDB LIS: {result_data}")

@app.get("/api/patients/{object_id}", response_model=dict)
async def get_patient_by_mongodb_id(object_id: str):
    status_code, patient = patient_crud.get_patient_by_object_id(object_id)
    if status_code == "success":
        return patient
    elif status_code == "notFound":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado en MongoDB LIS.")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener paciente: {patient}")

@app.get("/api/patients/identifier/{system}/{value}", response_model=dict)
async def get_patient_by_fhir_id(system: str, value: str):
    status_code, patient = patient_crud.get_patient_by_fhir_identifier(system, value)
    if status_code == "success":
        return patient
    elif status_code == "notFound":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado por identificador FHIR en MongoDB LIS.")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener paciente: {patient}")

@app.get("/api/patients")
async def get_all_patients_from_lis():
    try:
        patients = patient_crud.get_all_patients()
        return patients
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener todos los pacientes: {str(e)}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
