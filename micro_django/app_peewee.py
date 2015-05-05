# -*- coding: utf-8 -*-

import os
import sys

from django.conf import settings
from django.http import JsonResponse, HttpResponseNotAllowed, Http404
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application


DEBUG = os.environ.get('DEBUG', 'on') == 'on'

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

if not settings.configured:
    settings.configure(
        DEBUG=DEBUG,
        SECRET_KEY=SECRET_KEY,
        ALLOWED_HOSTS=ALLOWED_HOSTS,
        ROOT_URLCONF=__name__,
        DATABASES={},
        INSTALLED_APPS=(
            'django.contrib.sessions',
        ),
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            '__main__.DbMiddleware'
        ),
        SESSION_ENGINE='django.contrib.sessions.backends.signed_cookies',
    )


import peewee

db = peewee.SqliteDatabase('tasks.db')


class Task(peewee.Model):
    title = peewee.CharField()
    body = peewee.TextField()
    session_id = peewee.CharField()
    is_active = peewee.BooleanField(default=True)

    class Meta:
        database = db


class DbMiddleware(object):

    def process_request(self, request):
        request.db = db
        request.db.connect()

    def process_response(self, request, response):
        try:
            request.db.close()
        except AttributeError:
            pass
        return response


def create_tables():
    db.connect()
    db.create_tables([Task])


def _all(request):
    tasks = Task.select().where(Task.session_id == request.session.session_key)
    return JsonResponse({task.id: {'body': task.body, 'title': task.title, 'active': task.is_active} for task in tasks})


def add(request):
    if request.POST:
        task = Task.create(
            title=request.POST.get('title'),  # Never do shit like this
            body=request.POST.get('body'),
            session_id=request.session.session_key,
        )
        task.save()
        return JsonResponse({'success': 'ok'})
    return HttpResponseNotAllowed([])


def detail(request, id):
    try:
        task = Task.select().where(Task.id == id).where(Task.session_id == request.session.session_key).get()
    except peewee.DoesNotExist:
        raise Http404
    return JsonResponse({'body': task.body, 'title': task.title, 'active': task.is_active})


urlpatterns = (
    url(r'^$', lambda r: JsonResponse({'App': 'peewee'})),
    url(r'^tasks/$', _all),
    url(r'^tasks/add/$', add),
    url(r'^tasks/(?P<id>\d+)/$', detail),
)


application = get_wsgi_application()


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] in ['migrate', 'syncdb']:
        create_tables()
    else:
        from django.core.management import execute_from_command_line

        execute_from_command_line(sys.argv)

