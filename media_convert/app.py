from __future__ import print_function
import os
import json
import boto3
import logging

# Remove extranious logging messages
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    s3_file_url = get_s3_file_url(event)

    # First get account / region endpoint url
    client = boto3.client('mediaconvert')
    response = client.describe_endpoints(
        MaxResults=1,
        Mode='DEFAULT'
    )
    endpoint_url = response['Endpoints'][0]['Url']
    client = boto3.client('mediaconvert', endpoint_url=endpoint_url)

    settings = get_settings(s3_file_url, os.environ['DESTINATION_RELATIVE_PATH'])
    
    response = client.create_job(
        AccelerationSettings={
            'Mode': 'DISABLED'
        },
        BillingTagsSource='JOB_TEMPLATE',
        JobTemplate=os.environ['JOB_TEMPLATE_NAME'],
        Role=os.environ['ROLE_ARN'],
        Settings=settings,
    )
    return json.dumps(response, indent=4, sort_keys=True, default=str)


def get_settings(s3_file_url, destination_relative_path):
    if(destination_relative_path):
        destination = get_s3_output_path(s3_file_url, destination_relative_path)
        settings = {
            'Inputs': [{
                'FileInput': s3_file_url
            }],
            'OutputGroups': [{
                'OutputGroupSettings': {
                    'FileGroupSettings': {
                        'Destination': destination
                    }
                }
            }]
        }
    else:
        settings = {
            'Inputs': [{
                'FileInput': s3_file_url
            }]
        }
    return settings
        
def get_head_object():
    pass

def get_s3_file_url(event):
    if 'Records' not in event:
        raise Exception("Missing S3 Event")
    try:
        s3_key = event['Records'][0]['s3']['object']['key']
        bucket = event['Records'][0]['s3']['bucket']['name']
    except KeyError:
        raise Exception("Invalid S3 Event")
    
    return 's3://' + bucket + '/' + s3_key

def get_s3_output_path(s3_input_file, relative_path):
    destination = s3_input_file.rsplit('/', 2)[0] + '/' + relative_path
    return os.path.join(destination, '') #always with trailing slash

