import asyncio
import sys
import re
import discord
import traceback
import datetime
import json
from datetime import datetime

from assetsTonk import sendErrorMessage
from assetsTonk import tonkDB
from assetsTonk import parseDB

ConfigFile = open('assetsTonk/configs/TonkDevConfig.json')
ConfigDict = json.loads(ConfigFile.read())
botOwnerID = ConfigDict['OWNERID']
embedColor = discord.Colour(value=int("14cc00", 16))
failEmbedColor = discord.Colour(value=int("ce0000", 16))

# Function that verifies config formats and determines if the syntax of the configuration type is correct, such as embedColor being hex or not.
def checkConfigSyntax(ctx, configName, configValue):
    helpFile = open('assetsTonk/helpTexts/configUsage.json')
    helpDict = json.loads(helpFile.read())
    if configName in helpDict.keys():
        configType = helpDict[f'{configName}']['type']
        if configType == 'emojiID':
            emoji = discord.utils.get(ctx.guild.emojis, id=int(configValue))
            if emoji is None:
                return None
            else:
                if emoji.is_usable():
                    return True
                else:
                    return None
        elif configType == 'hexColor':
            if configValue.startswith('#'):
                try:
                    embedColor = configValue.lstrip('#')
                    embedColor = discord.Colour(value=int(f"{configValue}", 16))
                    return True
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                    return None
            else:
                return None
        elif configType == 'number':
            if len(configValue) < 16 and configValue.isdigit():
                return True
            else:
                return None
        elif configType == 'bool':
            if configValue.lower() == 'true' or configValue.lower() == 'false':
                return None
            else:
                return None
        elif configType == 'timeNumber':
            if len(configValue) < 16 and configValue.isdigit():
                return True
            else:
                return None
        else:
            return None

