```markdown
# MERN Application with AWS Microservices

## Overview

This project demonstrates how to deploy a MERN (MongoDB, Express, React, Node.js) application with microservices on AWS. It uses Docker, AWS Lambda, Amazon EKS, and other AWS services to ensure scalability, availability, and maintainability.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup AWS Environment](#setup-aws-environment)
3. [Prepare the MERN Application](#prepare-the-mern-application)
4. [Version Control with AWS CodeCommit](#version-control-with-aws-codecommit)
5. [Continuous Integration with Jenkins](#continuous-integration-with-jenkins)
6. [Infrastructure as Code (IaC) with Boto3](#infrastructure-as-code-iac-with-boto3)
7. [Deploying Backend Services](#deploying-backend-services)
8. [Networking and DNS Setup](#networking-and-dns-setup)
9. [Deploying Frontend Services](#deploying-frontend-services)
10. [AWS Lambda Deployment](#aws-lambda-deployment)
11. [Kubernetes (EKS) Deployment](#kubernetes-eks-deployment)
12. [Monitoring and Logging](#monitoring-and-logging)
13. [Documentation](#documentation)
14. [Final Checks](#final-checks)

## Prerequisites

- AWS CLI and Boto3 installed and configured
- Docker installed
- Helm installed
- Jenkins installed
- Python 3.x
- Git

## Setup AWS Environment

1. **Install AWS CLI:**

   ```bash
   pip install awscli
   aws configure
   ```

2. **Install Boto3:**

   ```bash
   pip install boto3
   ```

## Prepare the MERN Application

1. **Containerize the Application:**

   - **Running docker-compose:**

   ```bash
   docker-compose build
   ```

2. **Push Docker Images to Amazon ECR:**

   ```bash
   # Create repositories
   aws ecr create-repository --repository-name rmernmicrof
   aws ecr create-repository --repository-name rmernmicrobehello
   aws ecr create-repository --repository-name rmernmicrobeprofile

   # Build and push images
   docker build -t rmernmicrof .
   docker tag rmernmicrof:frontend <aws_account_id>.dkr.ecr.<region>.amazonaws.com/rmernmicrof:frontend
   docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/rmernmicrof:frontend

   docker build -t rmernmicrohello .
   docker tag rmernmicrohello:hello <aws_account_id>.dkr.ecr.<region>.amazonaws.com/rmernmicrohello:hello
   docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/rmernmicrohello:hello

   docker build -t rmernmicroprofile .
   docker tag rmernmicroprofile:profile <aws_account_id>.dkr.ecr.<region>.amazonaws.com/rmernmicroprofile:profile
   docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/rmernmicroprofile:profile
   ```

## Version Control with AWS CodeCommit

1. **Create a CodeCommit Repository:**

   ```bash
   aws codecommit create-repository --repository-name Rmernmicro
   ```

2. **Push Code to CodeCommit:**

   ```bash
   git remote add codecommit <codecommit_repo_url>
   git push codecommit main
   ```

## Continuous Integration with Jenkins

1. **Install Jenkins Plugins:**

   - Docker Pipeline
   - Amazon ECR

2. **Create Jenkins Jobs:**

   - **Build and Push Docker Images:**
     Configure Jenkins jobs to build Docker images and push them to ECR on code commits.

## Infrastructure as Code (IaC) with Boto3

1. **Define Infrastructure:**

   **Example Python Script: vpc.py**

   ```python
   import boto3

   ec2 = boto3.client('ec2')

   # Create a VPC, subnets, and security groups
   # Define Auto Scaling Group and launch configurations
   ```

## Deploying Backend Services

1. **Deploy Backend on EC2 with ASG: asg.py**

   **Example Python Script:**

   ```python
   import boto3

   asg = boto3.client('autoscaling')

   # Define launch configuration and auto-scaling group
   ```

## Networking and DNS Setup

1. **Create Load Balancer: alb.py**

   **Example Python Script:**

   ```python
   elb = boto3.client('elb')

   # Create and configure Elastic Load Balancer
   ```

   screenshots added in the docs folder

2. **Configure DNS:**

   Use Route 53 or cloudflare DNS service to set up DNS for your application.
   "screenshots added in docs folder"

## Deploying Frontend Services

1. **Deploy Frontend on EC2: ec2_instance.py**

   **Example Python Script:**

   ```python
   import boto3

   ec2 = boto3.client('ec2')

   # Launch EC2 instances for the frontend
   ```

## AWS implimentation
all the scripts are added in boto3 folder and for managing them there is
**infra.py** script   

## AWS Lambda Deployment

1. **Backup Database Script:**

   **dblambdabackup.py.py:**

   ```python
   import boto3
   import pymongo
   import datetime

   def lambda_handler(event, context):
       # Backup logic
   ```

## Kubernetes (EKS) Deployment

1. **Create EKS Cluster:**

   ```bash
   eksctl create cluster \
     --name my-eks-cluster \
     --version 1.21 \
     --region us-west-2 \
     --nodegroup-name standard-workers \
     --node-type t3.medium \
     --nodes 3 \
     --nodes-min 1 \
     --nodes-max 4 \
     --managed
   ```

2. **Deploy Application with Helm:**

   ```bash
   helm create mernmicrohelm
   ```

   **Example Helm Chart Files:**

   - `Chart.yaml`
   - `values.yaml`
   - `templates/deployment.yaml`
   - `templates/service.yaml`

   **Deploy with Helm:**

   ```bash
   helm package mernmicrohelm
   helm install mernmicrohelm mernmicrohelm-0.1.0.tgz
   ```

## Monitoring and Logging

1. **Set Up Monitoring with CloudWatch:**

   screenshots added in the docs folder



## Final Checks

1. **Validate the Deployment:**

   - Ensure that the MERN application is accessible.
   - Test both frontend and backend functionality.
   - Check monitoring and logging for any issues.

---
