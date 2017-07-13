web: gunicorn config.wsgi:application
worker: celery worker --app=toreda.taskapp --loglevel=info
