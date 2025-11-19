web: cd gestion_humana && python manage.py migrate && gunicorn --bind 0.0.0.0:$PORT --log-file - gestion_humana.wsgi:application
