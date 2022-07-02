import json
import os
import boto3
S3_CLIENT = boto3.client('s3')
DYNAMO_CLIENT = boto3.client('dynamodb')
SUBMISSION_TABLE = os.environ.get('SUBMISSION_TABLE')
BUCKET_NAME = os.environ.get('BUCEKT_NAME')


def get_post_url(key: str) -> dict:
    """
    Grab a post url for the submission s3 bucket to
    allow the user to upload a new submission

    Param ( key ): Submissions are stored in the s3 bucket under their 
        submissionId
    Return: presigned URL and metadata
    """

    try:
        response = S3_CLIENT.generate_presigned_post(
                Bucket=BUCKET_NAME,
                Key=key,
                ExpiresIn=3600
        )
        print(f"Received Prseigned POST url: {response}")
        return response
    except Exception as e:
        print(e)


def get_submission(submissionId: str) -> dict:
    """
    Take a submissionId , and see if it exists within the database
    as a form of validation.

    Param ( submissionId ): Id generated for a user's submission
    Return: the Submission within the database if it exists
    """

    try:
        response = DYNAMO_CLIENT.get_item(
            Key={
                'submissionId': submissionId
            }
        )
        return response.get('Item')
    except Exception as e:
        print(e)


def lambda_handler(event, context):

    statusCode = 200
    body = None

    queryStringParams = event.get("queryStringParameters")
    submissionId = queryStringParams.get('submissionId')
    submission = get_submission(submissionId=submissionId)

    if submission:
         body = {
            "submissionInfo": submission,
            "postInfo":get_post_url(submissionId)
        }
    else:
        statusCode = 400
        body = {
            'submissionInfo': 'submissionId invalid'
        }
       

    return {
        "statusCode": statusCode,
        "body": json.dumps(body)
    }