# -*- coding: utf-8 -*-

import os
import sys
from collections import OrderedDict
from functools import partial

from django.conf import settings
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.db import models
from django.apps.config import AppConfig

APP_LABEL = 'my_app'


class cached_classproperty(object):
    def __init__(self, method):
        self.method = method
        self.cache = None

    def __get__(self, obj, owner):
        if self.cache is None:
            self.cache = self.method(owner)
        return self.cache


class app(AppConfig):
    name = '__main__'
    verbose_name = 'Main'
    label = APP_LABEL
    _urlpatterns = OrderedDict()

    do_not_call_in_templates = True

    @cached_classproperty
    def urlpatterns(cls):
        res = []
        for pattern, methods in cls._urlpatterns.items():

            def view(_methods, request, *args, **kwargs):
                return _methods[request.method]['view'](request, *args, **kwargs)

            view = require_http_methods(methods.keys())(partial(view, methods))
            res.append(url(pattern, view))
        return res

    @classmethod
    def add(cls, regex, view, name=None, method='get'):
        cls._urlpatterns.setdefault(regex, {})[method.upper()] = {'name': name, 'view': view}

    @classmethod
    def route(cls, regex, name=None, methods=('GET', 'POST')):
        def decor(view):
            for method in methods:
                cls.add(regex, view, name, method)
            return view
        return decor

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
        ROOT_URLCONF=app,
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


class Task(models.Model):
    __module__ = '__main__'
    title = models.CharField(max_length=255)
    body = models.TextField(max_length=255)
    session_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = APP_LABEL
        db_table = 'task'


@app.route(r'^tasks/$', methods=['GET'])
def _all(request):
    tasks = Task.objects.filter(session_id=request.session.session_key)
    return JsonResponse({task.id: {'body': task.body, 'title': task.title, 'active': task.is_active} for task in tasks})


@app.route(r'^tasks/$', methods=['POST'])
@app.route(r'^tasks/add/$', methods=['POST'])
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


@app.route(r'^tasks/(?P<id>\d+)/$', methods=['GET'])
def detail(request, id):
    task = get_object_or_404(Task, id=id, session_id=request.session.session_key)
    return JsonResponse({'body': task.body, 'title': task.title, 'active': task.is_active})


application = get_wsgi_application()

if __name__ == "__main__":

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

