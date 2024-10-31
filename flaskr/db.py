import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def get_dynamodb_resource():
    """Sets up and returns the DynamoDB resource."""
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:8000'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    )
    return dynamodb

def init_dynamodb_tables(dynamodb):
    """Initializes DynamoDB tables if they don't exist."""
    try:
        dynamodb.create_table(
            TableName='Users',
            KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        # Define the Petitions table
        dynamodb.create_table(
            TableName='Petitions',
            KeySchema=[
                {'AttributeName': 'title', 'KeyType': 'HASH'},
                {'AttributeName': 'petition_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'title', 'AttributeType': 'S'},
                {'AttributeName': 'petition_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

    except dynamodb.meta.client.exceptions.ResourceInUseException:
        # Tables already exist
        pass
