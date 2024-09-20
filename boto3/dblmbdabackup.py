import boto3
import os
import subprocess
import datetime
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # S3 bucket and MongoDB details
    bucket_name = 'rakshi2508'
    db_name = 'sampleNginxLB'  # Replace with your MongoDB database name

    # Timestamp the backup
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_filename = f"{db_name}_backup_{timestamp}.gz"
    backup_filepath = f"/tmp/{backup_filename}"  # Lambda allows writing to /tmp

    try:
        # Run mongodump to create a backup of the MongoDB database
        mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://ravikishan:Cluster0@cluster0.y9zohpu.mongodb.net/sampleNginxLB')  # Connection string for MongoDB
# mongodb+srv://ravikishan:Cluster0@cluster0.y9zohpu.mongodb.net/sampleNginxLB
        # Call mongodump with subprocess
        subprocess.run([
            'mongodump',
            '--uri', mongo_uri,
            '--archive=' + backup_filepath,
            '--gzip'  # Compress the backup
        ], check=True)

        # Upload the backup file to S3
        with open(backup_filepath, 'rb') as data:
            s3.put_object(
                Bucket=bucket_name,
                Key=backup_filename,
                Body=data
            )

        # Return success
        return {
            'statusCode': 200,
            'body': json.dumps(f"Backup {backup_filename} stored in {bucket_name}")
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error during MongoDB backup: {str(e)}")
        }
