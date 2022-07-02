import json
import subprocess
"""
Sample event:
{
    "stdin":"",
    "submissionId":"XXX-XXX-XXX"
}
"""

def lambda_handler(event, context):

    metadata = None
    with open(f"{event.get('submissionId')}.json") as file:
        metadata = json.load(file)

    results = {}
    if metadata:
        try:
            completedRun = subprocess.run(
                args=["python3", metadata.get('executionPath')],
                input=event.get('stdin'),
                capture_output=True,
                text=True,
                timeout= 2
            )
            results = {
                "statusCode": "200",
                "stdout": completedRun.stdout,
                "stderr": completedRun.stderr
            }
        except subprocess.TimeoutExpired:
            results = {
                "statusCode": 400,
                "TimeOutException":"true"
            }
        except Exception as e:
            results = {
                "statusCode":400,
                "Exceptions":str(e)
            }
            
    return results
    

