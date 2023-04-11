import boto3
import key_config
import json

with open("a1.json") as file:
    data = json.load(file)

print('json loaded')



dynamo_client = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id = key_config.ACCESS_KEY_ID, aws_secret_access_key = key_config.ACCESS_SECRET_KEY)

music_table = dynamo_client.Table('music')

for index in data['songs']:
    music_table.put_item(
        Item={
        'title':index['title'],
        'artist':index['artist'],
        'year':index['year'],
        'web_url': index['web_url'],
        'img_url': index['img_url']
        }
    )

