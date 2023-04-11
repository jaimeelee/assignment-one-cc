import boto3
import key_config

dynamo_client = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id = key_config.ACCESS_KEY_ID, aws_secret_access_key = key_config.ACCESS_SECRET_KEY)


subscription_table = dynamo_client.create_table(
    TableName = 'subscription',
    KeySchema=[
    {
        'AttributeName': 'userid',
        'KeyType':'HASH'
    },
    {
        'AttributeName': 'track',
        'KeyType': 'RANGE'
    }
    ],
    AttributeDefinitions=[
    {
        'AttributeName':'userid',
        'AttributeType':'S'
    },
    {
        'AttributeName': 'track',
        'AttributeType': 'S'
    }
    ],
    ProvisionedThroughput={
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits' :5
    }
)

subscription_table.meta.client.get_waiter('table_exists').wait(TableName='subscription')

