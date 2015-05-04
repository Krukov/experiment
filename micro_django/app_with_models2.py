# -*- coding: utf-8 -*-

import os
import sys

from django.conf import settings
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404

from django.db import models
from django.forms.models import model_to_dict

APP_LABEL = 'my_app'
from django.apps.config import AppConfig


class app(AppConfig):
    name = '__main__'
    verbose_name = 'Main'
    label = APP_LABEL


DEBUG = os.environ.get('DEBUG', 'on') == 'on'

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'app_models2.db',
    }
}

if not settings.configured:
    settings.configure(
        DEBUG=DEBUG,
        SECRET_KEY=SECRET_KEY,
        ALLOWED_HOSTS=ALLOWED_HOSTS,
        ROOT_URLCONF=__name__,
        DATABASES=DATABASES,
        MIGRATION_MODULES={APP_LABEL: 'migrations'},
        INSTALLED_APPS=(
            'django.contrib.sessions',
            '__main__.app',
        ),
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ),
    )


class Book(models.Model):
    __module__ = '__main__'

    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    description = models.TextField(max_length=1023)

    class Meta:
        app_label = APP_LABEL


def detail_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return JsonResponse(model_to_dict(book))


urlpatterns = (
    url(r'^$', lambda r: JsonResponse({'App with model2': 'book'})),
    url(r'^book/(?P<pk>\d+)/$', detail_view),
)


application = get_wsgi_application()


if __name__ == "__main__":

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

