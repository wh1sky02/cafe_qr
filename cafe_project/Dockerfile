FROM python:3.11.4-slim-bullseye as builder

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11.4-slim-bullseye

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY . .

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=cafe_site.settings

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
