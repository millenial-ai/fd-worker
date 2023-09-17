import boto3
import os
import boto3
from string import Template
from .message import Message

ses = boto3.client('ses')

def get_topic_arn_by_name(topic_name):
    # Initialize the SNS client
    sns_client = boto3.client('sns')

    # List topics to find the topic ARN by name
    response = sns_client.list_topics()
    topics = response.get('Topics', [])

    for topic in topics:
        if topic_name in topic['TopicArn']:
            return topic['TopicArn']

    return None  # Topic with the given name not found

def get_sqs_url_by_name(queue_name):
    # Initialize the SQS client
    sqs_client = boto3.client('sqs')

    # List queues to find the queue URL by name
    response = sqs_client.list_queues(QueueNamePrefix=queue_name)
    queues = response.get('QueueUrls', [])

    if queues:
        return queues[0]  # Return the URL of the first queue with the matching name

    return None  # Queue with the given name not found

def get_default_sender_email():
    return 'millennium.ai.agent@gmail.com'

def ses_send_mail_template(
    msg: Message,
    recipient_email: str,
    mail_template_path: str,
    mail_title: str,
    sender_email: str = get_default_sender_email(),
    mail_body_extra_args: dict = {},
    **kwargs
):
    with open(mail_template_path) as f_mail_template:
        mail_template_str = f_mail_template.read()
        mail_template = Template(mail_template_str)
        print("extra args", kwargs.get('mail_body_extra_args', {}))
        mail_body = mail_template.safe_substitute(
            TX_ENDING=msg.tx_ending,
            TX_NAME=msg.tx_name,
            TX_MERCHANT=msg.merch_name,
            TX_DATE=msg.tx_date,
            TX_AMOUNT=msg.amt,
            **mail_body_extra_args
        )
        try:
            mail_body += f"<p>XGB: {kwargs.get('xgb_result')}</p>"
            mail_body += f"<p>RCF: {kwargs.get('rcf_result')}</p>"
        except:
            pass
        
        response = ses.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': mail_title},
                'Body': {
                    'Html': {'Data': mail_body}
                }
            }
        )
        print("Email sent successfully!")

def ses_send_transaction_confirmation_mail(
        msg: Message,
        recipient_email: str,
        tx_link_accept: str,
        tx_link_decline: str,
        sender_email: str = get_default_sender_email(),
        mail_template_path: str = 'resource/mail_template/transaction_confirmation.html',
        **kwargs
    ):
    ses_send_mail_template(
        msg,
        recipient_email,
        mail_template_path,
        mail_title='Transaction confirmation required',
        mail_body_extra_args={
            'TX_LINK_ACCEPT': tx_link_accept,
            'TX_LINK_DECLINE': tx_link_decline
        },
        **kwargs
    )

def ses_send_transaction_blocked_mail(
        msg: Message,
        recipient_email: str,
        sender_email: str = get_default_sender_email(),
        mail_template_path: str = 'resource/mail_template/transaction_block_notice.html',
        **kwargs
    ):
    ses_send_mail_template(
        msg,
        recipient_email,
        mail_template_path,
        mail_title='Transaction blocked',
        **kwargs
    )