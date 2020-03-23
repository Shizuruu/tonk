# This module separately parses the DB query jsons, returning any server/channel configured variables or assigning it the default variable if there is none found.

import traceback
import sys


def getDBConfig(channelID: str, dbQuery, defaultDBQuery, configName):
    try:
        return dbQuery['Items'][0]['mpaConfig'][f'{channelID}'][configName]
    except KeyError as e:
        if e.args[0] == configName:
            try:
                return dbQuery['Items'][0]['mpaConfig']['global'][configName]
            except KeyError:
                return defaultDBQuery['Items'][0]['mpaConfig'][configName]
        elif e.args[0] == f'{channelID}':
            try:
                return dbQuery['Items'][0]['mpaConfig']['global'][configName]
            except KeyError:
                return defaultDBQuery['Items'][0]['mpaConfig'][configName]
        else:
            return defaultDBQuery['Items'][0]['mpaConfig'][configName]
        

def getDefaultDBConfig(defaultDBQuery, configName):
    return defaultDBQuery['Items'][0]['mpaConfig'][configName]
    
def getAllowedMpaRoles(channelID: str, dbQuery):
    mpaAllowedRoles = {}
    try:
        mpaAllowedRoles['channelAllowedRoles'] = dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['mpaAllowedRoles']
    except KeyError:
        mpaAllowedRoles['channelAllowedRoles'] = None
    try:
        mpaAllowedRoles['serverAllowedRoles'] = dbQuery['Items'][0]['mpaConfig']['global']['mpaAllowedRoles']
    except KeyError:
        mpaAllowedRoles['serverAllowedRoles'] = None
    return mpaAllowedRoles

def getMpaManagerRoles(channelID: str, dbQuery):
    mpaManagerDict = {}
    try:
        mpaManagerDict['channelManagerRoles'] = dbQuery['Items'][0]['mpaConfig'][f'{channelID}']['mpaManagerRoles']
    except KeyError:
        mpaManagerDict['channelManagerRoles'] = None
    try:
        mpaManagerDict['serverManagerRoles'] = dbQuery['Items'][0]['mpaConfig']['global']['mpaManagerRoles']
    except KeyError:
        mpaManagerDict['serverManagerRoles'] = None
    return mpaManagerDict