# This function takes the message and breaks the arguments down (separated by spaces) and then calls the appropriate functions or throws the appropriate errors based on the input recieved.
async def cmdConfigParser(ctx, *args):
    if len(args) < 2:
        await sendErrorMessage.invalidArguments(ctx, 'badArguments', cmdConfigParser.__name__)
        return
    # Display active configurations on a given server/channel
    elif args[0] == 'show':
        try:
            if args[1].lower() == 'default':
                # Only the bot owner can read and modify defaults.
                if ctx.author.id == botOwnerID:
                    defaultConfigQuery = tonkDB.configDefaultQueryDB()
                    mpaConfig = {key.lower() for key in defaultConfigQuery['Items'][0]['mpaConfig'].keys()}
                    try:
                        if args[2].lower() in mpaConfig:
                            await showDefaultConfig(ctx, defaultConfigQuery, args[2])
                    except IndexError:
                        await sendErrorMessage.invalidArguments(ctx, 'badShowDefaultArguments', cmdConfigParser.__name__)
                    return
                else:
                    await sendErrorMessage.noCommandPermissions(ctx, cmdConfigParser.__name__)
                    return
            else:
                try:
                    dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
                    if len(ctx.message.channel_mentions) > 0:
                        channelID = ctx.message.channel_mentions[0].id
                    else:
                        channelID = int(args[2])
                    mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{channelID}'].keys()
                except IndexError:
                    channelID = None
                    mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()
                except TypeError:
                    channelID = None
                    mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()
                except ValueError:
                    channelID = None
                    mpaConfig = {}
                    pass
            if args[1] == 'all':
                if channelID is not None:
                    await showAllConfigs(ctx, dbQuery, channelID)
                else:
                    await showAllConfigs(ctx, dbQuery)
                return
            elif args[1].lower() in mpaConfig:
                if channelID is not None:
                    await showChannelConfig(ctx, dbQuery, args[1], channelID)
                else:
                    await showChannelConfig(ctx, dbQuery, args[1])
                return
            elif args[1].lower() == 'server':
                mpaConfig = {key.lower() for key in dbQuery['Items'][0]['mpaConfig']['global'].keys()}
                try:
                    if args[2].lower() in mpaConfig:
                        await showServerConfig(ctx, dbQuery, args[2])
                    else:
                        await showNothing(ctx, args[2])
                except IndexError:
                    await sendErrorMessage.invalidArguments(ctx, 'badShowServerArguments', cmdConfigParser.__name__)
            else:
                await showNothing(ctx, args[1])
                return
        except IndexError:
            await sendErrorMessage.invalidArguments(ctx, 'badShowArguments', cmdConfigParser.__name__)
            return
    # Sets new configurations
    elif args[0] == 'set':
        try:
            if args[1].lower() == 'default':
                if ctx.author.id == botOwnerID:
                    defaultConfigQuery = tonkDB.configDefaultQueryDB()
                    mpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
                    try:
                        if args[2].lower() in mpaConfig:
                            await setDefaultConfig(ctx, defaultConfigQuery, args[2], args[3])
                    except IndexError:
                        await sendErrorMessage.invalidArguments(ctx, 'badSetDefaultArguments', cmdConfigParser.__name__)
                    return
                else:
                    await sendErrorMessage.noCommandPermissions(ctx, cmdConfigParser.__name__)
                    return
            try:
                dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
                defaultConfigQuery = tonkDB.configDefaultQueryDB()
                if len(ctx.message.channel_mentions) > 0:
                    channelID = ctx.message.channel_mentions[0].id
                else:
                    channelID = int(args[3])
                mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{channelID}'].keys()
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
            except IndexError:
                channelID = None
                mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
            except TypeError:
                channelID = None
                mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
            except ValueError:
                channelID = None
                mpaConfig = {}
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
                pass
            if args[1] in mpaConfig:
                if channelID is not None:
                    await setChannelConfig(ctx, dbQuery, args[1], args[2], channelID)
                else:
                    await setChannelConfig(ctx, dbQuery, args[1], args[2])
                return
            elif args[1] not in mpaConfig and args[1] in defaultMpaConfig:
                if channelID is not None:
                    await setChannelConfig(ctx, dbQuery, args[1], args[2], channelID)
                else:
                    await setChannelConfig(ctx, dbQuery, args[1], args[2])
                return
            elif args[1].lower() == 'server':
                mpaConfig = dbQuery['Items'][0]['mpaConfig']['global'].keys()
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
                try:
                    if args[2] in mpaConfig:
                        await setServerConfig(ctx, dbQuery, args[2], args[3])
                    elif args[2] not in mpaConfig and args[2] in defaultMpaConfig:
                        await setServerConfig(ctx, dbQuery, args[2], args[3])
                    else:
                        await showNothing(ctx, args[2])
                except IndexError:
                    
                    await sendErrorMessage.invalidArguments(ctx, 'badSetServerArguments', cmdConfigParser.__name__)
            else:
                print (args)
                await showNothing(ctx, args[1])
                return
        except IndexError:
            
            await sendErrorMessage.invalidArguments(ctx, 'badSetArguments', cmdConfigParser.__name__)
            return
    # Clears configurations
    elif args[0] == 'remove' or args[0] == 'clear':
        try:
            if args[1].lower() == 'default':
                if ctx.author.id == botOwnerID:
                    defaultConfigQuery = tonkDB.configDefaultQueryDB()
                    mpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
                    try:
                        if args[2].lower() in mpaConfig:
                            await setDefaultConfig(ctx, defaultConfigQuery, args[2], args[3])
                    except IndexError:
                        
                        await sendErrorMessage.invalidArguments(ctx, 'badSetDefaultArguments', cmdConfigParser.__name__)
                    return
                else:
                    await sendErrorMessage.noCommandPermissions(ctx, cmdConfigParser.__name__)
                    return
            try:
                dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
                defaultConfigQuery = tonkDB.configDefaultQueryDB()
                if len(ctx.message.channel_mentions) > 0:
                    channelID = ctx.message.channel_mentions[0].id
                else:
                    channelID = int(args[3])
                mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{channelID}'].keys()
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
            except IndexError:
                channelID = None
                mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
            except TypeError:
                channelID = None
                mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
            except ValueError:
                channelID = None
                mpaConfig = dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
                pass
            if args[1] in mpaConfig:
                if channelID is not None:
                    await removeChannelConfig(ctx, dbQuery, args[1], args[2], channelID)
                else:
                    try:
                        await removeChannelConfig(ctx, dbQuery, args[1], args[2])
                    except IndexError:
                        await removeChannelConfig(ctx, dbQuery, args[1], '')
                return
            elif args[1].lower() == 'server':
                mpaConfig = dbQuery['Items'][0]['mpaConfig']['global'].keys()
                try:
                    if args[2] in mpaConfig:
                        await removeServerConfig(ctx, dbQuery, args[2], args[3])
                    else:
                        await showNothing(ctx, args[2])
                except IndexError:
                    await sendErrorMessage.invalidArguments(ctx, 'badSetServerArguments', cmdConfigParser.__name__)
            else:
                print (args)
                await showNothing(ctx, args[1])
                return
        except IndexError:
            await sendErrorMessage.invalidArguments(ctx, 'badSetArguments', cmdConfigParser.__name__)
            return
        return
    return
