import time

from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379', backend='redis://localhost:6379')


@app.task
def add(x, y):
    time.sleep(5)
    return x + y
