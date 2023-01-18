#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

LOGIN = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
# HOST = os.getenv("DB_HOST")
# PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_NAME")
# JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# SECRET_KEY = os.getenv("SECRET_KEY")
CIPHER_METHOD = os.getenv("PW_METHOD")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Apka_muzyczna.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
