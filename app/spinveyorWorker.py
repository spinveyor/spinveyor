import os
import hashlib
import celery 

from io import BytesIO
from urllib.parse import urlparse
from celery.utils.log import get_task_logger
from minio import Minio
from minio.error import BucketAlreadyExists, BucketAlreadyOwnedByYou, NoSuchKey
from worker import app
from celery import Celery

app = Celery(include=('tasks'), broker=os.environ['SPINVEYOR_BROKER'], backend=os.environ['SPINVEYOR_BROKER'])

logger = get_task_logger(__name__)

@app.task(bind=True, name='submit_job_to_queue', queue='spinveyor')
def submit_job_to_queue(recontype, bucket, senfm, imgdata, subjectID):
    # Start by forming the nextflow command
    s3urlSenMap = 's3://' + os.environ['MINIO_HOST'] + '/' + bucket + '/' + senfm
    s3urlImgData = 's3://' + os.environ['MINIO_HOST'] + '/' + bucket + '/' + imgdata
    nfCommand = 'nextflow run ' + 'recon' + recontype + '.nf ' + ' --senfm ' + s3urlSenMap + ' --imgData ' + s3urlImgData + ' --subjectID ' + subjectID

    print(s3urlSenMap)
    print(s3urlImgData)
    print(nfCommand)