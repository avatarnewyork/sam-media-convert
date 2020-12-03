from __future__ import print_function
from urllib.parse import urlparse
import os
import json
import cleanup
import boto3
import logging

# Remove extranious logging messages
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    if(is_media_convert_complete(event)):
        s3_output_file = get_s3_output_file(event)
        job_id = get_job_id(event)
        s3_input_file = get_s3_input_file(job_id)
        return delete_s3_input_file(s3_input_file)
    else:
        logger.info("MediaConvertEvent: job not complete")

def is_media_convert_complete(event):
    try:
        if event['detail']['status'] == "COMPLETE":
            return True    
        else:
            return False
    except KeyError:
        raise Exeception("Invalid MediaConvert Event")


def get_s3_output_file(event):
    logger.info(event)
    try:
        s3_output_file = event['detail']['outputGroupDetails'][0]['outputDetails'][0]['outputFilePaths'][0]
        return s3_output_file
    except:
        raise Exception("No S3 Output File in Event")

def get_s3_input_file(job_id):
    client = get_media_convert_client()
    job = client.get_job(Id=job_id)
    logger.info(job)
    try:
        s3_input_file = job['Job']['Settings']['Inputs'][0]['FileInput']
        return s3_input_file
    except KeyError:
        raise Exception("No job input file")
    pass

def get_job_id(event):
    try:
        job_id = event['detail']['jobId']
        return job_id
    except:
        raise Exception("No jobId")

def delete_s3_input_file(s3_input_file):
    s3_input_file = urlparse(s3_input_file)
    bucket = s3_input_file.netloc
    key = s3_input_file.path
    
    client = boto3.client('s3')
    
    response = client.delete_object(
        Bucket=bucket,
        Key=key.lstrip('/'),
    )
    return response
    
def get_media_convert_client():
    # First get account / region endpoint url
    client = boto3.client('mediaconvert')
    response = client.describe_endpoints(
        MaxResults=1,
        Mode='DEFAULT'
    )
    endpoint_url = response['Endpoints'][0]['Url']
    client = boto3.client('mediaconvert', endpoint_url=endpoint_url)
    return client
