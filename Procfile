web: cd gestion_humana && python manage.py migrate && gunicorn --bind 0.0.0.0:$PORT --timeout 120 --log-file - gestion_humana.wsgi:application
