# This module separately parses the DB query jsons, returning any server/channel configured variables or assigning it the default variable if there is none found.

def getPrivateMpa(channelID: str, dbQuery, defaultDBQuery):
    try:
        return dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['privateMpa']
    except KeyError:
        return defaultDBQuery['Items'][0]['mpaConfig']['privateMpa']

def getActiveServerSlotID(channelID: str, dbQuery, defaultDBQuery):
    try:
        return dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['privateMpa']
    except KeyError:
        return defaultDBQuery['Items'][0]['mpaConfig']['activeServerSlot']

def getInactiveServerSlotID(channelID: str, dbQuery, defaultDBQuery):
    try:
        return dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['privateMpa']
    except KeyError:
        return defaultDBQuery['Items'][0]['mpaConfig']['inactiveServerSlot']

def getEmbedColor(channelID: str, dbQuery, defaultDBQuery):
    try:
        return dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['embedColor']
    except KeyError:
        return defaultDBQuery['Items'][0]['mpaConfig']['embedColor']

def getMpaExpirationEnabled(channelID: str, dbQuery, defaultDBQuery):
    try:
        return dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['mpaExpirationEnabled']
    except KeyError:
        return defaultDBQuery['Items'][0]['mpaConfig']['mpaExpirationEnabled']

def getMpaExpirationTime(channelID: str, dbQuery, defaultDBQuery):
    try:
        return dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['mpaExpirationTime']
    except KeyError:
        return defaultDBQuery['Items'][0]['mpaConfig']['mpaExpirationTime']

def getClassIcons(defaultDBQuery):
    return defaultDBQuery['Items'][0]['mpaConfig']['classIDs']

def getHeroClasses(defaultDBQuery):
    return defaultDBQuery['Items'][0]['mpaConfig']['heroClasses']

def getSubbableHeroClasses(defaultDBQuery):
    return defaultDBQuery['Items'][0]['mpaConfig']['subbableHeroClasses']

def getMpaBlock(channelID: str, dbQuery, defaultDBQuery):
    try:
        return dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['mpaBlock']
    except KeyError:
        return defaultDBQuery['Items'][0]['mpaConfig']['mpaBlock']
    
def getAllowedMpaRoles(channelID: str, dbQuery, defaultDBQuery):
    try:
        return dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['mpaAllowedRoles']
    except KeyError:
        return defaultDBQuery['Items'][0]['mpaConfig']['mpaBlock']