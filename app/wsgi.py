# app/wsgi.py

# Importa la instancia 'app' de tu archivo app.py
# Gunicorn buscará la variable 'app' aquí para ejecutar tu aplicación FastAPI.
from app.app import app 

# NO DEBE HABER NADA MÁS AQUÍ.
# El bloque if __name__ == "__main__": con uvicorn.run() pertenece a app.py.
