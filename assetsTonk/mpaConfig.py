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

ConfigFile = open('assetsTonk/configs/TonkConfig.json')
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
            for item in ctx.guild.emojis:
                emoji = f'<:{item.name}:{item.id}>'
                if configValue == emoji:
                    emoji = discord.utils.get(ctx.guild.emojis, id=item.id)
                    break
                else:
                    emoji = None
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
                    print (configValue)
                    embedColor = configValue.lstrip('#')
                    embedColor = discord.Colour(value=int(f"{embedColor}", 16))
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
                return True
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
            elif args[1] in mpaConfig:
                if channelID is not None:
                    await showConfig(ctx, dbQuery, args[1], channelID)
                else:
                    await showConfig(ctx, dbQuery, args[1])
                return
            elif args[1] == 'global':
                mpaConfig = dbQuery['Items'][0]['mpaConfig']['global'].keys()
                try:
                    if args[2] in mpaConfig:
                        await showConfig(ctx, dbQuery, args[2], 'global')
                    elif args[2] == 'all':
                        await showAllConfigs(ctx, dbQuery, 'global')
                    else:
                        await showNothing(ctx, args[2])
                except IndexError:
                    await sendErrorMessage.invalidArguments(ctx, 'badShowGlobalArguments', cmdConfigParser.__name__)
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
                        if args[2] in mpaConfig:
                            await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigSet', cmdConfigParser.__name__, args[2])
                        else:
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
                    await setConfig(ctx, dbQuery, args[1], args[2], channelID)
                else:
                    await setConfig(ctx, dbQuery, args[1], args[2])
                return
            elif args[1] not in mpaConfig and args[1] in defaultMpaConfig:
                if channelID is not None:
                    await setConfig(ctx, dbQuery, args[1], args[2], channelID)
                else:
                    await setConfig(ctx, dbQuery, args[1], args[2])
                return
            elif args[1].lower() == 'global':
                mpaConfig = dbQuery['Items'][0]['mpaConfig']['global'].keys()
                defaultMpaConfig = defaultConfigQuery['Items'][0]['mpaConfig'].keys()
                try:
                    if args[2] in mpaConfig:
                        await setConfig(ctx, dbQuery, args[2], args[3], 'global')
                    elif args[2] not in mpaConfig and args[2] in defaultMpaConfig:
                        await setConfig(ctx, dbQuery, args[2], args[3], 'global')
                    else:
                        await showNothing(ctx, args[2])
                except IndexError:
                    if args[2] in mpaConfig or args[2] in defaultMpaConfig:
                        await sendErrorMessage.invalidArguments(ctx, 'invalidGlobalConfigSet', cmdConfigParser.__name__, args[2])
                    else:
                        await sendErrorMessage.invalidArguments(ctx, 'badSetGlobalArguments', cmdConfigParser.__name__)
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
                        if args[2] in mpaConfig or args[2] in defaultMpaConfig:
                            await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRemove', cmdConfigParser.__name__, args[2])
                        else:
                            await sendErrorMessage.invalidArguments(ctx, 'badRemoveDefaultArguments', cmdConfigParser.__name__)
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
                    await removeConfig(ctx, dbQuery, args[1], args[2], channelID)
                else:
                    try:
                        await removeConfig(ctx, dbQuery, args[1], args[2])
                    except IndexError:
                        await removeConfig(ctx, dbQuery, args[1], '')
                return
            elif args[1].lower() == 'global':
                mpaConfig = dbQuery['Items'][0]['mpaConfig']['global'].keys()
                try:
                    if args[2] in mpaConfig:
                        await removeConfig(ctx, dbQuery, args[2], args[3], 'global')
                    else:
                        await showNothing(ctx, args[2])
                except IndexError:
                    if args[2] in mpaConfig or args[2] in defaultMpaConfig:
                        await sendErrorMessage.invalidArguments(ctx, 'invalidGlobalConfigRemove', cmdConfigParser.__name__, args[2])
                    else:
                        await sendErrorMessage.invalidArguments(ctx, 'badRemoveGlobalArguments', cmdConfigParser.__name__)
            else:
                await showNothing(ctx, args[1])
                return
        except IndexError:
            await sendErrorMessage.invalidArguments(ctx, 'badSetArguments', cmdConfigParser.__name__)
            return
        return
    return
async def showAllConfigs(ctx, dbQuery, channelID: str = 'currentChannel'):
    em = discord.Embed(color=embedColor)
    if channelID == 'currentChannel':
        channelID = str(ctx.channel.id)
        em.set_author(name=f'Results')
    else:
        em.set_author(name=f'Results for {channelID}')
    for key, value in dbQuery['Items'][0]['mpaConfig'][f'{channelID}'].items():
        if type(value) is list:
        # Probably not the best way to determine if a key is a role list or not
            if 'role' in key.lower():
                if len(value) > 0:
                    roleList = ''
                    for index, item in enumerate(value):
                        foundRole = discord.utils.get(ctx.guild.roles, id=int(item))
                        roleList += f'{foundRole.mention} (ID: {item})\n'
                    em.add_field(name=f'{key}', value=f'{roleList}', inline=False)
            else:
                if len(value) > 0:
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

