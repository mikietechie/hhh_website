from pathlib import Path
## THREADS and Workers
workers = 3
threads = 3

## PORTS
bind = '0.0.0.0:8000'

## LOGGING
logs_path = "./media/logs"
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