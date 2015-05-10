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
        ),
        SESSION_ENGINE='django.contrib.sessions.backends.signed_cookies',
    )


from sqlite3 import dbapi2 as sqlite3


def connect_db():
    rv = sqlite3.connect('tasks.db', check_same_thread=False)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    sqlite_db = connect_db()
    return sqlite_db


def _all(request):
    db = get_db()
    cur = db.execute('SELECT * FROM task WHERE task.session_id=$1 order by id desc', [request.session.session_key, ])
    tasks = cur.fetchall()
    return JsonResponse({task['id']: {'body': task['body'], 'title': task['title'], 'active': task['is_active']} for task in tasks})


def add(request):
    if request.POST:
        data = request.POST
        db = get_db()
        db.execute('INSERT INTO task (title, body, session_id, is_active) VALUES ($1, $2, $3, 1)',
                   [data.get('title'), data.get('body'), request.session.session_key])
        db.commit()
        return JsonResponse({'success': 'ok'})
    return HttpResponseNotAllowed([])


def detail(request, id):
    db = get_db()
    task = db.execute('SELECT * from task WHERE session_id=$1 AND id=$2 LIMIT 1', [request.session.session_key, id]).fetchall()

    if task:
        task = task.pop()
        return JsonResponse({'body': task['body'], 'title': task['title'], 'active': task['is_active']})
    raise Http404


urlpatterns = (
    url(r'^$', lambda r: JsonResponse({'App': 'sqlite3'})),
    url(r'^tasks/$', _all),
    url(r'^tasks/add/$', add),
    url(r'^tasks/(?P<id>\d+)/$', detail),
)


application = get_wsgi_application()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

