web: uvicorn conf.asgi:application --host=0.0.0.0 --port=${PORT:-5000}
celery: celery worker -A conf.production.celery -l info -c 4