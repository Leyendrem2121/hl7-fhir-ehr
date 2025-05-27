from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr # Para validación de datos con Pydantic
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, time, datetime

# Importamos nuestra función de conexión a MongoDB
from connection import get_db
from pymongo.results import InsertOneResult
from pymongo.errors import PyMongoError # Para un manejo de errores más específico de PyMongo
from bson import ObjectId # Necesario para trabajar con los _id de MongoDB

# CAMBIO CLAVE: Importamos la CLASE PatientCrud y los modelos que usa (FHIRPatient, ValidationError)
# No importamos funciones o variables directas de PatientCrud.
from controlador.PatientCrud import PatientCrud, FHIRPatient, ValidationError 

# --- Definición de Modelos Pydantic para la Validación de Datos ---

class DatosPacienteLite(BaseModel):
    nombreCompleto: str
    numeroIdentificacion: str
    correoElectronico: EmailStr # Validar formato de email
    telefono: Optional[str] = None

class AppointmentCreate(BaseModel):
    idPacienteFHIR: str
    tipoServicio: str
    fechaCita: date # Pydantic validará que sea un formato de fecha válido (YYYY-MM-DD)
    horaCita: time # Pydantic validará que sea un formato de hora válido (HH:MM:SS)
    examenesSolicitados: List[str] = Field(default_factory=list) # Lista de strings, por defecto vacía
    notasPaciente: Optional[str] = None
    
# --- Configuración de la Aplicación FastAPI ---

app = FastAPI(
    title="Backend LIS - Agendamiento de Citas y Gestión de Pacientes",
    description="API para gestionar el agendamiento de citas de laboratorio y los datos de pacientes en el sistema LIS.",
    version="1.0.0",
)

# Configuración de CORS para permitir solicitudes desde tu frontend
origins = [
    "http://127.0.0.1:5500",  # Si estás usando Live Server en VS Code
    "http://localhost:5500", # Otro puerto común para desarrollo
    "http://127.0.0.1:8000", # Si tu frontend está en el mismo servidor pero otro puerto
    "http://localhost:8000",
    "https://hl7-fhir-ehr-brayan-9053.onrender.com", # Tu servicio FHIR (si accedes a él desde el frontend)
    "https://hl7-fhir-ehr-brayan-123456.onrender.com" # Tu propio backend (si el frontend se despliega allí)
    # Reemplaza con la URL real donde se desplegará tu frontend LIS
    # Por ejemplo: "https://tu-frontend-lis.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Lista de orígenes permitidos
    allow_credentials=True,      # Permitir cookies y credenciales
    allow_methods=["*"],         # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],         # Permitir todos los encabezados
)

# Variable global para la conexión a la base de datos
db = None
# Instancia de PatientCrud
patient_crud = None

# Evento que se ejecuta al iniciar la aplicación FastAPI
@app.on_event("startup")
async def startup_db_client():
    global db, patient_crud
    db = get_db() # Obtiene la instancia de la base de datos
    if db is None:
        print("¡Advertencia! La conexión a MongoDB no pudo establecerse al inicio.")
        # Aquí no inicializamos patient_crud para que los endpoints de paciente fallen si no hay DB
    else:
        # CAMBIO CLAVE: Inicializamos la clase PatientCrud aquí
        # PatientCrud internamente usará get_db() para obtener la conexión
        patient_crud = PatientCrud() 
        print("PatientCrud inicializado.")
        
# Evento que se ejecuta al apagar la aplicación FastAPI
@app.on_event("shutdown")
async def shutdown_db_client():
    if db:
        print("Aplicación apagándose. Conexión a MongoDB persistente o gestionada por driver.")

# --- Rutas (Endpoints) de la API ---

@app.get("/")
async def read_root():
    """
    Endpoint de prueba para verificar que el backend está funcionando.
    """
    return {"message": "Backend del Sistema LIS funcionando con FastAPI. ¡Hola!"}

@app.post("/api/appointments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment: AppointmentCreate):
    """
    Crea una nueva cita en la base de datos MongoDB.
    """
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="No se pudo conectar a la base de datos.")

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

        result: InsertOneResult = db.appointments.insert_one(appointment_data_for_db)
        
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
    """
    Recupera todas las citas de la base de datos.
    """
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="No se pudo conectar a la base de datos.")
    
    try:
        appointments = []
        for doc in db.appointments.find():
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


# --- Endpoints para la gestión de Pacientes en MongoDB LIS (usando PatientCrud) ---

@app.post("/api/patients", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_or_update_patient_in_lis(patient_data: dict): # Recibe un dict, que será validado por FHIRPatient
    """
    Crea o actualiza un recurso FHIR Patient en la base de datos MongoDB de tu LIS.
    """
    if patient_crud is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="El servicio de pacientes no está inicializado. Conexión a DB fallida.")
    
    status_code, result_data = patient_crud.create_or_update_patient_fhir_resource(patient_data)
    
    if status_code == "success":
        return {"message": "Paciente FHIR procesado exitosamente en MongoDB LIS", "patientId": result_data}
    elif status_code == "errorValidating":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Error de validación FHIR: {result_data}")
    else: # errorInserting
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al procesar el paciente en MongoDB LIS: {result_data}")

@app.get("/api/patients/{object_id}", response_model=dict)
async def get_patient_by_mongodb_id(object_id: str):
    """
    Obtiene un recurso FHIR Patient de la base de datos LIS por su ObjectId de MongoDB.
    """
    if patient_crud is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="El servicio de pacientes no está inicializado. Conexión a DB fallida.")
    
    status_code, patient = patient_crud.get_patient_by_object_id(object_id)
    if status_code == "success":
        return patient
    elif status_code == "notFound":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado en MongoDB LIS.")
    else: # error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener paciente: {patient}")

@app.get("/api/patients/identifier/{system}/{value}", response_model=dict)
async def get_patient_by_fhir_id(system: str, value: str):
    """
    Obtiene un recurso FHIR Patient de la base de datos LIS por su identificador FHIR.
    """
    if patient_crud is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="El servicio de pacientes no está inicializado. Conexión a DB fallida.")
    
    status_code, patient = patient_crud.get_patient_by_fhir_identifier(system, value)
    if status_code == "success":
        return patient
    elif status_code == "notFound":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado por identificador FHIR en MongoDB LIS.")
    else: # error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener paciente: {patient}")

@app.get("/api/patients")
async def get_all_patients_from_lis():
    """
    Recupera todos los pacientes de la base de datos LIS.
    """
    if patient_crud is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="El servicio de pacientes no está inicializado. Conexión a DB fallida.")
    
    try:
        patients = patient_crud.get_all_patients()
        return patients
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener todos los pacientes: {str(e)}")


# Para ejecutar en desarrollo (Uvicorn)
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
