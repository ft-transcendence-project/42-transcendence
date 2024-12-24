FROM python:latest

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r /code/requirements.txt

COPY . /code/
