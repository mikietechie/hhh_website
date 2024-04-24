from pathlib import Path
import os

## THREADS and Workers
workers = int(os.environ.get("WORKERS", 1))
threads = int(os.environ.get("THREADS", 3))

## PORTS
bind = '0.0.0.0:8000'

## LOGGING
logs_path = "./logs"
Path(logs_path).mkdir(parents=True, exist_ok=True)
# Access log - records incoming HTTP requests
accesslog =  logs_path + "/gunicorn.access.log"
open(accesslog, "a").close()
# Error log - records Gunicorn server goings-on
errorlog =  logs_path + "/gunicorn.error.log"
open(errorlog, "a").close()
# Whether to send Django output to the error log
capture_output = True
# How verbose the Gunicorn error logs should be 
loglevel = "info"