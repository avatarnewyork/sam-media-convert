import pytest
import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))
from media_convert import app

    
@pytest.fixture()
def file_upload_event():
    
    """ Generates File Upload Event"""
    return {
            "Records": [
                {
                    "eventVersion": "2.1",
                    "eventSource": "aws:s3",
                    "awsRegion": "us-east-1",
                    "eventTime": "2020-08-19T13:18:56.519Z",
                    "eventName": "ObjectCreated:Put",
                    "userIdentity": {
                        "principalId": "AWS:HDJHFD8DKJKDFGFY"
                    },
                    "requestParameters": {
                        "sourceIPAddress": "45.35.111.111"
                    },
                    "responseElements": {
                        "x-amz-request-id": "F81315ACA2A78E86",
                        "x-amz-id-2": "skwoZb0M+gZGWswijGYxUlG/O0MZ2cfl0GWdCGiS5foUH8FjMPlyeTlXeazYOGmmSmlcKJ09ECe9r2KShDnUNUMPaykzi9Nh"
                    },
                    "s3": {
                        "s3SchemaVersion": "1.0",
                        "configurationId": "test-uploads",
                        "bucket": {
                            "name": "test-bucket",
                            "ownerIdentity": {
                                "principalId": "A16H80YXC6P9WD"
                            },
                            "arn": "arn:aws:s3:::test-stage"
                        },
                        "object": {
                            "key": "uploads/unprocessed/test.mov",
                            "size": 4154,
                            "eTag": "281857964fc7b30d992b869e8ddf0f0f",
                            "versionId": "OCsve7FQxlb7sm1xXL2_HDJrSYUo02ZG",
                            "sequencer": "005F3D26C625FD0721"
                        }
                    }
                }
            ]
        
    }

@pytest.fixture()
def s3_input_file():

    """ Input File String """

    return "s3://media-convert/prefix/subdir/uploads/sample.MOV"

@pytest.fixture()
def invalid_s3_event():
    return {"Records": [{"key": "value"}]}

def test_get_s3_file_url(file_upload_event):    
    ret = app.get_s3_file_url(file_upload_event)
    assert ret == "s3://test-bucket/uploads/unprocessed/test.mov"

def test_get_s3_file_url_without_event():
    with pytest.raises(Exception) as e:
        ret = app.get_s3_file_url("")
    assert str(e.value) == 'Missing S3 Event'

def test_get_s3_file_url_invalid_event(invalid_s3_event):
    with pytest.raises(Exception) as e:
        ret = app.get_s3_file_url(invalid_s3_event)
    assert str(e.value) == 'Invalid S3 Event'

def test_get_s3_output_path_without_slash(s3_input_file):
    destination = app.get_s3_output_path(s3_input_file, 'processed')
    assert destination == 's3://media-convert/prefix/subdir/processed/'

def test_get_s3_output_path_with_slash(s3_input_file):
    destination = app.get_s3_output_path(s3_input_file, 'processed/')
    assert destination == 's3://media-convert/prefix/subdir/processed/'

def test_get_settings(s3_input_file):
    settings = app.get_settings(s3_input_file, "")
    test_json = {
            'Inputs': [{
                'FileInput': s3_input_file
            }]
    }
    assert test_json == settings

def test_get_settings_relative_path(s3_input_file):
    settings = app.get_settings(s3_input_file, "processed")
    test_json = {
            'Inputs': [{
                'FileInput': s3_input_file
            }],
            'OutputGroups': [{
                'OutputGroupSettings': {
                    'FileGroupSettings': {
                        'Destination': "s3://media-convert/prefix/subdir/processed/"
                    }
                }
            }]
        }
    assert test_json == settings
    
