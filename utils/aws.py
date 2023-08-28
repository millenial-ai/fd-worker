import boto3

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