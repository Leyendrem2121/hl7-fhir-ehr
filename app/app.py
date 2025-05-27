frfrom fastapi import FastAPI, HTTPException, Request, status # Importar 'status' para códigos HTTP
from fastapi.responses import JSONResponse # Para respuestas JSON personalizadas
from fastapi.middleware.cors import CORSMiddleware
import uvicorn # Para ejecutar el servidor localmente

# Importar las funciones CRUD y la variable 'collection' desde PatientCrud.py

# Asegúrate de que los nombres de las funciones en PatientCrud.py coincidan con estos (ej. 'get_patient_by_id_fhir')

from app.controlador.PatientCrud import get_patient_by_id_fhir, write_patient, collection

app = FastAPI()

# --- Configuración de CORS ---

# Permite que tu frontend (local o desplegado) pueda comunicarse con este backend.

# --- LA LÍNEA CORREGIDA ESTÁ AQUÍ ABAJO ---
origins =

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# --- Endpoints de la API ---

# Endpoint para obtener un paciente por su ID de recurso FHIR

@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    """
    Obtiene un paciente de MongoDB por su ID de recurso FHIR ('id').
    """
    # Verifica si la conexión a la base de datos está activa
    if collection is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Servicio no disponible: Conexión a la base de datos no establecida.")

    # Llama a la función CRUD para obtener el paciente
    status_code_crud, patient_data = get_patient_by_id_fhir(patient_id)

    if status_code_crud == "success":
        # Retorna el paciente encontrado con un código de estado 200 OK
        return JSONResponse(status_code=status.HTTP_200_OK, content=patient_data)
    elif status_code_crud == "notFound":
        # Si no se encuentra, retorna un 404 Not Found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
    else: # Esto captura el "error" genérico de PatientCrud.py
        # Cualquier otro error se maneja como un 500 Internal Server Error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error interno del servidor al obtener paciente: {patient_data}")

# Endpoint para añadir un nuevo paciente

@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    """
    Recibe los datos del paciente en formato JSON (esperado como un recurso HL7 FHIR Patient)
    y los guarda en MongoDB.
    """
    # Verifica si la conexión a la base de datos está activa
    if collection is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Servicio no disponible: Conexión a la base de datos no establecida.")

    try:
        # Intenta parsear el cuerpo de la solicitud como JSON
        new_patient_dict = dict(await request.json())
    except Exception as e:
        # Si el JSON es inválido, retorna un 400 Bad Request
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Formato JSON inválido en la solicitud: {e}")

    # Llama a la función CRUD para escribir (insertar) el paciente
    status_code_crud, result_data = write_patient(new_patient_dict)

    if status_code_crud == "success":
        # Si la inserción fue exitosa, retorna un 201 Created y el ID del paciente
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"message": "Paciente registrado exitosamente", "insertedId": result_data})
    elif status_code_crud == "errorValidating":
        # Si hay un error de validación FHIR, retorna un 400 Bad Request
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error de validación de datos FHIR: {result_data}")
    elif status_code_crud == "errorInserting":
        # Si hay un error al insertar en la base de datos, retorna un 500 Internal Server Error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error al insertar paciente en la base de datos: {result_data}")
    else: # Esto captura cualquier otro estado de error no esperado de PatientCrud.py
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error inesperado al registrar paciente: {result_data}")

# Nuevo Endpoint Opcional: Para obtener TODOS los pacientes

@app.get("/patients", response_model=list) # Usamos '/patients' (plural) por convención RESTful
async def get_all_patients():
    """
    Obtiene todos los pacientes de la colección de MongoDB.
    """
    # Verifica si la conexión a la base de datos está activa
    if collection is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Servicio no disponible: Conexión a la base de datos no establecida.")
    try:
        patients = # Inicializa la lista aquí
        # collection es el objeto PyMongo Collection. Iteramos sobre todos los documentos.
        for patient in collection.find():
            # Asegurarse de que el _id de MongoDB sea un string para la respuesta JSON
            if '_id' in patient and isinstance(patient['_id'], ObjectId):
                patient['_id'] = str(patient['_id'])
            patients.append(patient)
        return JSONResponse(status_code=status.HTTP_200_OK, content=patients)
    except PyMongoError as e:
        # Manejo de errores específicos de PyMongo
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error de base de datos al obtener todos los pacientes: {e}")
    except Exception as e:
        # Manejo de cualquier otro error inesperado
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error inesperado al obtener todos los pacientes: {e}")

# --- Bloque para ejecutar la aplicación localmente ---

if __name__ == '__main__':
    # 'app:app' significa que Uvicorn buscará la aplicación 'app' dentro del módulo 'app.py'
    # 'reload=True' es útil en desarrollo para que el servidor se reinicie con cada cambio en el código
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
