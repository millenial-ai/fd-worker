import boto3
import os
from utils.aws import get_topic_arn_by_name, get_sqs_url_by_name, ses_send_transaction_confirmation_mail
from utils.CONST import XGB_FRAUD_THRESHOLD

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

def should_send_mail(
    xgb_result,
    **kwargs
):
    return xgb_result.result >= XGB_FRAUD_THRESHOLD

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
                identifier=body_json.get('identifier'), 
                amt=body_json.get('amt'),
                lat=body_json.get('lat'),
                lng=body_json.get('lng'),
                city_pop=body_json.get('city_pop'),
                merch_lat=body_json.get('merch_lat'),
                merch_lng=body_json.get('merch_lng'),
                merch_name=body_json.get('merch_name'),
                tx_name=body_json.get('tx_name'),
                tx_date=body_json.get('tx_date'),
                tx_ending=body_json.get('tx_ending'),
                merchant=body_json.get('merchant'), 
                category=body_json.get('category'),
                city=body_json.get('city'),
                state=body_json.get('state'),
                dob=body_json.get('dob'),
                job=body_json.get('job'),
                recipient_email=body_json.get('recipient_email', 'caohoangtung2001@gmail.com')
            )
            rcf_processor = RCFProcessor(endpoint_name=RCF_ENDPOINT)
            rcf_result = rcf_processor.process(msg)
            print("RCF Result", rcf_result)
            
            xgb_processor = XGBProcessor(endpoint_name=XGB_ENDPOINT, content_type='text/csv')
            xgb_result = xgb_processor.process(msg)
            print("XGB Result", xgb_result)

            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
            
            
            if should_send_mail(xgb_result):
                print("Mail is being sent to", msg.recipient_email)
                ses_send_transaction_confirmation_mail(
                    msg=msg,
                    recipient_email=msg.recipient_email,
                    tx_link_accept='https://0m99smdcz1.execute-api.us-east-1.amazonaws.com/transaction/notify?message=accept transaction',
                    tx_link_decline='https://0m99smdcz1.execute-api.us-east-1.amazonaws.com/transaction/notify?message=reject transaction',
                    xgb_result=xgb_result.result,
                    rcf_result=rcf_result.result
                )
            else:
                print("Mail is NOT being sent")
    else:
        print("No messages available")
