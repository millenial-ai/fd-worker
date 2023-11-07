import boto3
import os
from utils.aws import get_topic_arn_by_name, get_sqs_url_by_name, ses_send_transaction_confirmation_mail, ses_send_transaction_blocked_mail
from utils.CONST import XGB_FRAUD_THRESHOLD, RCF_FRAUD_THRESHOLD
from utils.aws import create_ses_template

from utils.processor import RCFProcessor, XGBProcessor
from utils.message import PCARequestMessage, BasicInfoRequestMessage
from utils.cw_logger import log
            
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
    rcf_result,
    **kwargs
):
    return xgb_result.result >= XGB_FRAUD_THRESHOLD or rcf_result.result >= RCF_FRAUD_THRESHOLD

def should_block_transaction(
    xgb_result,
    rcf_result,
    **kwargs
):
    return xgb_result.result >= XGB_FRAUD_THRESHOLD and rcf_result.result >= RCF_FRAUD_THRESHOLD


# Using same html on purpose
with open('resource/mail_template/transaction_confirmation.html') as f_block,\
    open('resource/mail_template/transaction_confirmation.html') as f_confirm:
    
    blocked_mail_html, confirmation_mail_html = f_block.read(), f_confirm.read()
    
    create_ses_template(
        template_name='TransactionBlocked',
        mail_subject='Transaction blocked',
        mail_html=blocked_mail_html
    )
    create_ses_template(
        template_name='TransactionConfirmation',
        mail_subject='Transaction confirmation required',
        mail_html=confirmation_mail_html
    )



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
            
            # msg = PCARequestMessage(identifier=eval(message['Body'])['identifier'], values=eval(message['Body'])['pca'])
            body_json = eval(message['Body'])
            log(body_json)
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
                recipient_email=body_json.get('recipient_email')
            )
            rcf_processor = RCFProcessor(endpoint_name=RCF_ENDPOINT)
            rcf_result = rcf_processor.process(msg)
            log("RCF Result:")
            log(rcf_result)
            
            xgb_processor = XGBProcessor(endpoint_name=XGB_ENDPOINT, content_type='text/csv')
            xgb_result = xgb_processor.process(msg)
            log("XGB Result:")
            log(xgb_result)

            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

            if should_block_transaction(xgb_result, rcf_result):
                log(f"BLOCK Mail is being sent to {msg.recipient_email}")
                ses_send_transaction_blocked_mail(
                    msg=msg,
                    recipient_email=msg.recipient_email,
                    xgb_result=xgb_result.result,
                    rcf_result=rcf_result.result
                )
            elif should_send_mail(xgb_result, rcf_result):
                log(f"YES/NO Mail is being sent to {msg.recipient_email}")
                ses_send_transaction_confirmation_mail(
                    msg=msg,
                    recipient_email=msg.recipient_email,
                    xgb_result=xgb_result.result,
                    rcf_result=rcf_result.result
                )
            else:
                log("Mail is NOT being sent")
    else:
        print("No messages available")
