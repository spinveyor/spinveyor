import os
import celery

from celery import Celery

app = Celery(include=('tasks',))
