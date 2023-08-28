import boto3

topic_arn = 'arn:aws:sns:us-east-1:348490654799:FraudDetectionResult'

# Initialize the SNS client
sns = boto3.client('sns')

# Message to be published
message = "Hello from Python script!"

# Publish the message to the SNS topic
response = sns.publish(TopicArn=topic_arn, Message=message)

print("Message published:", response['MessageId'])
