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


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

engine = create_engine('sqlite:///tasks.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    body = Column(String(255))
    session_id = Column(String(255))
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return "<Task>(id=%s, title=%s)"


class DbMiddleware(object):

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        db_session.remove()
        return response


def _all(request):
    tasks = Task.query.filter(Task.session_id == request.session.session_key)
    return JsonResponse({task.id: {'body': task.body, 'title': task.title, 'active': task.is_active} for task in tasks})


def add(request):
    if request.POST:
        task = Task(
            title=request.POST.get('title'),  # Never do shit like this
            body=request.POST.get('body'),
            session_id=request.session.session_key,
        )
        db_session.add(task)
        db_session.commit()
        return JsonResponse({'success': 'ok'})
    return HttpResponseNotAllowed([])


def detail(request, id):
    task = Task.query.filter(Task.id == id).filter(Task.session_id == request.session.session_key).first()
    if task:
        return JsonResponse({'body': task.body, 'title': task.title, 'active': task.is_active})
    raise Http404


urlpatterns = (
    url(r'^$', lambda r: JsonResponse({'App': 'peewee'})),
    url(r'^tasks/$', _all),
    url(r'^tasks/add/$', add),
    url(r'^tasks/(?P<id>\d+)/$', detail),
)


application = get_wsgi_application()


if __name__ == "__main__":

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

