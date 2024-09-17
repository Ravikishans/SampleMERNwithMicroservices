import boto3
import json

def create_vpc(config):
    # Initialize Boto3 clients
    ec2 = boto3.client('ec2')
    autoscaling = boto3.client('autoscaling')

    # Create VPC, Subnets, etc.
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc['Vpc']['VpcId']


    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})

    availability_zones = ec2.describe_availability_zones()['AvailabilityZones']


    subnet1 = ec2.create_subnet(
            CidrBlock='10.0.1.0/24', 
            VpcId=vpc_id, 
            AvailabilityZone=availability_zones[0]['ZoneName']
        )
    subnet2 = ec2.create_subnet(
            CidrBlock='10.0.2.0/24', 
            VpcId=vpc_id, 
            AvailabilityZone=availability_zones[1]['ZoneName']
        )
    subnet3 = ec2.create_subnet(
            CidrBlock='10.0.3.0/24', 
            VpcId=vpc_id, 
            AvailabilityZone=availability_zones[2]['ZoneName']
        )

    subnet1_id = subnet1['Subnet']['SubnetId']
    subnet2_id = subnet2['Subnet']['SubnetId']
    subnet3_id = subnet3['Subnet']['SubnetId']
    print(f"Subnets '{subnet1_id}' and '{subnet2_id}' and '{subnet3_id}' created successfully.")

    ec2.modify_subnet_attribute(SubnetId=subnet1_id, MapPublicIpOnLaunch={'Value': True})
    ec2.modify_subnet_attribute(SubnetId=subnet2_id, MapPublicIpOnLaunch={'Value': True})
    ec2.modify_subnet_attribute(SubnetId=subnet3_id, MapPublicIpOnLaunch={'Value': True})


    igw_response = ec2.create_internet_gateway()
    igw_id = igw_response['InternetGateway']['InternetGatewayId']
    print(f"Internet Gateway '{igw_id}' created successfully.")

    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print(f"Internet Gateway '{igw_id}' attached to VPC '{vpc_id}'.")

    route_table_response = ec2.create_route_table(VpcId=vpc_id)    
    route_table_id = route_table_response['RouteTable']['RouteTableId']
    print(f"Route Table '{route_table_id}' created successfully.")

    ec2.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )
    print(f"Route to Internet Gateway '{igw_id}' created successfully.")

    ec2.associate_route_table(SubnetId=subnet1_id, RouteTableId=route_table_id)
    ec2.associate_route_table(SubnetId=subnet2_id, RouteTableId=route_table_id)
    print(f"Route Table '{route_table_id}' associated with subnets.")


    # Create Security Group
    security_group_response = ec2.create_security_group(
        GroupName='rmern-sg',
        Description='mernmicro',
        VpcId = vpc_id
    )
    sg = security_group_response['GroupId']
        # Allow inbound traffic on port 80 (HTTP) and 22 (SSH)
        
    # Define rules
    ingress_rules = [
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 3000,
            'ToPort': 3000,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 3001,
            'ToPort': 3001,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 3002,
            'ToPort': 3002,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
        
    egress_rules = [
        {
            'IpProtocol': '-1',  # Represents all protocols
            'FromPort': -1,      # Represents all ports
            'ToPort': -1,        # Represents all ports
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]

        # Add ingress rules
    for rule in ingress_rules:
        try:
            ec2.authorize_security_group_ingress(GroupId=sg, IpPermissions=[rule])
            print(f"Ingress rule {rule} added successfully.")
        except ec2.exceptions.ClientError as e:
            if 'InvalidPermission.Duplicate' in str(e):
                print(f"Ingress rule {rule} already exists.")
            else:
                raise

        # Add egress rules
    for rule in egress_rules:
        try:
            ec2.authorize_security_group_egress(GroupId=sg, IpPermissions=[rule])
            print(f"Egress rule {rule} added successfully.")
        except ec2.exceptions.ClientError as e:
            if 'InvalidPermission.Duplicate' in str(e):
                print(f"Egress rule {rule} already exists.")
            else:
                raise

    # Update config with new resources
    config.update({
        "vpc_id": vpc_id,
        "subnet1_id": subnet1_id,
        "subnet2_id": subnet2_id,
        "subnet3_id": subnet3_id,
        "igw_id": igw_id,
        "route_table_id": route_table_id,
        "security_group_id": sg
    })

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)
    create_vpc(config)