async def showAllConfigs(ctx, dbQuery, channelID: str = 'allChannels'):
    em = discord.Embed(color=embedColor)
    if channelID == 'allChannels':
        channelID = str(ctx.channel.id)
        em.set_author(name=f'Results')
    else:
        em.set_author(name=f'Results for channel ID {channelID}')
    for key, value in dbQuery['Items'][0]['mpaConfig'][f'{channelID}'].items():
        if type(value) is list:
        # Probably not the best way to determine if a key is a role list or not
            if 'role' in key.lower():
                if len(value) > 1:
                    for index, item in enumerate(value):
                        foundRole = discord.utils.get(ctx.guild.roles, id=int(item))
                        em.add_field(name=f'{key} - {index + 1}', value=f'{foundRole.mention} (ID: {item})', inline=False)
            else:
                if len(value) > 1:
                    for index, item in enumerate(value):
                        em.add_field(name=f'{key} - {item + 1}', value=f'{item}', inline=False)
        else:
            em.add_field(name=f'{key}:', value=f'{value}', inline=False)
    await ctx.send('', embed=em)
    return

async def showNothing(ctx, configName):
    em = discord.Embed(color=failEmbedColor)
    em.set_author(name=f'Error')
    em.add_field(name='Nothing found!', value=f'Nothing was found for config {configName}')
    await ctx.send('', embed=em)
    return

async def showChannelConfig(ctx, dbQuery, configName, channelID: str = 'currentChannel'):
    em = discord.Embed(color=embedColor)
    if channelID == 'currentChannel':
        channelID = str(ctx.channel.id)
        em.set_author(name=f'Results for config {configName}')
    else:
        em.set_author(name=f'Results for config {configName} for channel ID {channelID}')
    try:
        resultValue = dbQuery[f'{configName}']
    except KeyError:
        em = discord.Embed(color=failEmbedColor)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
    if type(resultValue) is list:
        # Probably not the best way to determine if a key is a role list or not
        if 'role' in configName.lower():
            if len(resultValue) > 0:
                for index, item in enumerate(resultValue):
                    foundRole = discord.utils.get(ctx.guild.roles, id=int(item))
                    em.add_field(name=f'{index + 1}', value=f'{foundRole.mention} (ID: {item})', inline=False)
                await ctx.send('', embed=em)
                return
        else:
            if len(resultValue) > 0:
                for index, item in enumerate(resultValue):
                    em.add_field(name=f'{item + 1}', value=f'{item}', inline=False)
                await ctx.send('', embed=em)
                return
    else:
        em.add_field(name=f'{configName}:', value=f'{resultValue}')
        await ctx.send('', embed=em)
        return
   # em.add_field(name='Value', value=resultValue, inline=False)
    await ctx.send('', embed=em)
    return

async def showServerConfig(ctx, dbQuery, configName):
    em = discord.Embed(color=embedColor)
    em.set_author(name=f'Results for config {configName}')
    try:
        resultValue = dbQuery[f'{configName}']
    except KeyError:
        em = discord.Embed(color=failEmbedColor)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
    if type(resultValue) is list:
        # Probably not the best way to determine if a key is a role list or not
        if 'role' in configName.lower():
            if len(resultValue) > 0:
                for index, item in enumerate(resultValue):
                    foundRole = discord.utils.get(ctx.guild.roles, id=int(item))
                    em.add_field(name=f'{index + 1}', value=f'{foundRole.mention} (ID: {item})', inline=False)
                await ctx.send('', embed=em)
                return
        else:
            if len(resultValue) > 0:
                for index, item in enumerate(resultValue):
                    em.add_field(name=f'{item + 1}', value=f'{item}', inline=False)
                await ctx.send('', embed=em)
                return
    else:
        em.add_field(name=f'{configName}:', value=f'{resultValue}')
        await ctx.send('', embed=em)
        return
   # em.add_field(name='Value', value=resultValue, inline=False)
    await ctx.send('', embed=em)
    return

