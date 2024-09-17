import boto3
import json

def deploy_alb(config):
    elbv2 = boto3.client('elbv2', region_name=config['region'])

    load_balancer = elbv2.create_load_balancer(
        Name='ravi-load-balancer',
        Subnets=[config['subnet1_id'],config['subnet2_id'],config['subnet3_id']],
        SecurityGroups=[config['security_group_id']],
        Scheme='internet-facing',
        Tags=[{'Key': 'Name', 'Value': 'ravi-load-balancer'}],
        Type='application'
    )
    elb_arn = load_balancer['LoadBalancers'][0]['LoadBalancerArn']
    print(f"ALB '{elb_arn}' created successfully.")

    response = elbv2.modify_load_balancer_attributes(
        LoadBalancerArn=elb_arn,
        Attributes=[
            {
                'Key': 'load_balancing.cross_zone.enabled',
                'Value': 'true'  # Enable cross-zone load balancing
            }
        ]
    )
    print(f"Response from AWS: {response}")
    print(f"Cross-Zone Load Balancing enabled for ALB '{elb_arn}'.")

    elb_dns = load_balancer['LoadBalancers'][0]['DNSName']  # Get the DNS name
    print(f"ALB DNS Name: {elb_dns}")
    return elb_arn , elb_dns
    
def hello_target_group(config):
    elbv2 = boto3.client('elbv2', region_name=config['region'])

    target_group = elbv2.create_target_group(
        Name='backend-hello-tg',
        Protocol='HTTP',
        Port=3001,
        VpcId=config['vpc_id'],
        HealthCheckProtocol= 'HTTP',
        HealthCheckPort="3001",
        HealthCheckPath="/hello/health",
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=5,
        HealthyThresholdCount=5,
        UnhealthyThresholdCount=2,
        TargetType='instance'
    )
    target_group_hello_arn = target_group['TargetGroups'][0]['TargetGroupArn']
    print(f"hello tg '{target_group_hello_arn}' created successfully")
    return target_group_hello_arn 

def profile_target_group(config):
    elbv2 = boto3.client('elbv2', region_name=config['region'])

    target_group = elbv2.create_target_group(
        Name='backend-profile-tg',
        Protocol='HTTP',
        Port=3002,
        VpcId=config['vpc_id'],
        HealthCheckProtocol= 'HTTP',
        HealthCheckPort="3002",
        HealthCheckPath="/profile/health",
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=5,
        HealthyThresholdCount=5,
        UnhealthyThresholdCount=2,
        TargetType='instance'
    )
    target_group_profile_arn = target_group['TargetGroups'][0]['TargetGroupArn']
    print(f"profile tg '{target_group_profile_arn}' created successfully")
    return target_group_profile_arn 

def frontend_target_group(config):
    elbv2 = boto3.client('elbv2', region_name=config['region'])

    target_group = elbv2.create_target_group(
        Name='frontend-tg',
        Protocol='HTTP',
        Port=3000,
        VpcId=config['vpc_id'],
        HealthCheckProtocol= 'HTTP',
        HealthCheckPort="3000",
        HealthCheckPath="/",
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=5,
        HealthyThresholdCount=5,
        UnhealthyThresholdCount=2,
        TargetType='instance'
    )
    target_group_frontend_arn = target_group['TargetGroups'][0]['TargetGroupArn']
    print(f"frontend tg '{target_group_frontend_arn}' created successfully")
    return target_group_frontend_arn 

def register_targets(target_group_arn, instance_ids, config):
    elbv2 = boto3.client('elbv2', region_name=config['region'])
    
    # Register the EC2 instances as targets
    response=elbv2.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': instance_id} for instance_id in instance_ids]
    )
    print(f"Response from AWS: {response}")
    
    print(f"Targets {instance_ids} registered successfully to Target Group '{target_group_arn}'.")


def create_listener(elb_arn, target_group_hello_arn, target_group_profile_arn, target_group_frontend_arn, config):
    elbv2 = boto3.client('elbv2', region_name=config['region'])
    
    # Create a listener on port 80
    listener = elbv2.create_listener(
        LoadBalancerArn=elb_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[{
            'Type': 'fixed-response',
            'FixedResponseConfig': {
                'MessageBody': 'welcome to load balancer',
                'StatusCode': '200',
                'ContentType': 'text/plain'
            }
        }]
    )
    
    listener_arn = listener['Listeners'][0]['ListenerArn']
    print(f"Listener '{listener_arn}' created successfully.")
    
    # Add path-based routing rules
    elbv2.create_rule(
        ListenerArn=listener_arn,
        Conditions=[
            {
                'Field': 'path-pattern',
                'Values': ['/hello/*']  # For hello service
            }
        ],
        Priority=1,
        Actions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_hello_arn
            }
        ]
    )
    
    elbv2.create_rule(
        ListenerArn=listener_arn,
        Conditions=[
            {
                'Field': 'path-pattern',
                'Values': ['/profile/*']  # For profile service
            }
        ],
        Priority=2,
        Actions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_profile_arn
            }
        ]
    )

    elbv2.create_rule(
        ListenerArn=listener_arn,
        Conditions=[
            {
                'Field': 'path-pattern',
                'Values': ['/frontend/*']  # For frontend service
            }
        ],
        Priority=3,
        Actions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_frontend_arn
            }
        ]
    )

    print("Listener rules created for path-based routing.")
    return listener_arn


if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    elb_arn,elb_dns = deploy_alb(config)
    
    tg_hello = hello_target_group(config)
    tg_profile = profile_target_group(config)
    tg_frontend = frontend_target_group(config)
    
    # Replace these instance IDs with actual IDs of your instances
    instance_hello = config['instance_id_hello']
    instance_profile = config['instance_id_profile']
    instance_frontend = config['instance_id_frontend']
    
    # Register instances to the respective target groups
    register_targets(tg_hello, instance_hello, config)
    register_targets(tg_profile, instance_profile, config)
    register_targets(tg_frontend, instance_frontend, config)
    
    # Create a listener for the 'hello' service (you can do similar for other services)
    # create_listener(elb_arn, tg_hello, config)
    # create_listener(elb_arn,tg_profile,config)
    # create_listener(elb_arn,tg_frontend,config)
    create_listener(elb_arn, tg_hello, tg_profile, tg_frontend, config)

    config.update({
        "load_balancer_arn": elb_arn,
        "alb_dns": elb_dns,
        "target_group_hello_arn": tg_hello,
        "target_group_profile_arn": tg_profile,
        "target_group_frontend_arn": tg_frontend
    })


    with open('config.json', 'w') as f:
        json.dump(config, f)




# DefaultActions=[{
#         'Type': 'forward',
#         'ForwardConfig': {
#             'TargetGroups': [
#                 {'TargetGroupArn': target_group_hello_arn, 'Weight': 1},
#                 {'TargetGroupArn': target_group_profile_arn, 'Weight': 1},
#                 {'TargetGroupArn': target_group_frontend_arn, 'Weight': 1}
#             ],
#             'TargetGroupStickinessConfig': {
#                 'Enabled': False
#             }
#         }
#     }]