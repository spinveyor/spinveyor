import os
import celery 
import subprocess

from celery import Celery
from subprocess import call

app = Celery('SV_Worker', broker=os.environ['SPINVEYOR_BROKER'], backend=os.environ['SPINVEYOR_BROKER'])

@app.task
def submit_job_to_queue(recontype, bucket, senfm, imgdata, subjectID):
    # Start by forming the nextflow command
    protonHome = os.environ['PROTON_HOME']
    nextflowBin = os.environ['NEXTFLOW_BIN']
    s3urlSenMap = 's3://' + os.environ['MINIO_HOST'] + '/' + bucket + '/' + senfm
    s3urlImgData = 's3://' + os.environ['MINIO_HOST'] + '/' + bucket + '/' + imgdata
    nfCommand = (nextflowBin + ' run ' + 'recon' + recontype + '.nf ' + ' --senfm ' +
                s3urlSenMap + ' --imgData ' + s3urlImgData + ' --subjectID ' + 
                subjectID + ' --protonHome ' + protonHome)

    print(s3urlSenMap)
    print(s3urlImgData)
    print(nfCommand)
    call(nfCommand)