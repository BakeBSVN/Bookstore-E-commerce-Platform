#!/bin/bash
set -e


chmod +x ./docker-entrypoint.sh
/wait-for-it.sh db:3306 --timeout=20 --strict -- echo "MySQL is up"
## Run migrations
python manage.py migrate

## Collect static files
python manage.py collectstatic --noinput

# Run server
#uwsgi --ini /bookstore/uwsgi.ini
gunicorn bookstore.wsgi:application --bind 0.0.0.0:8001


