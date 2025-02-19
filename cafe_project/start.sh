
#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Install NPM packages for tailwind
# cd theme/static_src && npm install && cd ../..

# Build Tailwind CSS
python manage.py tailwind install
python manage.py tailwind build

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Start Django server
python manage.py runserver 0.0.0.0:8000
