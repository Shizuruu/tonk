import boto3
from boto3.dynamodb.conditions import Key



dynamodb = boto3.resource('dynamodb', region_name=f"{ConfigDict['DB-REGION']}")
configTable = dynamodb.Table(f"{ConfigDict['DB-NAME']}")
