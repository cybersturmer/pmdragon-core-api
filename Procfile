web: uvicorn conf.asgi:application --host=0.0.0.0 --port=${PORT:-5000}
worker: celery -A conf.celery worker --loglevel=INFO