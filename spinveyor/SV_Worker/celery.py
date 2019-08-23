import os
import celery

from celery import Celery
from celery.utils.log import get_task_logger

app = Celery('SV_Worker', broker=os.environ['SPINVEYOR_BROKER'], backend=os.environ['SPINVEYOR_BROKER'], include=['SV_Worker.tasks'])

logger = get_task_logger(__name__)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires = 2592000, # 30 days for result expiration
    result_persistant = True,
    broker_transport_options = {'visibility_timeout', 86400 }, # 24 hours in seconds
    task_acks_late = True,
    worker_prefetch_multiplier=1
)

if __name__ == '__main__':
    app.start()