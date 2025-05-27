from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr # Para validación de datos con Pydantic
from typing import List, Optional
from datetime import date, time, datetime

# Importamos nuestra función de conexión a MongoDB
from connection import get_db
from pymongo.results import InsertOneResult

# --- Definición de Modelos Pydantic para la Validación de Datos ---

# Puedes definir modelos para los datos que esperas recibir
# Esto es una de las grandes ventajas de FastAPI y Pydantic para la validación y documentación automática.

class DatosPacienteLite(BaseModel):
    nombreCompleto: str
    numeroIdentificacion: str
    correoElectronico: EmailStr # Validar formato de email
    telefono: Optional[str] = None

class AppointmentCreate(BaseModel):
    # idPacienteFHIR es crucial, lo recibimos del frontend después de que se crea el paciente FHIR
    idPacienteFHIR: str
    tipoServicio: str
    fechaCita: date # Pydantic validará que sea un formato de fecha válido (YYYY-MM-DD)
    horaCita: time # Pydantic validará que sea un formato de hora válido (HH:MM:SS)
    examenesSolicitados: List[str] = Field(default_factory=list) # Lista de strings, por defecto vacía
    notasPaciente: Optional[str] = None
    
    # Campo para la fecha de creación, se puede rellenar en el backend
    # No se espera que el cliente lo envíe
    # createdAt: datetime = Field(default_factory=datetime.utcnow) # Esto se añadirá en el endpoint

    # Si quieres incluir datos lite del paciente desde el frontend (aunque el backend ya los construye)
    # datosPacienteLite: Optional[DatosPacienteLite] = None

# --- Configuración de la Aplicación FastAPI ---

app = FastAPI(
    title="Backend LIS - Agendamiento de Citas",
    description="API para gestionar el agendamiento de citas de laboratorio en el sistema LIS.",
    version="1.0.0",
)

# Configuración de CORS para permitir solicitudes desde tu frontend
origins = [
    "http://127.0.0.1:5500",  # Si estás usando Live Server en VS Code
    "http://localhost:5500", # Otro puerto común para desarrollo
    "http://127.0.0.1:8000", # Si tu frontend está en el mismo servidor pero otro puerto
    "http://localhost:8000",
    "https://hl7-fhir-ehr-brayan-9053.onrender.com", # Tu servicio FHIR (si accedes a él desde el frontend)
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

# Evento que se ejecuta al iniciar la aplicación FastAPI
@app.on_event("startup")
async def startup_db_client():
    global db
    db = get_db()
    if db is None:
        print("¡Advertencia! La conexión a MongoDB no pudo establecerse al inicio.")
        # Podrías lanzar una excepción o registrar un error crítico aquí
        
# Evento que se ejecuta al apagar la aplicación FastAPI
@app.on_event("shutdown")
async def shutdown_db_client():
    if db:
        # Aquí puedes cerrar la conexión si get_db() devuelve un cliente con método close()
        # En el caso de MongoClient, la conexión se gestiona internamente por pymongo,
        # pero si tuvieras un pool de conexiones o un cliente específico, lo cerrarías aquí.
        # Por ahora, simplemente informamos.
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
        # Convertir la fecha y hora a objetos datetime para el almacenamiento
        # y luego a string ISO para MongoDB si lo prefieres así, o almacenar como datetime directamente.
        # MongoDB almacena objetos datetime de Python como BSON Date.
        fecha_hora_cita = datetime.combine(appointment.fechaCita, appointment.horaCita)

        # Crear el diccionario de datos para insertar en MongoDB
        appointment_data_for_db = appointment.dict() # Convierte el modelo Pydantic a un diccionario
        appointment_data_for_db["fechaCita"] = fecha_hora_cita # Reemplazar fecha y hora separadas por un solo datetime
        appointment_data_for_db["createdAt"] = datetime.utcnow() # Añadir timestamp de creación
        appointment_data_for_db["estadoCita"] = "Pendiente" # Estado inicial

        # Si el frontend envía datosPacienteLite, los usamos. Si no, podrías reconstruirlos o no enviarlos.
        # En nuestro frontend actual, ya los reconstruimos.
        # Aquí, simplemente nos aseguramos de que el campo exista para consistencia.
        if "datosPacienteLite" not in appointment_data_for_db:
             appointment_data_for_db["datosPacienteLite"] = {
                "nombreCompleto": "", # Estos se rellenarán con los datos del paciente FHIR en un escenario real
                "numeroIdentificacion": "",
                "correoElectronico": "",
                "telefono": ""
             }
        # Nota: El frontend ya envía estos datos, así que aquí solo se asegurarían de existir.

        # Insertar la cita en la colección 'appointments'
        result: InsertOneResult = db.appointments.insert_one(appointment_data_for_db)
        
        return {
            "message": "Cita creada exitosamente",
            "appointmentId": str(result.inserted_id), # Convertir ObjectId a string
            "data": appointment_data_for_db # Devolver los datos tal como se guardaron
        }

    except Exception as e:
        print(f"Error al crear la cita: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error interno del servidor: {str(e)}")

# Puedes agregar más rutas (GET para ver citas, PUT para actualizar, DELETE para eliminar)
# Por ejemplo, para obtener todas las citas:
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
            doc["_id"] = str(doc["_id"]) # Convertir ObjectId a string para JSON
            appointments.append(doc)
        return appointments
    except Exception as e:
        print(f"Error al obtener citas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error interno del servidor al obtener citas: {str(e)}")


# Para ejecutar en desarrollo (Uvicorn)
# Asegúrate de que tu `requirements.txt` tenga uvicorn instalado
# Para correr: uvicorn app:app --reload --port 8000
# Si tu archivo se llama 'main.py' en lugar de 'app.py', sería: uvicorn main:app --reload --port 8000
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
