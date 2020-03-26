import boto3
import json
from boto3.dynamodb.conditions import Key

ConfigFile = open('assetsTonk/configs/TonkDevConfig.json')
ConfigDict = json.loads(ConfigFile.read())

dynamodb = boto3.resource('dynamodb', region_name=f"{ConfigDict['DB-REGION']}", aws_access_key_id=f"{ConfigDict['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{ConfigDict['AWS_SECRET_ACCESS_KEY']}")
dbTable = dynamodb.Table(f"{ConfigDict['DB-NAME']}")

def gidQueryDB(guildID):
    return dbTable.query(KeyConditionExpression=Key('guildID').eq(f'{guildID}'))

def configDefaultQueryDB():
    return dbTable.query(KeyConditionExpression=Key('guildID').eq('defaults'))

def queryExpirationKeys():
    return dbTable.scan(ProjectionExpression='activeMPAs, mpaConfig')

def updateMpaChannels(guildID, newChannelID, timeStamp):
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression="SET mpaChannels = list_append(mpaChannels, :newmpachannel), mpaConfig.#newChannelID = :mpaConfig, activeMPAs.#newChannelID = :activeMPAs, lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#newChannelID': f"{newChannelID}"
        },
        ExpressionAttributeValues={
            ':newmpachannel': [f"{newChannelID}"],
            ':timestamp': [f"{timeStamp}"],
            ':mpaConfig': {},
            ':activeMPAs': {}
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
            'mpaConfig': {
                "global": {},
                f"{newChannelID}": {}
            },
            'activeMPAs': {f"{newChannelID}": {}}
        }
    )
    return

def removeMpaChannel(guildID, channelID, channelIndex, timeStamp):
    dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"REMOVE mpaChannels[{channelIndex}], mpaConfig.#channelID, activeMPAs.#channelID SET lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#channelID': f"{channelID}"
        },
        ExpressionAttributeValues={
            ':timestamp': f"{timeStamp}"
        }
    )
    return

def startMPATable(guildID, channelID, messageID, EQList, SubList, privateMpa, participantCount, maxParticipants, expirationDate, startDate):
    print (startDate)
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
                'privateMpa': f"{str(privateMpa)}",
                'maxParticipants': f"{str(maxParticipants)}",
                'participantCount': f"{str(participantCount)}",
                'expirationDate': f"{expirationDate}",
                'startDate': f"{startDate}"
            },
            ':timestamp': f"{startDate}"
        }
    )

def updateMPATable(guildID, channelID, messageID, EQList, SubList, privateMpa, participantCount, maxParticipants, expirationDate, timeStamp, startDate):
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
                'privateMpa': f"{str(privateMpa)}",
                'maxParticipants': f"{str(maxParticipants)}",
                'participantCount': f"{str(participantCount)}",
                'expirationDate': f"{expirationDate}",
                'startDate': f"{startDate}"
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

def updateRoleList(guildID, channelID, configName, roleID, timeStamp, keyExists: str = 'true'):
    if keyExists == 'false':
        return dbTable.update_item(
            Key={
                'guildID': f"{guildID}"
            },
            UpdateExpression=f"SET mpaConfig.#channelID.#configName = :roleID, lastUpdated = :timestamp",
            ExpressionAttributeNames={
                '#channelID': f"{channelID}",
                '#configName': f"{configName}"
            },
            ExpressionAttributeValues={
                ':timestamp': f"{timeStamp}",
                ':roleID': [f"{roleID}"]
            },
            ReturnValues='UPDATED_NEW'
        )
    elif channelID == 'default':
        return dbTable.update_item(
            Key={
                'guildID': "defaults"
            },
            UpdateExpression=f"SET mpaConfig.#configName = list_append(mpaConfig.#configName, :roleID), lastUpdated = :timestamp",
            ExpressionAttributeNames={
                '#channelID': f"{channelID}",
                '#configName': f"{configName}"
            },
            ExpressionAttributeValues={
                ':timestamp': f"{timeStamp}",
                ':roleID': [f"{roleID}"]
            },
            ReturnValues='UPDATED_NEW'
        )
    else:
        return dbTable.update_item(
            Key={
                'guildID': f"{guildID}"
            },
            UpdateExpression=f"SET mpaConfig.#channelID.#configName = list_append(mpaConfig.#channelID.#configName, :roleID), lastUpdated = :timestamp",
            ExpressionAttributeNames={
                '#channelID': f"{channelID}",
                '#configName': f"{configName}"
            },
            ExpressionAttributeValues={
                ':timestamp': f"{timeStamp}",
                ':roleID': [f"{roleID}"]
            },
            ReturnValues='UPDATED_NEW'
        )
    return None

def updateConfig(guildID, channelID, configName, configValue, timeStamp, keyExists: str = 'true'):
    if channelID != '':
        return dbTable.update_item(
            Key={
                'guildID': f"{guildID}"
            },
            UpdateExpression=f"SET mpaConfig.#channelID.#configName = :configValue, lastUpdated = :timestamp",
            ExpressionAttributeNames={
                '#channelID': f"{channelID}",
                '#configName': f"{configName}"
            },
            ExpressionAttributeValues={
                ':timestamp': f"{timeStamp}",
                ':configValue': f"{configValue}"
            },
            ReturnValues='UPDATED_NEW'
        )
    elif channelID == 'default':
        return dbTable.update_item(
            Key={
                'guildID': "defaults"
            },
            UpdateExpression=f"SET mpaConfig.#configName = :configValue, lastUpdated = :timestamp",
            ExpressionAttributeNames={
                '#channelID': f"{channelID}",
                '#configName': f"{configName}"
            },
            ExpressionAttributeValues={
                ':timestamp': f"{timeStamp}",
                ':configValue': f"{configValue}"
            },
            ReturnValues='UPDATED_NEW'
        )
    return None


def removeRoleList(guildID, channelID, configName, index, timeStamp):
    # Theres this really weird bug where if the list item does not exist in the DB, this statement does not create the key and appends the list.
    # Needs investigation.
    if channelID == 'default':
        guildID = 'defaults'
    return dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"REMOVE mpaConfig.#channelID.#configName[{index}] SET lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#channelID': f"{channelID}",
            '#configName': f"{configName}"
        },
        ExpressionAttributeValues={
            ':timestamp': f"{timeStamp}"
        },
        ReturnValues='UPDATED_NEW'
    )
    return None


def removeConfig(guildID, channelID, configName, timeStamp):
    if channelID == 'default':
        guildID = 'defaults'
    return dbTable.update_item(
        Key={
            'guildID': f"{guildID}"
        },
        UpdateExpression=f"REMOVE mpaConfig.#channelID.#configName SET lastUpdated = :timestamp",
        ExpressionAttributeNames={
            '#channelID': f"{channelID}",
            '#configName': f"{configName}"
        },
        ExpressionAttributeValues={
            ':timestamp': f"{timeStamp}"
        },
        ReturnValues='UPDATED_NEW'
    )
    return None