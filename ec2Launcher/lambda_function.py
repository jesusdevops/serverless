import boto3
import os

region_name = os.getenv("region")
ami_id = os.getenv("ami_id")
instance_type = os.getenv("instance_type")
key_name = os.getenv("key_name")
subnet_id = os.getenv("subnet_id")
security_group_ids = [os.getenv("security_id")]
user_data_script_path = os.getenv("user_data_script_path")
iam_instance_profile = os.getenv("iam_instance_profile")
volume_size = os.getenv("volume_size")
ec2_client = boto3.client('ec2', region_name=region_name)


def launch_ec2_instance():
    with open(user_data_script_path, 'r') as script_file:
        user_data_script = script_file.read()
    encoded_value = f"<powershell>{user_data_script}</powershell><persist>true</persist>"

    try:
        response = ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            SubnetId=subnet_id,
            SecurityGroupIds=security_group_ids,
            MinCount=1,
            MaxCount=1,
            UserData=encoded_value,
            InstanceInitiatedShutdownBehavior='terminate',
            IamInstanceProfile={
                'Arn': iam_instance_profile
            },
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'VolumeSize': volume_size,
                        'VolumeType': 'gp2',
                        'DeleteOnTermination': True,
                    },
                },
            ]
        )
        instance_id = response['Instances'][0]['InstanceId']
        print(f"Instance {instance_id} launched successfully.")
        return instance_id
    except Exception as e:
        print(f"Error launching instance: {e}")
        return None


def lambda_handler(event, context):
    launch_ec2_instance()
    return {
        'statusCode': 200,
        'status': 'OK',
        'body': {}
    }
