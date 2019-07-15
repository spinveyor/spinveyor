import os
import celery

from celery import Celery

app = Celery(include=('tasks'), broker=os.environ['SPINVEYOR_BROKER'], backend=os.environ['SPINVEYOR_BROKER'])
