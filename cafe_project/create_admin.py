
#!/usr/bin/env python
import os
import django
import sys

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cafe_site.settings")
django.setup()

from django.contrib.auth.models import User

def create_admin(username, password):
    try:
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists.")
            return
            
        User.objects.create_superuser(username=username, email='admin@example.com', password=password)
        print(f"Admin user '{username}' created successfully.")
    except Exception as e:
        print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    create_admin(username, password)
