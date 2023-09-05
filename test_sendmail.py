import os
import boto3
from utils.aws import get_topic_arn_by_name
from string import Template

ses = boto3.client('ses')
sender_email = 'millennium.ai.agent@gmail.com'
recipient_email = 'caohoangtung2001@gmail.com'

with open('resource/mail_template/transaction_confirmation.html') as f_mail_template:
    mail_template_str = f_mail_template.read()
    mail_template = Template(mail_template_str)
    mail_body = mail_template.safe_substitute(
        TX_ENDING='xxyy',
        TX_NAME='Ben L',
        TX_MERCHANT='Store A',
        TX_DATE='04/09/2023',
        TX_AMOUNT='100,000',
        TX_LINK_ACCEPT='https://0m99smdcz1.execute-api.us-east-1.amazonaws.com/transaction/notify?message=accept transaction',
        TX_LINK_DECLINE='https://0m99smdcz1.execute-api.us-east-1.amazonaws.com/transaction/notify?message=reject transaction',
    )
    
    response = ses.send_email(
        Source=sender_email,
        Destination={'ToAddresses': [recipient_email]},
        Message={
            'Subject': {'Data': 'Transaction confirmation required'},
            'Body': {
                'Html': {'Data': mail_body}
            }
        }
    )
    print("Email sent successfully!")
    print(response)
    