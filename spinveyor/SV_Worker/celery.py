import os
import celery

from celery import Celery
from celery.utils.log import get_task_logger

app = Celery('SV_Worker', broker=os.environ['SPINVEYOR_BROKER'], backend=os.environ['SPINVEYOR_BROKER'], include=['SV_Worker.tasks'])

logger = get_task_logger(__name__)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()