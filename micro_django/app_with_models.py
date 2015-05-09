# -*- coding: utf-8 -*-

import os
import sys

from django.conf import settings
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.db import models


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
        MIGRATION_MODULES={'__main__': 'migrations'},
        INSTALLED_APPS=(
            'django.contrib.sessions',
            '__main__'
        ),
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ),
    )


from django.apps import apps
apps.populate(settings.INSTALLED_APPS)
# -1 We are pre-loading apps, it is necessary to
#  after this
# >python app_with_models.py migrate'
# Operations to perform:
#   Synchronize unmigrated apps: __main__
#   ...
# >python app_with_models.py makemigrations __main__
# Migrations for '__main__':
#   0001_initial.py:
#     - Create model Task
#  but then when we are run migrate there are nothing happens
# Ok ... adding MIGRATION_MODULES at setting configure
# SUCCESS   Applying __main__.0001_initial... OK


class Task(models.Model):
    __module__ = '__main__'
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

