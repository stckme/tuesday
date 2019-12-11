# fastapi
# app: uvicorn service:app --host 0.0.0.0 --port 8888
# Hug
app: gunicorn service:__hug_wsgi__ -b unix:./run/app.sock -w 4 --access-logfile ./logs/access.log --error-logfile ./logs/error.log --log-level error -n tuesday
queue: celery worker -A app.tasks.queue -c 4 -l info -f ./logs/celery.log
