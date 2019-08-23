import os
import celery 
import subprocess

from celery import Celery
from subprocess import call

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
                subjectID + ' --protonHome ' + protonHome + ' --outDir ' + s3urlOutDir)
                
    workDir = protonHome + '/spinveyor/recon'
    print(s3urlSenMap)
    print(s3urlImgData)
    print(nfCommand)
    call(nfCommand, shell=True, cwd=workDir)
    