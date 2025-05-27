from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from pymongo.errors import PyMongoError
import uvicorn

from app.controlador.PatientCrud import get_patient_by_id_fhir, write_patient, collection

app = FastAPI()

# --- Configuración de CORS ---
origins = ["http://localhost:3000", "https://tusitio-en-render.com"]  # Ajusta esto

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint raíz para verificar que la API está funcionando
@app.get("/")
async def root():
    return {"message": "API funcionando correctamente"}

@app.get("/patients", response_model=list)
async def get_all_patients():
    if collection is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Servicio no disponible: Conexión a la base de datos no establecida.")
    try:
        patients = []
        for patient in collection.find():
            if '_id' in patient and isinstance(patient['_id'], ObjectId):
                patient['_id'] = str(patient['_id'])
            patients.append(patient)
        return JSONResponse(status_code=status.HTTP_200_OK, content=patients)
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error de base de datos al obtener todos los pacientes: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error inesperado al obtener todos los pacientes: {e}")
