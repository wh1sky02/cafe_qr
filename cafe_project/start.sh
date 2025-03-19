#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Build Tailwind CSS
python manage.py tailwind install
python manage.py tailwind build

# Run database migrations
python manage.py makemigrations
python manage.py migrate --run-syncdb

# Start Django server
python manage.py runserver 0.0.0.0:8000