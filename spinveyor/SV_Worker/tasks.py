import os
import celery 
import subprocess

from celery import app
from subprocess import call

@app.task
def submit_job_to_queue(recontype, bucket, senfm, imgdata, subjectID):
    # Start by forming the nextflow command
    protonHome = os.environ['PROTON_HOME']
    s3urlSenMap = 's3://' + os.environ['MINIO_HOST'] + '/' + bucket + '/' + senfm
    s3urlImgData = 's3://' + os.environ['MINIO_HOST'] + '/' + bucket + '/' + imgdata
    nfCommand = ('nextflow run ' + 'recon' + recontype + '.nf ' + ' --senfm ' +
                s3urlSenMap + ' --imgData ' + s3urlImgData + ' --subjectID ' + 
                subjectID + ' --protonHome ' + protonHome)

    print(s3urlSenMap)
    print(s3urlImgData)
    print(nfCommand)
    call(nfCommand)