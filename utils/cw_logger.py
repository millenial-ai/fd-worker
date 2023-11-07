
import boto3
from datetime import datetime
import time

# Initialize the CloudWatch Logs client
client = boto3.client('logs')

# Define the log group and log stream names
log_group_name = 'fd-worker'
log_stream_name = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")


try:
    response = client.describe_log_groups(logGroupNamePrefix=log_group_name)
    if not response['logGroups']:
        # The log group doesn't exist, so create it
        client.create_log_group(logGroupName=log_group_name)
except client.exceptions.ResourceNotFoundException:
    # The log group doesn't exist, so create it
    client.create_log_group(logGroupName=log_group_name)

# Check if the log stream exists
try:
    response = client.describe_log_streams(logGroupName=log_group_name, logStreamNamePrefix=log_stream_name)
    if not response['logStreams']:
        # The log stream doesn't exist, so create it
        client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
except client.exceptions.ResourceNotFoundException:
    # The log stream doesn't exist, so create it
    client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)

# try:
#     # Create the log group (if it doesn't exist)
#     client.create_log_group(logGroupName=log_group_name)
    
#     # Create the log stream (if it doesn't exist)
#     client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
# except Exception as e:
#     print(e)
#     pass

def log(message, stdout=True):
    if stdout:
        print(message)
    client.put_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        logEvents=[{'timestamp': int(time.time() * 1000), 'message': str(message)}]
    )
