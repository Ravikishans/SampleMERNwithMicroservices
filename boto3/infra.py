import vpc
import ec2_instances
import alb
import asg
import sys
import json
import boto3
import time
import create_s3_bucket

def deploy_infrastructure():
    with open('config.json') as f:
        config = json.load(f)
    
    vpc.create_vpc(config)
    
    with open('config.json') as f:
        config = json.load(f)

    create_s3_bucket.create_s3_bucket(config)

    # Step 2: Launch EC2 Instances
    instance_hello = ec2_instances.launch_instance_hello(config, config['subnet1_id'])
    instance_profile = ec2_instances.launch_instance_profile(config, config['subnet2_id'])
    instance_frontend= ec2_instances.launch_instance_frontend(config, config['subnet2_id'])

    config.update({
        "instance_id_hello": [instance_hello],
        "instance_id_profile": [instance_profile],
        "instance_id_frontend": [instance_frontend]
    })

    with open('config.json', 'w') as f:
        json.dump(config, f)

    # Step 3: Deploy Application Load Balancer
    elb_arn, elb_dns = alb.deploy_alb(config)
    
    tg_hello = alb.hello_target_group(config)
    tg_profile = alb.profile_target_group(config)
    tg_frontend = alb.frontend_target_group(config)
    
    # Replace these instance IDs with actual IDs of your instances
    instance_hello = config['instance_id_hello']
    instance_profile = config['instance_id_profile']
    instance_frontend = config['instance_id_frontend']
    
    # Register instances to the respective target groups
    alb.register_targets(tg_hello, instance_hello, config)
    alb.register_targets(tg_profile, instance_profile, config)
    alb.register_targets(tg_frontend, instance_frontend, config)
    
    # Create a listener
    alb.create_listener(elb_arn, tg_hello, tg_profile, tg_frontend, config)

    config.update({
        "load_balancer_arn": elb_arn,
        "alb_dns": elb_dns,
        "target_group_hello_arn": tg_hello,
        "target_group_profile_arn": tg_profile,
        "target_group_frontend_arn": tg_frontend
    })


    with open('config.json', 'w') as f:
        json.dump(config, f)
    
    # Step 4: Create Auto Scaling Group
    asg.hello_launch_configuration(config)
    asg.hello_auto_scaling_group(config)
    asg.configure_scaling_policy_hello(config)

    asg.profile_launch_configuration(config)
    asg.profile_auto_scaling_group(config)
    asg.configure_scaling_policy_profile(config)

    asg.frontend_launch_configuration(config)
    asg.frontend_auto_scaling_group(config)
    asg.configure_scaling_policy_frontend(config)

    with open('config.json') as f:
        config = json.load(f)



