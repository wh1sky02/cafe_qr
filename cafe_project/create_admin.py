#!/usr/bin/env python
import os
import django
import sys

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cafe_site.settings")
django.setup()

from django.contrib.auth.models import User

def set_password(username, password):
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"Password for user '{username}' updated successfully.")
    except User.DoesNotExist:
        print(f"User '{username}' not found.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python set_admin_password.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    set_password(username, password)