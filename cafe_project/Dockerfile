FROM python:3.11.4-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY . /app/

RUN libpq-dev \
    gcc \
    python3-dev \
    nodejs \
    npm

COPY ./requirements.txt .
RUN pip install -r requirements.txt