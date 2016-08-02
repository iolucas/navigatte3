"""
WSGI config for navigatte project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from dj_static import Cling 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navigatte.settings")

#If production env
if "BLUEMIX_REGION" in os.environ:
    #Serve static files with gunicorn
    application = Cling(get_wsgi_application())
else: #if non production env
    application = get_wsgi_application()