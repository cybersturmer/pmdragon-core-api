web: uvicorn conf.asgi:application --host=0.0.0.0 --port=${PORT:-5000}
celery: celery -A conf.production.celery worker --loglevel=INFO