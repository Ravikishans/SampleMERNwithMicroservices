import boto3
import json

def hello_launch_configuration(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.create_launch_configuration(
        LaunchConfigurationName='ravi-launch-config-backend-hello',
        ImageId='ami-05d2438ca66594916',
        InstanceType='t2.micro',
        KeyName=config["key_pair_name"],
        SecurityGroups=[config['security_group_id']],
        UserData="""#!/bin/bash
        sudo docker pull public.ecr.aws/f8g8h5d4/rmernmicrobhello:hello
        sudo docker run -d -p 3001:3001 public.ecr.aws/f8g8h5d4/rmernmicrobhello:hello
        """
        # public.ecr.aws/f8g8h5d4/rmernmicrobhello:hello
    )

def hello_auto_scaling_group(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='ravi-asg-backend-hello',
        LaunchConfigurationName='ravi-launch-config-backend-hello',
        MinSize=1,
        MaxSize=3,
        VPCZoneIdentifier=f'{config['subnet1_id']},{config['subnet2_id']},{config['subnet3_id']}',
        Tags=[{'Key': 'Name', 'Value': 'ravi-mern-backend-hello', 'PropagateAtLaunch': True}],
        TargetGroupARNs=[config['target_group_hello_arn']]
    )
    print("Auto Scaling Group created successfully.")


def configure_scaling_policy_hello(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.put_scaling_policy(
        AutoScalingGroupName='ravi-asg-backend-hello',
        PolicyName='scale-out',
        PolicyType='TargetTrackingScaling',
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'ASGAverageCPUUtilization'
            },
            'TargetValue': 50.0
        }
    )
    print("Scaling policy configured successfully.")



def profile_launch_configuration(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.create_launch_configuration(
        LaunchConfigurationName='ravi-launch-config-backend-profile',
        ImageId='ami-05d2438ca66594916',
        InstanceType='t2.micro',
        KeyName=config["key_pair_name"],
        SecurityGroups=[config['security_group_id']],
        UserData="""#!/bin/bash
        sudo docker pull public.ecr.aws/f8g8h5d4/rmernmicrobprofile:profile
        sudo docker run -d -p 3002:3002 public.ecr.aws/f8g8h5d4/rmernmicrobprofile:profile
        """
    )

def profile_auto_scaling_group(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='ravi-asg-backend-profile',
        LaunchConfigurationName='ravi-launch-config-backend-profile',
        MinSize=1,
        MaxSize=3,
        VPCZoneIdentifier=f'{config['subnet1_id']},{config['subnet2_id']},{config['subnet3_id']}',
        Tags=[{'Key': 'Name', 'Value': 'ravi-mern-backend-profile', 'PropagateAtLaunch': True}],
        TargetGroupARNs=[config['target_group_profile_arn']]
    )
    print("Auto Scaling Group created successfully.")


def configure_scaling_policy_profile(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.put_scaling_policy(
        AutoScalingGroupName='ravi-asg-backend-profile',
        PolicyName='scale-out',
        PolicyType='TargetTrackingScaling',
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'ASGAverageCPUUtilization'
            },
            'TargetValue': 50.0
        }
    )
    print("Scaling policy configured successfully.")



def frontend_launch_configuration(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.create_launch_configuration(
        LaunchConfigurationName='ravi-launch-config-frontend',
        ImageId='ami-05d2438ca66594916',
        InstanceType='t2.micro',
        KeyName=config["key_pair_name"],
        SecurityGroups=[config['security_group_id']],
        UserData="""#!/bin/bash
        sudo docker pull public.ecr.aws/f8g8h5d4/rmernmicrof:frontend
        sudo docker run -d -p 3000:80 public.ecr.aws/f8g8h5d4/rmernmicrof:frontend
        """
    )

def frontend_auto_scaling_group(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='ravi-asg-frontend',
        LaunchConfigurationName='ravi-launch-config-frontend',
        MinSize=1,
        MaxSize=3,
        VPCZoneIdentifier=f'{config['subnet1_id']},{config['subnet2_id']},{config['subnet3_id']}',
        Tags=[{'Key': 'Name', 'Value': 'ravi-mern-frontend', 'PropagateAtLaunch': True}],
        TargetGroupARNs=[config['target_group_frontend_arn']]
    )
    print("Auto Scaling Group created successfully.")


def configure_scaling_policy_frontend(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.put_scaling_policy(
        AutoScalingGroupName='ravi-asg-frontend',
        PolicyName='scale-out',
        PolicyType='TargetTrackingScaling',
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'ASGAverageCPUUtilization'
            },
            'TargetValue': 50.0
        }
    )
    print("Scaling policy configured successfully.")


if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    hello_launch_configuration(config)
    hello_auto_scaling_group(config)
    configure_scaling_policy_hello(config)

    profile_launch_configuration(config)
    profile_auto_scaling_group(config)
    configure_scaling_policy_profile(config)

    frontend_launch_configuration(config)
    frontend_auto_scaling_group(config)
    configure_scaling_policy_frontend(config)