def tear_down_infrastructure():
    with open('config.json') as f:
        config = json.load(f)

    ec2 = boto3.resource('ec2', region_name=config['region'])
    elbv2 = boto3.client('elbv2', region_name=config['region'])
    asg = boto3.client('autoscaling', region_name=config['region'])

    # Release Elastic IP Addresses
    ec2_client = boto3.client('ec2', region_name=config['region'])
    print("Releasing Elastic IP addresses...")
    eip_addresses = ec2_client.describe_addresses()
    for eip in eip_addresses['Addresses']:
        if 'AssociationId' in eip:
            ec2_client.disassociate_address(AssociationId=eip['AssociationId'])
            ec2_client.release_address(AllocationId=eip['AllocationId'])
            print(f"Released Elastic IP '{eip['PublicIp']}'")
        else:
            print(f"No association found for Elastic IP '{eip['PublicIp']}'")

    # Terminate EC2 instances (hello, profile, frontend)
    for instance_id in config['instance_id_hello'] + config['instance_id_profile'] + config['instance_id_frontend']:
        instance = ec2.Instance(instance_id)
        instance.terminate()
        instance.wait_until_terminated()
        print(f"EC2 instance '{instance_id}' terminated successfully.")

    # Delete load balancer
    elbv2.delete_load_balancer(LoadBalancerArn=config['load_balancer_arn'])
    print(f"Load balancer '{config['load_balancer_arn']}' deleted successfully.")

    time.sleep(30)

    # Delete target groups (hello, profile, frontend)
    elbv2.delete_target_group(TargetGroupArn=config['target_group_hello_arn'])
    print(f"Target group '{config['target_group_hello_arn']}' deleted successfully.")

    elbv2.delete_target_group(TargetGroupArn=config['target_group_profile_arn'])
    print(f"Target group '{config['target_group_profile_arn']}' deleted successfully.")

    elbv2.delete_target_group(TargetGroupArn=config['target_group_frontend_arn'])
    print(f"Target group '{config['target_group_frontend_arn']}' deleted successfully.")

    # Delete Auto Scaling groups (hello, profile, frontend)
    asg.delete_auto_scaling_group(
        AutoScalingGroupName='ravi-asg-backend-hello',
        ForceDelete=True
    )
    print("Hello Auto Scaling Group deleted successfully.")

    asg.delete_auto_scaling_group(
        AutoScalingGroupName='ravi-asg-backend-profile',
        ForceDelete=True
    )
    print("Profile Auto Scaling Group deleted successfully.")

    asg.delete_auto_scaling_group(
        AutoScalingGroupName='ravi-asg-frontend',
        ForceDelete=True
    )
    print("Frontend Auto Scaling Group deleted successfully.")

    time.sleep(30)

    # Delete launch configurations (hello, profile, frontend)
    asg.delete_launch_configuration(
        LaunchConfigurationName='ravi-launch-config-backend-hello'
    )
    print("Hello launch configuration deleted successfully.")

    asg.delete_launch_configuration(
        LaunchConfigurationName='ravi-launch-config-backend-profile'
    )
    print("Profile launch configuration deleted successfully.")

    asg.delete_launch_configuration(
        LaunchConfigurationName='ravi-launch-config-frontend'
    )
    print("Frontend launch configuration deleted successfully.")


    time.sleep(60)
    # Detach and delete Internet Gateway
    print("Detaching and deleting Internet Gateway...")
    if 'igw_id' in config:
        ec2_client.detach_internet_gateway(InternetGatewayId=config['igw_id'], VpcId=config['vpc_id'])
        ec2_client.delete_internet_gateway(InternetGatewayId=config['igw_id'])
        print(f"Internet Gateway '{config['igw_id']}' deleted successfully.")

    time.sleep(15)

    # Delete security group
    ec2.SecurityGroup(config['security_group_id']).delete()
    print(f"Security Group '{config['security_group_id']}' deleted successfully.")

    time.sleep(15)

    # Delete subnets
    ec2.Subnet(config['subnet1_id']).delete()
    ec2.Subnet(config['subnet2_id']).delete()
    print(f"Subnets '{config['subnet1_id']}' and '{config['subnet2_id']}' deleted successfully.")

    # Delete route table
    ec2.RouteTable(config['route_table_id']).delete()
    print(f"Route Table '{config['route_table_id']}' deleted successfully.")
    
    time.sleep(30)

    # Delete S3 bucket
    s3 = boto3.client('s3', region_name=config['region'])
    # Delete S3 bucket
    s3.list_objects_v2(Bucket=config['bucket_name']).get('Contents', [])
    for obj in s3.list_objects_v2(Bucket=config['bucket_name']).get('Contents', []):
        s3.delete_object(Bucket=config['bucket_name'], Key=obj['Key'])
    s3.delete_bucket(Bucket=config['bucket_name'])
    print(f"S3 bucket '{config['bucket_name']}' deleted successfully.")

    time.sleep(30)

    # Delete VPC
    ec2.Vpc(config['vpc_id']).delete()
    print(f"VPC '{config['vpc_id']}' deleted successfully.")

    # # Delete S3 bucket
    # s3 = boto3.client('s3', region_name=config['region'])
    # print("Deleting S3 bucket objects...")
    # for obj in s3.list_objects_v2(Bucket=config['bucket_name']).get('Contents', []):
    #     s3.delete_object(Bucket=config['bucket_name'], Key=obj['Key'])
    # s3.delete_bucket(Bucket=config['bucket_name'])
    # print(f"S3 bucket '{config['bucket_name']}' deleted successfully.")

    # print("Infrastructure tear down completed successfully.")



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_infrastructure.py <deploy|teardown>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "deploy":
        deploy_infrastructure()
    elif command == "teardown":
        tear_down_infrastructure()
    else:
        print("Invalid command. Use 'deploy' or 'teardown'.")
        sys.exit(1)
