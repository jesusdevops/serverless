import boto3
import json
import os

ecs = boto3.client('ecs')
eventbridge = boto3.client('events')
task_type = os.getenv('taskType')


def publish_event(payload):
    try:
        response = eventbridge.put_events(
            Entries=[
                {
                    'Detail': json.dumps(payload),
                    'DetailType': 'taskLaunched',
                    'EventBusName': 'default',
                    'Source': task_type
                }
            ]
        )
        print('Event published successfully:', response)
    except Exception as e:
        print('Error publishing event:', e)


def lambda_handler(event, context):
    messages = event['Records']
    for msg in messages:
        body = json.loads(msg['body'])
        data = body['data']

        try:
            response = ecs.run_task(
                cluster=os.getenv('CLUSTER_NAME'),
                count=1,
                taskDefinition=os.getenv('TASK_DEFINITION'),
                launchType='FARGATE',
                group=os.getenv('CONTAINER_NAME'),
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': [
                            os.getenv('SUBNET_1'), os.getenv('SUBNET_2'),
                        ],
                        'assignPublicIp': 'ENABLED',
                        'securityGroups': [os.getenv('SECURITY_GROUP')]
                    }
                },
                overrides={
                    'containerOverrides': [
                        {
                            'name': os.getenv('CONTAINER_NAME'),
                            'environment': [
                                {
                                    'name': 'requestData',
                                    'value': json.dumps(data)
                                }
                            ]
                        }
                    ]
                }
            )
            publish_event({'task': response['tasks'][0]['containers'], 'data': data})
            print(f'Task launched')

        except Exception as e:
            print('Error:', str(e))
            raise e

