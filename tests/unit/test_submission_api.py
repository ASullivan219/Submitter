import json
import pytest 
import boto3
import os
import uuid
import sys

sys.path.insert(0, os.path.join("..",".."))
import SubmissionPublicFunctions.GetSubmission.app as app

DYNAMO_CLIENT = boto3.client('dynamodb')

@pytest.fixture()
def valid_api_event():

    ## Set up the environment Variables expercted by the function
    ## TODO: Find a way to implement dynamic env. vars by deployment stage

    os.environ.setdefault('SUBMISSION_TABLE','submissionTable-dev')
    os.environ.setdefault('BUCKET_NAME', 'submitter-submissions-bucket-dev')
    os.environ.setdefault('DEBUG', 'true')

    ## Generate a UUID and insert into database as a submission
    uniqueId = str(uuid.uuid4())
    try:
        DYNAMO_CLIENT.put_item(
            TableName = os.environ.get('SUBMISSION_TABLE'),
            Item = {
                'submissionId':{
                    'S': uniqueId
                }
            }
        )
    except Exception as e:
        print(e)
        
    return {
        "queryStringParameters":{
            "submissionId": uniqueId
        }
    }

def test_success_code(valid_api_event):
    print(os.environ.get('SUBMISSION_TABLE'))

    ret = app.lambda_handler(valid_api_event, "")
    assert ret.get('statusCode') == 200
    assert os.environ.get('SUBMISSION_TABLE') == 'submissionTable-dev'
    assert os.environ.get('BUCKET_NAME') == 'submitter-submissions-bucket-dev'
    assert os.environ.get('DEBUG') == 'true'