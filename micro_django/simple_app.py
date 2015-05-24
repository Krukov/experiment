# -*- coding: utf-8 -*-

import os
import sys

from django.conf import settings
from django.http import JsonResponse
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application


if not settings.configured:
    settings.configure(
        DEBUG=os.environ.get('DEBUG', 'on') == 'on',
        SECRET_KEY=os.environ.get('SECRET_KEY', 'INSECURE'),
        ALLOWED_HOSTS=os.environ.get('ALLOWED_HOSTS', 'localhost').split(','),
        ROOT_URLCONF=__name__,
        DATABASES={'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.db',
            }
        },
        INSTALLED_APPS=(
            'django.contrib.sessions',
        ),
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
        ),
    )

urlpatterns = (
    url(r'^$', lambda r: JsonResponse({'A simple app must be': 'simple'})),
)

application = get_wsgi_application()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

