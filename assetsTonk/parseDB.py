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

def getMpaManagerRoles(channelID: str, dbQuery):
    try:
        mpaManagerDict = {}
        mpaManagerDict['channelManagerRoles'] = dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['mpaManagerRoles']
        mpaManagerDict['serverManagerRoles'] = dbQuery['Items'][0]['mpaConfig']['global']['mpaManagerRoles']
        return mpaManagerDict
    except KeyError as e:
        # Check scenario if channelManagerRoles has data but not serverManagerRoles
        if e.args[0] == 'serverMpaManagerRoles':
            mpaManagerDict['serverManagerRoles'] = None
        else:
            # Return none type, the key isnt there meaning the server did not configure any roles.
            mpaManagerDict['channelManagerRoles'] = None
            mpaManagerDict['serverManagerRoles'] = None
        return mpaManagerDict
    except IndexError:
        return IndexError