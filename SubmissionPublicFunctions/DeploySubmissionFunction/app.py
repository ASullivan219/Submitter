import boto3
import json
from io import BytesIO
import zipfile
import os

"""
Sample event Below Given to the lambda function
{
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "1970-01-01T00:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123456789",
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "testConfigRule",
        "bucket": {
          "name": "example-bucket",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::example-bucket"
        },
        "object": {
          "key": "test/key",
          "size": 1024,
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}
"""
S3_CLIENT = boto3.client('s3')


def lambda_handler(event, context):

    bucketInfo = event.get('Records')[0].get('s3')
    submissionKey = bucketInfo.get('object').get('key')
    submissionId = submissionKey.split('.')[0]
    bucketName = bucketInfo.get('bucket').get('name')
    print(f"Now deploying submission {submissionKey} from bucket {bucketName}")
   

    lambdaMetadata = {
        "executionPath":"",
        "submissionId":""
    }

    
    response = S3_CLIENT.get_object(
        Bucket = bucketName,
        Key = submissionKey
    )

    buffer = BytesIO(response.get('Body').read())

    zipped = zipfile.ZipFile(buffer, 'a')

    mainFiles = 0
    executionPath = None
    for fileName in zipped.namelist():
        if "main.py" in fileName or "Main.py" in fileName:
            mainFiles += 1
            executionPath = fileName

    if mainFiles > 1:
        print("Invalid Submission: Too many main.py files")
    else :
        lambdaMetadata["submissionId"] = submissionId
        lambdaMetadata["executionPath"] = executionPath
        print(lambdaMetadata)

    with open(f"/tmp/{submissionId}.json", "w") as tempMetada:
        json.dump(lambdaMetadata, tempMetada)
        tempMetada.close()

    zipped.write(f"/tmp/{submissionId}.json", os.path.basename(f"/tmp/{submissionId}.json"))
    zipped.write( "lambda_function.py")

    print("FILES IN ZIPFILE")
    for filename in zipped.namelist():
        print(filename)

