import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def get_dynamodb_resource():
    """Sets up and returns the DynamoDB resource."""
    ddb = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8765',  # Change this if using a different endpoint
        region_name='us-west-2',  # Use a valid AWS region or your local DynamoDB region
        aws_access_key_id='dummy',  # Use dummy for local DynamoDB or actual keys for AWS
        aws_secret_access_key='dummy'
    )
    return ddb

def init_dynamodb_tables(dynamodb):
    """Initializes DynamoDB tables if they don't exist."""
    try:
        # Create Users table if it doesn't exist
        dynamodb.create_table(
            TableName='Users',
            KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print("Created Users table.")

    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("Users table already exists.")

    try:
        # Create Petitions table if it doesn't exist
        dynamodb.create_table(
            TableName='Petitions',
            KeySchema=[{'AttributeName': 'petition_id', 'KeyType': 'HASH'}],  # Partition key only
            AttributeDefinitions=[{'AttributeName': 'petition_id', 'AttributeType': 'S'}],  # String type for partition key
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print("Created Petitions table.")

    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("Petitions table already exists.")

    # Optionally, you could return the tables or their status if needed
