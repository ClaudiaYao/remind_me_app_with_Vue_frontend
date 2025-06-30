import boto3
import config

# this code could print out the sagemaker job's debugging information

# Initialize Boto3 logs client
logs_client = boto3.client(
    "logs",
    aws_access_key_id = config.S3_ACCESS_KEY_ID,
    aws_secret_access_key= config.S3_SECRET_ACCESS_KEY,
    region_name=config.AWS_REGION
)


response = logs_client.describe_log_streams(
    logGroupName='/aws/sagemaker/TrainingJobs',
    logStreamNamePrefix='train-d9aa357c-20d1-704c-3877-63edc40201bd-1747027021'         # change to your sagemaker job name
)

stream_name = ""
for stream in response['logStreams']:
    stream_name = stream['logStreamName']
    print("LogStreamName:", stream['logStreamName'])
    break

response = logs_client.get_log_events(
    logGroupName='/aws/sagemaker/TrainingJobs',
    logStreamName=stream_name,
    startFromHead=True
)

print("\n****************************************")
for event in response['events']:
    print(event['message'])
print("\n****************************************")


