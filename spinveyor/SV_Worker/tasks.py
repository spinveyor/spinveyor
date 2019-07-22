import os
import celery 
import subprocess

from celery import Celery
from subprocess import call

app = Celery('SV_Worker', broker=os.environ['SPINVEYOR_BROKER'], backend=os.environ['SPINVEYOR_BROKER'])

# set a 12 hour hard limit and a 10 hour soft time limit
@app.task(time_limit=43200, soft_time_limit=36000)
def submit_job_to_queue(recontype, bucket, senfm, imgdata, subjectID):
    # Start by forming the nextflow command
    protonHome = os.environ['PROTON_HOME']
    nextflowBin = os.environ['NEXTFLOW_BIN']
    s3urlSenMap = 's3://' + bucket + '/' + senfm
    s3urlImgData = 's3://' + bucket + '/' + imgdata
    nfCommand = (nextflowBin + ' run ' + 'recon' + recontype + '.nf ' + ' --senfm ' +
                s3urlSenMap + ' --imgData ' + s3urlImgData + ' --subjectID ' + 
                subjectID + ' --protonHome ' + protonHome)
    workDir = protonHome + '/spinveyor/recon'
    print(s3urlSenMap)
    print(s3urlImgData)
    print(nfCommand)
    call(nfCommand, shell=True, cwd=workDir)
    