async def showConfig(ctx, dbQuery, configName, channelID: str = 'currentChannel'):
    em = discord.Embed(color=embedColor)
    if channelID == 'currentChannel':
        channelID = str(ctx.channel.id)
        em.set_author(name=f'Results for config {configName}')
    else:
        em.set_author(name=f'Results for config {configName} for {channelID}')
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig'][f'{channelID}'][f'{configName}']
    except KeyError:
        traceback.print_exc(file=sys.stdout)
        print (dbQuery)
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


async def setConfig(ctx, dbQuery, configName, configValue, channelID: str = 'currentChannel'):
    em = discord.Embed(color=embedColor)
    if channelID == 'currentChannel':
        channelID = str(ctx.channel.id)
        em.set_author(name=f'Results for config {configName}')
    else:
        em.set_author(name=f'Results for config {configName} {channelID}')
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
                    await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setConfig.__name__, configName)
                    return
            except ValueError:
                await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setConfig.__name__, configName)
                return
        try:
            if str(configValue) in resultValue[f'{configName}']:
                await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setConfig.__name__, configName) 
                return
            else:
                updateDB = tonkDB.updateRoleList(ctx.guild.id, channelID, configName, configValue, str(datetime.utcnow()))
            if updateDB is not None:
                em.add_field(name=f'Success:', value=f'added {foundRole.mention} (ID: {configValue}) to {configName}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setConfig.__name__, configName)
                return
        except KeyError:
            keyExists = "false"
            updateDB = tonkDB.updateRoleList(ctx.guild.id, channelID, configName, configValue, str(datetime.utcnow()), keyExists)
            if updateDB is not None:
                em.add_field(name=f'Success:', value=f'added {foundRole.mention} (ID: {configValue}) to {configName}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setConfig.__name__, configName)
                return
        await ctx.send('', embed=em)
        return
    else:
        try:
            if str(configValue) in resultValue[f'{configName}']:
                await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setConfig.__name__, configName) 
                return
            else:
                if (checkConfigSyntax(ctx, configName, configValue)) is not None:
                    updateDB = tonkDB.updateConfig(ctx.guild.id, channelID, configName, configValue, str(datetime.utcnow()))
                else:
                    updateDB = None
            if updateDB is not None:
                em.add_field(name=f'Success', value=f'Set {configName} to {configValue}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setConfig.__name__, configName)
                return
        except KeyError:
            if (checkConfigSyntax(ctx, configName, configValue)) is not None:
                keyExists = "false"
                updateDB = tonkDB.updateConfig(ctx.guild.id, channelID, configName, configValue, str(datetime.utcnow()), keyExists)
            else:
                updateDB = None
            if updateDB is not None:
                em.add_field(name=f'Success', value=f'Set {configName} to {configValue}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setConfig.__name__, configName)
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
                    await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setDefaultConfig.__name__, configName)
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


async def removeConfig(ctx, dbQuery, configName, configValue, channelID: str = 'currentChannel'):
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
                await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigRoleRemove', removeConfig.__name__, configName)
                return
        if str(configValue) in resultValue[f'{configName}']:
            for index, item in enumerate(resultValue[f'{configName}']):
                if str(configValue) == str(item):
                    updateDB = tonkDB.removeRoleList(ctx.guild.id, channelID, configName, index, str(datetime.utcnow()))
                    break
        else:
            await sendErrorMessage.invalidArguments(ctx, 'ItemDoesntExist', removeConfig.__name__, configName) 
            return
        if updateDB is not None:
            em.add_field(name=f'Success:', value=f'removed {foundRole.mention} (ID: {configValue}) from {configName}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigRoleRemove', removeConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return
    else:
        updateDB = tonkDB.removeConfig(ctx.guild.id, channelID, configName, str(datetime.utcnow()))
        if updateDB is not None:
            em.add_field(name=f'Success:', value=f'Successfully removed {configName}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigRemove', removeConfig.__name__, configName)
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
                await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRoleRemove', removeDefaultConfig.__name__, configName)
                return
        try:
            if str(configValue) in resultValue[f'{configName}']:
                for index, item in enumerate(resultValue[f'{configName}']):
                    if str(configValue) == str(item):
                        updateDB = tonkDB.removeRoleList(ctx.guild.id, 'default', configName, index, str(datetime.utcnow()))
                        break
            else:
                await sendErrorMessage.invalidArguments(ctx, 'ItemDoesntExist', removeDefaultConfig.__name__, configName) 
            if updateDB is not None:
                em.add_field(name=f'Success:', value=f'removed {foundRole.mention} (ID: {configValue}) from {configName}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRoleRemove', setConfig.__name__, configName)
                return
        except KeyError:
            await sendErrorMessage.invalidArguments(ctx, 'ItemDoesntExist', setConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return
    else:
        updateDB = tonkDB.removeConfig(ctx.guild.id, 'default', configName, str(datetime.utcnow()))
        if updateDB is not None:
            em.add_field(name=f'Success:', value=f'Successfully removed {configName}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRemove', removeConfig.__name__, configName)
            return
        await ctx.send('', embed=em)
        return