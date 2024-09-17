import boto3
import json
import time

def launch_instance_hello(config, subnet_id):
    ec2 = boto3.resource('ec2', region_name=config['region'])

    instances = ec2.create_instances(
        ImageId='ami-05d2438ca66594916',
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.micro',
        KeyName=config['key_pair_name'],
        # SecurityGroupIds=[config['security_group_id']],
        # SubnetId=subnet_id,
        # AssociatePublicIpAddress=True,
        UserData='''#!/bin/bash
        sudo apt-get update -y
        sudo apt-get install docker.io -y
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo docker pull public.ecr.aws/f8g8h5d4/rmernmicrobhello:hello
        sudo docker run -d -p 3001:3001 public.ecr.aws/f8g8h5d4/rmernmicrobhello:hello   
        ''',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': "RmernmicroHello"
                    }
                ]
            }
        ],
        NetworkInterfaces=[
            {
                'SubnetId': subnet_id,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': True,
                'Groups': [config['security_group_id']]
            }
        ]
    )
    
    instance_id = instances[0].id
    print(f"EC2 instance '{instance_id}' launched successfully.")

    # Wait until the instance is running
    ec2.meta.client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance '{instance_id}' is now running.")

    instance = instances[0]
    instance.reload()
    public_ip = instance.public_ip_address
    print(f"Public IP of instance hello '{instance_id}': {public_ip}")
    print(f"open the link for backend hello {public_ip}:3001")
    return instance_id


def launch_instance_profile(config, subnet_id):
    ec2 = boto3.resource('ec2', region_name=config['region'])

    instances = ec2.create_instances(
        ImageId='ami-05d2438ca66594916',
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.micro',
        KeyName=config['key_pair_name'],
        # SecurityGroupIds=[config['security_group_id']],
        # SubnetId=subnet_id,
        # AssociatePublicIpAddress=True,
        UserData='''#!/bin/bash
        sudo apt-get update -y
        sudo apt-get install docker.io -y
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo docker pull public.ecr.aws/f8g8h5d4/rmernmicroprofile:profile
        sudo docker run -d -p 3002:3002 public.ecr.aws/f8g8h5d4/rmernmicrobprofile:profile
        ''',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': "RmernmicroProfile"
                    }
                ]
            }
        ],
        NetworkInterfaces=[
            {
                'SubnetId': subnet_id,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': True,
                'Groups': [config['security_group_id']]
            }
        ]
    )
    
    instance_id = instances[0].id
    print(f"EC2 instance '{instance_id}' launched successfully.")

    # Wait until the instance is running
    ec2.meta.client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance '{instance_id}' is now running.")

    instance = instances[0]
    instance.reload()
    public_ip = instance.public_ip_address
    print(f"Public IP of instance profile '{instance_id}': {public_ip}")
    print(f"open the link for backend profile {public_ip}:3002")

    return instance_id


def launch_instance_frontend(config, subnet_id):
    ec2 = boto3.resource('ec2', region_name=config['region'])

    instances = ec2.create_instances(
        ImageId='ami-05d2438ca66594916',
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.micro',
        KeyName=config['key_pair_name'],
        # SecurityGroupIds=[config['security_group_id']],
        # SubnetId=subnet_id,
        # AssociatePublicIpAddress=True,
        UserData='''#!/bin/bash
        sudo apt-get update -y
        sudo apt-get install docker.io -y
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo docker pull public.ecr.aws/f8g8h5d4/rmernmicrof:frontend
        sudo docker run -d -p 3000:80 public.ecr.aws/f8g8h5d4/rmernmicrof:frontend
        ''',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': "Rmernmicrofrontend"
                    }
                ]
            }
        ],
        NetworkInterfaces=[
            {
                'SubnetId': subnet_id,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': True,
                'Groups': [config['security_group_id']]
            }
        ]
    )
    
    instance_id = instances[0].id
    print(f"EC2 instance '{instance_id}' launched successfully.")

    # Wait until the instance is running
    ec2.meta.client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance '{instance_id}' is now running.")

    instance = instances[0]
    instance.reload()
    public_ip = instance.public_ip_address
    print(f"Public IP of instance frontend'{instance_id}': {public_ip}")
    print(f"open the link for frontend {public_ip}:3000")

    return instance_id

    


if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    instance_hello = launch_instance_hello(config, config['subnet1_id'])
    instance_profile = launch_instance_profile(config, config['subnet2_id'])
    instance_frontend= launch_instance_frontend(config, config['subnet2_id'])

    config.update({
        "instance_id_hello": [instance_hello],
        "instance_id_profile": [instance_profile],
        "instance_id_frontend": [instance_frontend]
    })

    with open('config.json', 'w') as f:
        json.dump(config, f)
