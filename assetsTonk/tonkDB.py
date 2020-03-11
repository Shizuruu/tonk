import boto3
import json
from boto3.dynamodb.conditions import Key

ConfigFile = open('assetsTonk/configs/TonkDevConfig.json')
ConfigDict = json.loads(ConfigFile.read())

dynamodb = boto3.resource('dynamodb', region_name=f"{ConfigDict['DB-REGION']}")
configTable = dynamodb.Table(f"{ConfigDict['DB-NAME']}")

def gidQueryDB(guildID):
    return configTable.query(KeyConditionExpression=Key('guildID').eq(f'{guildID}'))

def updateMpaChannels(guildID, newChannelID, timeStamp):
    configTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression="SET mpaChannels = list_append(mpaChannels, :newmpachannel), SET lastUpdated = :timestamp",
        ExpressionAttributeValues={
            ':newmpachannel': [f"{newChannelID}"],
            ':timestamp': [f"{timeStamp}"]
        }
    )
    return
# This function should only be used when the server has no MPA channels whatsoever.
# The function is also used if the server does not already exist in the database.
def addMpaChannel(guildID, newChannelID, timeStamp):
    configTable.put_item(
        Item={
            'guildID': f"{guildID}",
            'mpaChannels': [f"{newChannelID}"],
            'lastUpdated': f"{timeStamp}"
        }
    )
    return

# def updateMpaAutoExpirationChannels(guildID, newChannelID, dbQuery):
#     try:
#         if len(dbQuery['Items'][0]['mpaAutoExpirationChannels']) > 0:   
#             configTable.update_item(
#             Key={
#                 'guildID': f"{guildID}"
#             },
#             UpdateExpression="SET mpaAutoExpirationChannels = list_append(mpaAutoExpirationChannels, :newmpachannel)",
#             ExpressionAttributeValues={
#                 ':newmpachannel': [f"{newChannelID}"]
#             }
#             )
#     except KeyError:
#             configTable.update_item(
#             Key={
#                 'guildID': f"{guildID}"
#             },
#             UpdateExpression="SET mpaAutoExpirationChannels = if_not_exists(mpaAutoExpirationChannels, :newmpachannel)",
#             ExpressionAttributeValues={
#                 ':newmpachannel': [f"{newChannelID}"]
#             }
#             )
#     return


def removeMpaChannel(guildID, channelIndex, timeStamp):
    configTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"REMOVE mpaChannels[{channelIndex}] SET lastUpdated = :timestamp",
        ExpressionAttributeValues={
            ':timestamp': f"{timeStamp}"
        }
    )
    return
