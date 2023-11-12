
import boto3
from datetime import datetime
import time

# Initialize the CloudWatch Logs client
client = boto3.client('logs')

class CWLogger():
    def __init__(self, env):
        # Define the log group and log stream names
        self.log_group_name = f'fd-worker/{env}'
        self.log_stream_name = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        self.env = env
        
        try:
            response = client.describe_log_groups(logGroupNamePrefix=self.log_group_name)
            if not response['logGroups']:
                # The log group doesn't exist, so create it
                client.create_log_group(logGroupName=self.log_group_name)
        except client.exceptions.ResourceNotFoundException:
            # The log group doesn't exist, so create it
            client.create_log_group(logGroupName=self.log_group_name)
        
        # Check if the log stream exists
        try:
            response = client.describe_log_streams(logGroupName=self.log_group_name, logStreamNamePrefix=self.log_stream_name)
            if not response['logStreams']:
                # The log stream doesn't exist, so create it
                client.create_log_stream(logGroupName=self.log_group_name, logStreamName=self.log_stream_name)
        except client.exceptions.ResourceNotFoundException:
            # The log stream doesn't exist, so create it
            client.create_log_stream(logGroupName=self.log_group_name, logStreamName=self.log_stream_name)
    
    def is_production(self):
        return self.env == 'production'
        
    def log(self, message, stdout=True):
        if stdout:
            print(message)
        client.put_log_events(
            logGroupName=self.log_group_name,
            logStreamName=self.log_stream_name,
            logEvents=[{'timestamp': int(time.time() * 1000), 'message': str(message)}]
        )
