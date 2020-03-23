import boto3
import json
import os
from os import listdir
from os.path import isfile, join

ConfigFile = open('assetsTonk/configs/TonkDevConfig.json')
ConfigDict = json.loads(ConfigFile.read())
bucketName = ConfigDict['S3_BUCKET_NAME']
s3_client = boto3.client('s3', aws_access_key_id=f"{ConfigDict['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{ConfigDict['AWS_SECRET_ACCESS_KEY']}")


def getMpaBanner(bannerName):
    # Check the tmp file cache, if the file already exists then upload from the cache instead of having to redownload from S3.
    cachedFiles = [f for f in listdir('tmp/') if isfile(join('tmp/', f))]
    for item in cachedFiles:
        if bannerName in item:
            return f"tmp/{item}"
    objectsList = s3_client.list_objects_v2(
        Bucket=bucketName
    )
    for item in objectsList['Contents']:
        if bannerName in item['Key']:         
            filePath = f"tmp/{item['Key']}"
            s3_client.download_file(bucketName, f"{item['Key']}", f'{filePath}')
            return filePath
    return None

def getAlias(aliasName):
    aliasFile = open('assetsTonk/mpaAliases.json')
    aliasDict = json.loads(aliasFile.read())
    if aliasName in aliasDict.keys():
        return aliasDict[aliasName]
    else:
        return aliasName