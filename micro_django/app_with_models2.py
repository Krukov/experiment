# -*- coding: utf-8 -*-

import os
import sys

from django.conf import settings
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.db import models
from django.apps.config import AppConfig

APP_LABEL = 'my_app'


class App(AppConfig):
    verbose_name = 'Main'
    label = APP_LABEL

app = App('name', sys.modules[__name__])

DEBUG = os.environ.get('DEBUG', 'on') == 'on'

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tasks.db',
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
            app,
        ),
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ),
    )


class Task(models.Model):
    __module__ = '__main__'
    title = models.CharField(max_length=255)
    body = models.TextField(max_length=255)
    session_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = APP_LABEL
        db_table = 'task'


def _all(request):
    tasks = Task.objects.filter(session_id=request.session.session_key)
    return JsonResponse({task.id: {'body': task.body, 'title': task.title, 'active': task.is_active} for task in tasks})


def add(request):
    if request.POST:
        task = Task(
            title=request.POST.get('title'),  # Never do shit like this
            body=request.POST.get('body'),
            session_id=request.session.session_key,
        )
        task.save()
        return JsonResponse({'success': 'ok'})
    return HttpResponseNotAllowed([])


def detail(request, id):
    task = get_object_or_404(Task, id=id, session_id=request.session.session_key)
    return JsonResponse({'body': task.body, 'title': task.title, 'active': task.is_active})

urlpatterns = (
    url(r'^$', lambda r: JsonResponse({'App with model2': 'task'})),
    url(r'^tasks/$', _all),
    url(r'^tasks/add/$', add),
    url(r'^tasks/(?P<id>\d+)/$', detail),
)


application = get_wsgi_application()


if __name__ == "__main__":

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

