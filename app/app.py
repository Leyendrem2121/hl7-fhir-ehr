from fastapi import FastAPI, HTTPException, Request, status # Importar &#39;status&#39; para códigos HTTP
from fastapi.responses import JSONResponse # Para respuestas JSON personalizadas
from fastapi.middleware.cors import CORSMiddleware
import uvicorn # Para ejecutar el servidor localmente

# Importar las funciones CRUD y la variable 'collection' desde PatientCrud.py

# Asegúrate de que los nombres de las funciones en PatientCrud.py coincidan con estos (ej. 'get\_patient\_by\_id\_fhir')

from app.controlador.PatientCrud import get\_patient\_by\_id\_fhir, write\_patient, collection

app = FastAPI()

# \--- Configuración de CORS ---

# Permite que tu frontend (local o desplegado) pueda comunicarse con este backend.

origins = [
"https://hl7-patient-write-brayan-9053.onrender.com", \# Dominio de tu frontend ya desplegado
"http://localhost",         \# Para pruebas locales sin puerto específico
"http://localhost:3000",    \# Típico puerto de frameworks frontend (React, Vue, Angular) en desarrollo
"http://localhost:8000",    \# El puerto donde corre tu backend si lo accedes desde el mismo host
\# Puedes añadir más orígenes si tu frontend corre en otros puertos o dominios locales
]

app.add\_middleware(
CORSMiddleware,
allow\_origins=origins,
allow\_credentials=True,
allow\_methods=["*"],  \# Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
allow\_headers=["*"],  \# Permitir todos los encabezados
)

# \--- Endpoints de la API ---

# Endpoint para obtener un paciente por su ID de recurso FHIR

@app.get("/patient/{patient\_id}", response\_model=dict)
async def get\_patient\_by\_id(patient\_id: str):
"""
Obtiene un paciente de MongoDB por su ID de recurso FHIR ('id').
"""
\# Verifica si la conexión a la base de datos está activa
if collection is None:
raise HTTPException(status\_code=status.HTTP\_503\_SERVICE\_UNAVAILABLE,
detail="Servicio no disponible: Conexión a la base de datos no establecida.")
