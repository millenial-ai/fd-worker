import boto3
import os
from datetime import datetime
from argparse import ArgumentParser
import time
from utils.aws import get_topic_arn_by_name, get_sqs_url_by_name, ses_send_transaction_confirmation_mail, ses_send_transaction_blocked_mail
from utils.CONST import XGB_FRAUD_THRESHOLD, RCF_FRAUD_THRESHOLD
from utils.aws import create_ses_template, record_transaction_to_feature_store

from utils.processor import RCFProcessor, XGBProcessor
from utils.message import PCARequestMessage, BasicInfoRequestMessage
from utils.cw_logger import CWLogger
            
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

def rcf_score_exceed_threshold(rcf_result):
    return rcf_result.result >= RCF_FRAUD_THRESHOLD

def should_send_mail(
    xgb_result,
    rcf_result,
    **kwargs
):
    return xgb_result.result >= XGB_FRAUD_THRESHOLD or rcf_score_exceed_threshold(rcf_result)

def should_block_transaction(
    xgb_result,
    rcf_result,
    **kwargs
):
    return xgb_result.result >= XGB_FRAUD_THRESHOLD and rcf_score_exceed_threshold(rcf_result)

def str_to_iso_date(d: str):
    return datetime.strptime(d, '%Y-%m-%d %H:%M:%S').isoformat() + 'Z'

def save_to_dynamodb(identifier, status):
    # Create a DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    
    # Specify the table name
    table_name = 'transaction_status'
    
    # Access the DynamoDB table
    table = dynamodb.Table(table_name)
    
    # Define the item to be written to DynamoDB
    item_to_write = {
        'identifier': identifier,
        'status': status
        # Add more attributes as needed
    }
    
    # Write the item to DynamoDB
    response = table.put_item(Item=item_to_write)
    
    # Print the response
    print("Item added successfully:", response)


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


def main(args):
    logger = CWLogger(env=args.env)
    feature_group_name = os.environ.get('FEATURE_STORE_GROUP_NAME', f'transactions-{args.env}') 
    
    while True:
        try:
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
                    logger.log(body_json)
                    msg = BasicInfoRequestMessage(
                        identifier=body_json.get('identifier'), 
                        amt=body_json.get('amt'),
                        lat=body_json.get('lat'),
                        long=body_json.get('long'),
                        city_pop=body_json.get('city_pop'),
                        merch_lat=body_json.get('merch_lat'),
                        merch_long=body_json.get('merch_long'),
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
                    logger.log("RCF Result:")
                    logger.log(rcf_result)
                    
                    xgb_processor = XGBProcessor(endpoint_name=XGB_ENDPOINT, content_type='text/csv')
                    xgb_result = xgb_processor.process(msg)
                    logger.log("XGB Result:")
                    logger.log(xgb_result)
                    
                    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
                    logger.log("Deleted message from SQS")
                    
                    unique_id = f"{msg.identifier}/{msg.tx_date}"
                    if should_block_transaction(xgb_result, rcf_result):
                        logger.log(f"BLOCK Mail is being sent to {msg.recipient_email}")
                        
                        if not args.disable_mail_alert:
                            ses_send_transaction_blocked_mail(
                                msg=msg,
                                recipient_email=msg.recipient_email,
                                xgb_result=xgb_result.result,
                                rcf_result=rcf_result.result
                            )
                            save_to_dynamodb(unique_id, 'fraud')
                    elif should_send_mail(xgb_result, rcf_result):
                        logger.log(f"YES/NO Mail is being sent to {msg.recipient_email}")
                        if not args.disable_mail_alert:
                            ses_send_transaction_confirmation_mail(
                                msg=msg,
                                recipient_email=msg.recipient_email,
                                xgb_result=xgb_result.result,
                                rcf_result=rcf_result.result
                            )
                            save_to_dynamodb(unique_id, 'fraud')
                        
                    else:
                        logger.log("Mail is NOT being sent")
                        save_to_dynamodb(unique_id, 'not_fraud')
                        
                    key_to_remove = ["identifier", "merch_name", "tx_date", "tx_name", "tx_ending", "recipient_email"]
                    
                    record_to_ingest_feature_store = {
                        key: str(body_json[key])
                        for key in body_json
                        if key not in key_to_remove
                    }
                    record_to_ingest_feature_store["trans_date_trans_time"] = str_to_iso_date(body_json["tx_date"])
                    record_to_ingest_feature_store["rcf_isfraud"] = '1' if rcf_score_exceed_threshold(rcf_result) else '0'
                    record_to_ingest_feature_store["rcf_score"] = str(rcf_result.result)
                    
                    record_to_ingest_feature_store["trans_num"] = str(int(time.time()))
                    logger.log("Logging record to Feature Store")
                    record_transaction_to_feature_store(feature_group_name, record_to_ingest_feature_store)
            else:
                print("No messages available")
        except Exception as e:
            logger.log(f"Got error while handling message: {e}")
            logger.log(f"Skipping.")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--env", type=str, default="production", help="Running environment: production/staging/dev")
    parser.add_argument("--disable-mail-alert", action="store_true", help="Disable sending mail")
    args = parser.parse_args()
    
    main(args)