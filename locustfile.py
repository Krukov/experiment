from locust import HttpLocust, TaskSet


def index(l):
    l.client.get("/")

def profile(l):
    l.client.get("/profile")

class TasksBehavior(TaskSet):
    tasks = {index: 5, profile: 5}


class WebsiteTasks(HttpLocust):
    task_set = TasksBehavior
    min_wait=5000
    max_wait=9000
