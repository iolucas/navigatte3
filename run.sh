#!/bin/bash

#Ensure production variable is defined
#if [ -z "$BLUEMIX_REGION" ];then
#echo "Production environment verication failed. Non BLUEMIX_REGION defined."
#exit 100
#fi

echo [$0] Making database migrations...
python manage.py makemigrations
python manage.py migrate

#echo "from django.contrib.auth.models import User; User.objects.create_superuser('user', 'email@email.com', 'pass')" | python manage.py shell

echo [$0] Collecting static files to the root folder...
python manage.py collectstatic

#echo [$0] Testing application...
#python manage.py test
#NOT APPLICACABLE NOW DUE TO LOW DATABASE PRIORITIES

echo [$0] Starting application on gunicorn server...
gunicorn navigatte.wsgi --workers 3 --bind 0.0.0.0:$PORT