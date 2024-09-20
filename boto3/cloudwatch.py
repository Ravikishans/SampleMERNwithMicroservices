import boto3
import datetime
import json

def create_cloudwatch_rule(lambda_arn, schedule_expression, rule_name):
    events_client = boto3.client('events')

    try:
        # Create CloudWatch event rule
        response = events_client.put_rule(
            Name='S3_Lambda',
            ScheduleExpression='rate(1 day)',  # e.g., 'rate(1 day)' for daily trigger
            State='ENABLED'
        )
        rule_arn = response['RuleArn']

        # Give permission for the rule to invoke the Lambda function
        lambda_client = boto3.client('lambda')
        lambda_client.add_permission(
            FunctionName="Rmernmicro",
            StatementId=f"{rule_name}-invoke",
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_arn
        )

        # Attach the Lambda function to the rule
        events_client.put_targets(
            Rule=rule_name,
            Targets=[{'Id': '1', 'Arn': lambda_arn}]
        )

        print(f"CloudWatch event rule '{rule_name}' created to trigger Lambda.")
    except Exception as e:
        print(f"Error creating CloudWatch rule: {e}")
