# -*- coding: utf-8 -*-

import os
import sys
from types import ModuleType

import django


class Settings(ModuleType):
    DEBUG = os.environ.get('DEBUG', 'on') == 'on'

    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))

    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'tasks.db',
        }
    }
    ALLOWED_HOSTS = ALLOWED_HOSTS
    ROOT_URLCONF = __name__
    MIGRATION_MODULES = {'__main__': 'migrations'}
    
    INSTALLED_APPS = (
        'django.contrib.sessions',
        '__main__'
    )
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

sys.modules['settings'] = Settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

django.setup()

from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.db import models


class Task(models.Model):
    __module__ = '__main__'  # for manage shell 
    title = models.CharField(max_length=255)
    body = models.TextField(max_length=255)
    session_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
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
    url(r'^$', lambda r: JsonResponse({'App': 'django ORM', 'omg': 'Stupid django ORM. It is so slowwwwww'})),
    url(r'^tasks/$', _all),
    url(r'^tasks/add/$', add),
    url(r'^tasks/(?P<id>\d+)/$', detail),
)


application = get_wsgi_application()


if __name__ == "__main__":

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