async def showDefaultConfig(ctx, dbQuery, configName):
    em = discord.Embed(color=embedColor)
    em.set_author(name=f'Results for config {configName}')
    try:
        resultValue = dbQuery[f'{configName}']
    except KeyError:
        em = discord.Embed(color=failEmbedColor)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
    if type(resultValue) is list:
        # Probably not the best way to determine if a key is a role list or not
        if 'role' in configName.lower():
            if len(resultValue) > 0:
                for index, item in enumerate(resultValue):
                    foundRole = discord.utils.get(ctx.guild.roles, id=int(item))
                    em.add_field(name=f'{index + 1}', value=f'{foundRole.mention} (ID: {item})', inline=False)
                await ctx.send('', embed=em)
                return
        else:
            if len(resultValue) > 0:
                for index, item in enumerate(resultValue):
                    em.add_field(name=f'{item + 1}', value=f'{item}', inline=False)
                await ctx.send('', embed=em)
                return
    else:
        em.add_field(name=f'{configName}:', value=f'{resultValue}')
        await ctx.send('', embed=em)
        return
   # em.add_field(name='Value', value=resultValue, inline=False)
    await ctx.send('', embed=em)
    return


async def setChannelConfig(ctx, dbQuery, configName, configValue, channelID: str = 'currentChannel'):
    em = discord.Embed(color=embedColor)
    if channelID == 'currentChannel':
        channelID = str(ctx.channel.id)
        em.set_author(name=f'Results for config {configName}')
    else:
        em.set_author(name=f'Results for config {configName} for channel ID {channelID}')
    # Sets all keys to lowercase, making search arguments case insensitive
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig'][f'{channelID}']
    except KeyError:
        em = discord.Embed(color=failEmbedColor)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
        # Probably not the best way to determine if a key is a role list or not
    if 'role' in configName.lower():
        if len(ctx.message.role_mentions) > 0:
            foundRole = ctx.message.role_mentions[0]
            configValue = foundRole.id
        else:
            try:
                foundRole = discord.utils.get(ctx.guild.roles, id=int(configValue))
                if foundRole is None:
                    await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setChannelConfig.__name__, configName)
                    return
            except ValueError:
                await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setChannelConfig.__name__, configName)
                return
        if str(configValue) in resultValue[f'{configName}']:
            await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setChannelConfig.__name__, configName) 
            return
        else:
            updateDB = tonkDB.updateRoleList(ctx.guild.id, channelID, configName, configValue, str(datetime.utcnow()))
        if updateDB is not None:
            em.add_field(name=f'Success:', value=f'added {foundRole.mention} (ID: {configValue}) to {configName}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setChannelConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return
    else:
        if (checkConfigSyntax(ctx, configName, configValue)) is not None:
            updateDB = tonkDB.updateConfig(ctx.guild.id, channelID, configName, configValue, str(datetime.utcnow()))
        else:
            updateDB = None
        if updateDB is not None:
            em.add_field(name=f'Success', value=f'Set {configName} to {configValue}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setChannelConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return

async def setServerConfig(ctx, dbQuery, configName, configValue):
    em = discord.Embed(color=embedColor)
    em.set_author(name=f'Server Config Results')
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig']['global']
    except KeyError:
        em = discord.Embed(color=failEmbedColor)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
        # Probably not the best way to determine if a key is a role list or not
    if 'role' in configName.lower():
        if len(ctx.message.role_mentions) > 0:
            foundRole = ctx.message.role_mentions[0]
            configValue = foundRole.id
        else:
            try:
                foundRole = discord.utils.get(ctx.guild.roles, id=int(configValue))
                if foundRole is None:
                    await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigSet', setChannelConfig.__name__, configName)
                    return
            except ValueError:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigSet', setServerConfig.__name__, configName)
                return
        try:
            if str(configValue) in resultValue[f'{configName}']:
                await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setServerConfig.__name__, configName) 
                return
            else:
                updateDB = tonkDB.updateRoleList(ctx.guild.id, 'global', configName, configValue, str(datetime.utcnow()))
            if updateDB is not None:
                em.add_field(name=f'Success:', value=f'added {foundRole.mention} (ID: {configValue}) to the server flag {configName}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigSet', setChannelConfig.__name__, configName)
                return
        except KeyError:
            updateDB = tonkDB.updateRoleList(ctx.guild.id, 'globalKeyNotExists', configName, configValue, str(datetime.utcnow()))
            if updateDB is not None:
                em.add_field(name=f'Success:', value=f'added {foundRole.mention} (ID: {configValue}) to the server flag {configName}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigSet', setChannelConfig.__name__, configName)
                return
        await ctx.send('', embed=em)
        return
    else:
        try:
            if str(configValue) in resultValue[f'{configName}']:
                await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setServerConfig.__name__, configName) 
                return
            else:
                if (checkConfigSyntax(ctx, configName, configValue)) is not None:
                    updateDB = tonkDB.updateConfig(ctx.guild.id, 'global', configName, configValue, str(datetime.utcnow()))
                else:
                    updateDB = None
            if updateDB is not None:
                em.add_field(name=f'Success', value=f'Set {configName} to {configValue}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigSet', setChannelConfig.__name__, configName)
                return
        except KeyError:
            if (checkConfigSyntax(ctx, configName, configValue)) is not None:
                updateDB = tonkDB.updateConfig(ctx.guild.id, 'globalKeyNotExists', configName, configValue, str(datetime.utcnow()))
            else:
                updateDB = None
            if updateDB is not None:
                em.add_field(name=f'Success', value=f'Set {configName} to {configValue}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigSet', setChannelConfig.__name__, configName)
                return
        await ctx.send('', embed=em)
        return

