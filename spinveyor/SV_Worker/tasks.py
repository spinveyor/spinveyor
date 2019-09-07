import os
import celery 
import subprocess

from celery import Celery
from subprocess import call
from minio import Minio
from minio.error import BucketAlreadyExists, BucketAlreadyOwnedByYou, NoSuchKey
from minio.error import ResponseError

app = Celery('SV_Worker', broker=os.environ['SPINVEYOR_BROKER'], backend=os.environ['SPINVEYOR_BROKER'])

# set a 24 hour hard limit and a 22 hour soft time limit
@app.task(time_limit=86400, soft_time_limit=79200)
def submit_job_to_queue(recontype, bucket, senfm, imgdata, subjectID):
    # Start by forming the nextflow command
    protonHome = os.environ['PROTON_HOME']
    nextflowBin = os.environ['NEXTFLOW_BIN']
    outBucket = os.environ['SPINVEYOR_OUTPUT_BUCKET']
    s3urlSenMap = 's3://' + bucket + '/' + senfm
    s3urlImgData = 's3://' + bucket + '/' + imgdata
    s3urlOutDir = 's3://' + outBucket
    nfCommand = (nextflowBin + ' run ' + 'recon' + recontype + '.nf ' + ' --senfm ' +
                s3urlSenMap + ' --imgData ' + s3urlImgData + ' --subjectID ' + 
                subjectID + ' --protonHome ' + protonHome + ' --outDir ' + s3urlOutDir 
                + ' --with-report --with-timeline timeline.html') 
                
    workDir = protonHome + '/spinveyor/recon'
    print(s3urlSenMap)
    print(s3urlImgData)
    print(nfCommand)
    call(nfCommand, shell=True, cwd=workDir)
    # Now I want to push the nextflow report and timeline to s3
    minio_client = Minio(os.environ['MINIO_HOST'], 
                         access_key=os.environ['MINIO_ACCESS_KEY'],
                         secret_key=os.environ['MINIO_SECRET_KEY'],
                         secure=False)
    copy_file_to_object_store(minio_client, workDir + '/report.html', outBucket, 'report.html')
    copy_file_to_object_store(minio_client, workDir + '/timeline.html', outBucket, 'timeline.html')


def copy_file_to_object_store(minio_client, filename, bucket, objectname):
    try:
        with open(filename, 'rb') as file_data:
            file_stat = os.stat(filename)
            minio_client.put_object(bucket, objectname,
                          file_data, file_stat.st_size)
    except ResponseError as err:
        print(err)
    
    