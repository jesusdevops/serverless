import boto3
import json
from botocore.exceptions import ClientError
import os

email_source = os.getenv('email_source')
CHARSET = "utf-8"


def lambda_handler(event, context):
    recipients = event['detail']['recipients']
    message = event['detail']['message']
    body = event['detail']['body']

    return {
        'statusCode': 200,
        'body': json.dumps(send_mail(message, recipients, body))
    }


def send_mail(message, recipients, body):
    client = boto3.client("ses")
    try:
        response = client.send_email(
            Source=email_source,
            Destination={
                'ToAddresses': recipients,
            },
            Message={
                'Subject': {
                    'Data': message,
                    'Charset': CHARSET
                },
                'Body': {
                    'Text': {
                        'Data': body,
                        'Charset': CHARSET
                    }
                }
            },

        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    else:
        print(f"Email sent. Message ID: {response['MessageId']}")

    return response