async def setDefaultConfig(ctx, dbQuery, configName, configValue):
    em = discord.Embed(color=embedColor)
    em.set_author(name=f'Results')
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig']
    except KeyError:
        em = discord.Embed(color=failEmbedColor)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
        # Probably not the best way to determine if a key is a role list or not
    if 'role' in configName.lower():
        if len(ctx.message.role_mentions) > 0:
            foundRole = ctx.message.role_mentions[0]
            configValue = foundRole.id
        else:
            try:
                foundRole = discord.utils.get(ctx.guild.roles, id=int(configValue))
                if foundRole is None:
                    await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setChannelConfig.__name__, configName)
                    return
            except ValueError:
                await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRoleSet', setDefaultConfig.__name__, configName)
                return
        if str(configValue) in resultValue[f'{configName}']:
            await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setDefaultConfig.__name__, configName) 
            return
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRoleSet', setDefaultConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return
    else:
        if (checkConfigSyntax(ctx, configName, configValue)) is not None:
            updateDB = tonkDB.updateConfig(ctx.guild.id, 'default', configName, configValue, str(datetime.utcnow()))
        else:
            updateDB = None
        if updateDB is not None:
            em.add_field(name=f'Success', value=f'Set {configName} to {configValue}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigSet', setDefaultConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return


async def removeChannelConfig(ctx, dbQuery, configName, configValue, channelID: str = 'currentChannel'):
    em = discord.Embed(color=embedColor)
    if channelID == 'currentChannel':
        channelID = str(ctx.channel.id)
        em.set_author(name=f'Results for config {configName}')
    else:
        em.set_author(name=f'Results for config {configName} for channel ID {channelID}')
    # Sets all keys to lowercase, making search arguments case insensitive
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig'][f'{channelID}']
    except KeyError:
        em = discord.Embed(color=failEmbedColor)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
        # Probably not the best way to determine if a key is a role list or not
    if 'role' in configName.lower():
        updateDB = None
        if len(ctx.message.role_mentions) > 0:
            foundRole = ctx.message.role_mentions[0]
            configValue = foundRole.id
        else:
            try:
                foundRole = discord.utils.get(ctx.guild.roles, id=int(configValue))
            except ValueError:
                await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigRoleRemove', removeChannelConfig.__name__, configName)
                return
        if str(configValue) in resultValue[f'{configName}']:
            for index, item in enumerate(resultValue[f'{configName}']):
                if str(configValue) == str(item):
                    updateDB = tonkDB.removeRoleList(ctx.guild.id, channelID, configName, index, str(datetime.utcnow()))
                    break
        else:
            await sendErrorMessage.invalidArguments(ctx, 'ItemDoesntExist', removeChannelConfig.__name__, configName) 
            return
        if updateDB is not None:
            em.add_field(name=f'Success:', value=f'removed {foundRole.mention} (ID: {configValue}) from {configName}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigRoleRemove', removeChannelConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return
    else:
        updateDB = tonkDB.removeConfig(ctx.guild.id, channelID, configName, str(datetime.utcnow()))
        if updateDB is not None:
            em.add_field(name=f'Success:', value=f'Successfully removed {configName}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigRemove', removeChannelConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return

async def removeServerConfig(ctx, dbQuery, configName, configValue):
    em = discord.Embed(color=embedColor)
    em.set_author(name=f'Results')
    # Sets all keys to lowercase, making search arguments case insensitive
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig']['global']
    except KeyError:
        em = discord.Embed(color=failEmbedColor)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
        # Probably not the best way to determine if a key is a role list or not
    if 'role' in configName.lower():
        if len(ctx.message.role_mentions) > 0:
            foundRole = ctx.message.role_mentions[0]
            configValue = foundRole.id
        else:
            try:
                foundRole = discord.utils.get(ctx.guild.roles, id=int(configValue))
            except ValueError:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigRoleRemove', setServerConfig.__name__, configName)
                return
        try:
            if str(configValue) in resultValue[f'{configName}']:
                for index, item in enumerate(resultValue[f'{configName}']):
                    if str(configValue) == str(item):
                        updateDB = tonkDB.removeRoleList(ctx.guild.id, 'global', configName, index, str(datetime.utcnow()))
                        break
            else:
                await sendErrorMessage.invalidArguments(ctx, 'ItemDoesntExist', setServerConfig.__name__, configName) 
            if updateDB is not None:
                em.add_field(name=f'Success:', value=f'removed {foundRole.mention} (ID: {configValue}) from {configName}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigRoleRemove', setChannelConfig.__name__, configName)
                return
        except KeyError:
            await sendErrorMessage.invalidArguments(ctx, 'ItemDoesntExist', setChannelConfig.__name__)
            return
        await ctx.send('', embed=em)
        return
    else:
        updateDB = tonkDB.removeConfig(ctx.guild.id, 'global', configName, str(datetime.utcnow()))
        if updateDB is not None:
            em.add_field(name=f'Success:', value=f'Successfully removed {configName}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigRemove', removeChannelConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return

async def removeDefaultConfig(ctx, dbQuery, configName, configValue):
    em = discord.Embed(color=embedColor)
    em.set_author(name=f'Results')
    # Sets all keys to lowercase, making search arguments case insensitive
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig']
    except KeyError:
        em = discord.Embed(color=failEmbedColor)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
        # Probably not the best way to determine if a key is a role list or not
    if 'role' in configName.lower():
        if len(ctx.message.role_mentions) > 0:
            foundRole = ctx.message.role_mentions[0]
            configValue = foundRole.id
        else:
            try:
                foundRole = discord.utils.get(ctx.guild.roles, id=int(configValue))
            except ValueError:
                await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRoleRemove', setServerConfig.__name__, configName)
                return
        try:
            if str(configValue) in resultValue[f'{configName}']:
                for index, item in enumerate(resultValue[f'{configName}']):
                    if str(configValue) == str(item):
                        updateDB = tonkDB.removeRoleList(ctx.guild.id, 'default', configName, index, str(datetime.utcnow()))
                        break
            else:
                await sendErrorMessage.invalidArguments(ctx, 'ItemDoesntExist', setServerConfig.__name__, configName) 
            if updateDB is not None:
                em.add_field(name=f'Success:', value=f'removed {foundRole.mention} (ID: {configValue}) from {configName}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRoleRemove', setChannelConfig.__name__, configName)
                return
        except KeyError:
            await sendErrorMessage.invalidArguments(ctx, 'ItemDoesntExist', setChannelConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return
    else:
        updateDB = tonkDB.removeConfig(ctx.guild.id, 'default', configName, str(datetime.utcnow()))
        if updateDB is not None:
            em.add_field(name=f'Success:', value=f'Successfully removed {configName}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRemove', removeChannelConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return