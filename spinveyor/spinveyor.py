import os
import click
import minio
import string
from minio import Minio
from minio.error import BucketAlreadyExists, BucketAlreadyOwnedByYou, NoSuchKey
from minio.error import ResponseError
from progress import Progress
from SV_Worker.tasks import submit_job_to_queue
@click.command()
@click.argument('senfm', type=click.Path(exists=True))
@click.argument('imgData', type=click.Path(exists=True))
@click.argument('recontype')
@click.option("--subjectID", default='defaultSubj', help="Subject ID to use")
@click.option('--verbose', is_flag=True, help="Will print verbose messages.")

def spinveyor(senfm, imgdata, recontype, subjectid, verbose):
    """Driver program to lanch SpinVeyor recons from the commandline."""

    click.echo("SenFM: %s imgData: %s protocol: %s" % (senfm, imgdata, recontype))

    minio_client = Minio(os.environ['MINIO_HOST'], 
        access_key=os.environ['MINIO_ACCESS_KEY'],
        secret_key=os.environ['MINIO_SECRET_KEY'],
        secure=False)
        
    bucket_name = subjectid.lower()

    print('Creating bucket to store data on s3:\\' + os.environ['MINIO_HOST'])
    # Create a bucket for the recon
    # Use the SubjectID to create the bucket name
    create_bucket_in_object_store(minio_client, bucket_name)
    
    print('Copying sense map/field map data...\n')
    # Copy the sense/field map to S3 (minio)
    # Create the object name for the sense map
    copy_file_to_object_store(minio_client, senfm, bucket_name, os.path.basename(senfm))
    print('\n')
    print('Copying imaging data... \n')
    # Copy the imaging data to S3
    # Create the object name for the imaging data
    copy_file_to_object_store(minio_client, imgdata, bucket_name, os.path.basename(imgdata))
    print('\n')
    print('Adding reconstruction to queue...\n')
    # Fire off the recon by sending to the Celery queue
    submit_job_to_queue.delay(recontype, bucket_name, os.path.basename(senfm), os.path.basename(imgdata), subjectid)

def create_bucket_in_object_store(minio_client, bucket):
    try:
        minio_client.make_bucket(bucket, location="us-east-1")
    except BucketAlreadyExists:
        pass
    except BucketAlreadyOwnedByYou:
        pass

def copy_file_to_object_store(minio_client, filename, bucket, objectname):

    # Put a file with progress.
    progress = Progress()
    try:
        with open(filename, 'rb') as file_data:
            file_stat = os.stat(filename)
            minio_client.put_object(bucket, objectname,
                          file_data, file_stat.st_size, progress=progress)
    except ResponseError as err:
        print(err)
        
if __name__ == '__main__':
    spinveyor()