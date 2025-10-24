web: gunicorn askmo.wsgi:application
release: python manage.py migrate && python manage.py import_lapangan && python manage.py import_avatar