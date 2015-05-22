#!/usr/bin/python2.7

import random
import string

from locust import HttpLocust, TaskSet, task


class Tasks(TaskSet):

    @task(5)
    def all_tasks(self):
        self.client.get('/tasks')

    @task(5)
    def task_by_id(self):
        for i in range(10):
            self.client.get('/tasks/%s' % i, name='/tasks/[id]')

    @task(10)
    def add_tasks(self):
        self.client.post('/tasks/add',
                         {
                             'title': ''.join([random.choice(string.ascii_letters) for _ in xrange(32)]),
                             'body': ''.join([random.choice(string.ascii_letters) for _ in xrange(100)])
                         })


class WebsiteTasks(HttpLocust):
    task_set = Tasks
    min_wait = 5000
    max_wait = 9000
