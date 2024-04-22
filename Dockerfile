# syntax=docker/dockerfile:1
FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /hhh_website
COPY requirements.txt /hhh_website/
RUN pip install -r requirements.txt
COPY . /hhh_website/
RUN chmod +x ./dockercmd.sh
ENTRYPOINT ["/bin/bash", "./dockercmd.sh"]
# ENTRYPOINT [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]