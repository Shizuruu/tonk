import boto3
import json
from boto3.dynamodb.conditions import Key

ConfigFile = open('assetsTonk/configs/TonkDevConfig.json')
ConfigDict = json.loads(ConfigFile.read())

dynamodb = boto3.resource('dynamodb', region_name=f"{ConfigDict['DB-REGION']}")
dbTable = dynamodb.Table(f"{ConfigDict['DB-NAME']}")

def gidQueryDB(guildID):
    return dbTable.query(KeyConditionExpression=Key('guildID').eq(f'{guildID}'))

def configDefaultQueryDB():
    return dbTable.query(KeyConditionExpression=Key('guildID').eq('defaults'))

def updateMpaChannels(guildID, newChannelID, timeStamp):
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression="SET mpaChannels = list_append(mpaChannels, :newmpachannel), lastUpdated = :timestamp",
        ExpressionAttributeValues={
            ':newmpachannel': [f"{newChannelID}"],
            ':timestamp': [f"{timeStamp}"]
        }
    )
    return
# This function should only be used when the server has no MPA channels whatsoever.
# The function is also used if the server does not already exist in the database.
def addMpaChannel(guildID, newChannelID, timeStamp):
    dbTable.put_item(
        Item={
            'guildID': f"{guildID}",
            'mpaChannels': [f"{newChannelID}"],
            'lastUpdated': f"{timeStamp}",
            'mpaConfig': {f"{newChannelID}": {}},
            'activeMPAs': {f"{newChannelID}": {}}
        }
    )
    return

# def updateMpaAutoExpirationChannels(guildID, newChannelID, dbQuery):
#     try:
#         if len(dbQuery['Items'][0]['mpaAutoExpirationChannels']) > 0:   
#             dbTable.update_item(
#             Key={
#                 'guildID': f"{guildID}"
#             },
#             UpdateExpression="SET mpaAutoExpirationChannels = list_append(mpaAutoExpirationChannels, :newmpachannel)",
#             ExpressionAttributeValues={
#                 ':newmpachannel': [f"{newChannelID}"]
#             }
#             )
#     except KeyError:
#             dbTable.update_item(
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
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"REMOVE mpaChannels[{channelIndex}] SET lastUpdated = :timestamp",
        ExpressionAttributeValues={
            ':timestamp': f"{timeStamp}"
        }
    )
    return


def addMpaBlockNumber(guildID, channelID: str, blockNumber: str, timeStamp):
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"SET mpaConfig.#channelID.mpaBlock = :block, lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#channelID': f"{channelID}"
        },
        ExpressionAttributeValues={
            ':block': f"{blockNumber}",
            ':timestamp': f"{timeStamp}"
        }
    )
    return

def removeMpaBlockNumber(guildID, channelID: str, timeStamp):
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"REMOVE mpaConfig.#channelID.mpaBlock SET lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#channelID': f"{channelID}"
        },
        ExpressionAttributeValues={
            ':timestamp': f"{timeStamp}"
        }
    )
    return

def removeMpaBlockNumber(guildID, channelID: str, timeStamp):
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"REMOVE mpaConfig.#channelID.mpaBlock SET lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#channelID': f"{channelID}"
        },
        ExpressionAttributeValues={
            ':timestamp': f"{timeStamp}"
        }
    )
    return

def startMPATable(guildID, channelID, messageID, EQList, SubList, guestEnabled, participantCount, maxParticipants, expirationDate, startDate):
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"SET activeMPAs.#channelID.#messageID = :eqDict, lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#channelID': f"{channelID}",
            '#messageID': f"{messageID}"
        },
        ExpressionAttributeValues={
            ':eqDict': {
                'EQTest': EQList,
                'SubList': SubList,
                'guestEnabled': f"{str(guestEnabled)}",
                'maxParticipants': f"{str(maxParticipants)}",
                'participantCount': f"{str(participantCount)}",
                'expirationDate': f"{expirationDate}",
                'startDate': f"{startDate}"
            },
            ':timestamp': f"{startDate}"
        }
    )

def updateMPATable(guildID, channelID, messageID, EQList, SubList, guestEnabled, participantCount, maxParticipants, expirationDate, timeStamp):
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"SET activeMPAs.#channelID.#messageID = :eqDict, lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#channelID': f"{channelID}",
            '#messageID': f"{messageID}"
        },
        ExpressionAttributeValues={
            ':eqDict': {
                'EQTest': EQList,
                'SubList': SubList,
                'guestEnabled': f"{str(guestEnabled)}",
                'maxParticipants': f"{str(maxParticipants)}",
                'participantCount': f"{str(participantCount)}",
                'expirationDate': f"{expirationDate}"
            },
            ':timestamp': f"{timeStamp}"
        }
    )


def removeMPATable(guildID, channelID, messageID, timeStamp):
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"REMOVE activeMPAs.#channelID.#messageID SET lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#channelID': f"{channelID}",
            '#messageID': f"{messageID}"
        },
        ExpressionAttributeValues={
            ':timestamp': f"{timeStamp}"
        }
    )