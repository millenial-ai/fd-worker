import boto3
import os
from utils.aws import get_topic_arn_by_name, get_sqs_url_by_name

# Read AWS credentials from environment variables or AWS CLI configuration
session = boto3.Session()

# Create an SQS client
sqs = session.client('sqs')

TOPIC_NAME = os.environ.get('TOPIC_NAME', 'FraudDetectionResult')
SQS_NAME = os.environ.get('SQS_NAME', 'FraudRequestQueue')
RCF_ENDPOINT = os.environ.get('RCF_ENDPOINT', 'custom-rcf')
XGB_ENDPOINT = os.environ.get('XGB_ENDPOINT', 'custom-xgb')

# Replace with the URL of your SQS queue
topic_arn = get_topic_arn_by_name(TOPIC_NAME)
queue_url = get_sqs_url_by_name(SQS_NAME)

# Initialize the SNS client
sns = boto3.client('sns')

while True:
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,  # Change as needed
        WaitTimeSeconds=10      # Change as needed
    )

    if 'Messages' in response:
        for message in response['Messages']:
            # Process the message
            print("Received Message:", message['Body'], type(message['Body']))

            # Delete the processed message from the queue
            receipt_handle = message['ReceiptHandle']
            
            from utils.processor import RCFProcessor, XGBProcessor
            from utils.message import PCARequestMessage, BasicInfoRequestMessage
            
            # msg = PCARequestMessage(identifier=eval(message['Body'])['identifier'], values=eval(message['Body'])['pca'])
            body_json = eval(message['Body'])
            msg = BasicInfoRequestMessage(
                identifier=body_json['identifier'], 
                amt=body_json['amt'],
                lat=body_json['lat'],
                lng=body_json['lng'],
                city_pop=body_json['city_pop'],
                merch_lat=body_json['merch_lat'],
                merch_lng=body_json['merch_lng']
            )
            rcf_processor = RCFProcessor(endpoint_name=RCF_ENDPOINT)
            rcf_result = rcf_processor.process(msg)
            print("RCF Result", rcf_result)
            
            xgb_processor = XGBProcessor(endpoint_name=XGB_ENDPOINT, content_type='text/csv')
            xgb_result = xgb_processor.process(msg)
            print("XGB Result", xgb_result)
            
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
            
            # Message to be published
            message = "There has been a recent activity in your transaction. Here is the detail of our fraud detection model:\n"
            message += f"XGB: {xgb_result.result}\n"
            message += f"RCF: {rcf_result.result}"
            
            # Publish the message to the SNS topic
            response = sns.publish(TopicArn=topic_arn, Message=message)
            
            print("Message published:", response['MessageId'])

    else:
        print("No messages available")
