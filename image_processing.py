import json
import requests
import os
import boto
import boto3
import sys
import key_config

with open("flask\\a1.json") as file:
    data = json.load(file)

print('json loaded')

s3c = boto3.client('s3', region_name='us-east-1', aws_access_key_id = key_config.ACCESS_KEY_ID, aws_secret_access_key = key_config.ACCESS_SECRET_KEY)

for index in data['songs']:
        img_url = index['img_url']
        song_title = index['title']
        img_data = requests.get(img_url).content
        img_name = 'flask\\images\\' + song_title + '.jpg'
        with open(img_name, "wb") as handler:
              handler.write(img_data)

bucket_name = 'assignmentoneflaskimagebucket'
local_folder_path='images'

for file_name in os.listdir(local_folder_path):
      local_file_path = os.path.join(local_folder_path, file_name)
      s3c.upload_file(local_file_path, bucket_name, file_name)


