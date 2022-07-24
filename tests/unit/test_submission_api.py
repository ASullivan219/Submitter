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
    ## In the future we can have the event API functions create submissions
    ## Rather than placing an arbitrary value within the Submission table
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
        
    yield {
        "queryStringParameters":{
            "submissionId": uniqueId
        }
    }

    ## Cleanup the UUID Placed within the function
    try:
        response = DYNAMO_CLIENT.delete_item(
            TableName = os.environ.get('SUBMISSION_TABLE'),
            Key = {
                'submissionId':{
                    'S': uniqueId
                }
            }
        )
        print(f"[DELETE RESPONSE] {response}")
    except Exception as e:
        print(e)

def test_success_code(valid_api_event):
    print(os.environ.get('SUBMISSION_TABLE'))

    ret = app.lambda_handler(valid_api_event, "")
    assert ret.get('statusCode') == 200
    body = json.loads(ret.get('body'))
    print(body)
    assert body.get('postInfo') is not None
