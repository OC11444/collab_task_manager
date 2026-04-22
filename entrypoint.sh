#!/bin/sh
set -e

echo " Applying database migrations...almost...there!"
python manage.py migrate --noinput

echo " Collecting static files..."
python manage.py collectstatic --noinput || echo "Static collection skipped"

echo " Starting Gunicorn server...meeep... ...meeeep..... ....hurray "
# Using collab_task_manager as identified in your file list<----our project management file
exec gunicorn collab_task_manager.wsgi:application --bind 0.0.0.0:10000