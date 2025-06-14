# gunicorn.conf.py

bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
