import asyncio
import sys
import re
import discord
import traceback
import datetime
from datetime import datetime

from assetsTonk import sendErrorMessage
from assetsTonk import tonkDB
from assetsTonk import parseDB

# This function takes the message and breaks the arguments down (separated by spaces) and then calls the appropriate functions or throws the appropriate errors based on the input recieved.
async def cmdConfigParser(ctx, *args):
    if len(args) < 2:
        await sendErrorMessage.invalidArguments(ctx, 'badArguments', cmdConfigParser.__name__)
        return
    # Display active configurations on a given server/channel
    elif args[0] == 'show':
        try:
            if args[1].lower() == 'default':
                defaultConfigQuery = tonkDB.configDefaultQueryDB()
                mpaConfig = {key.lower() for key in defaultConfigQuery['Items'][0]['mpaConfig'].keys()}
                try:
                    if args[2].lower() in mpaConfig:
                        await showDefaultConfig(ctx, defaultConfigQuery, args[2])
                except IndexError:
                    traceback.print_exc(file=sys.stdout)
                    await sendErrorMessage.invalidArguments(ctx, 'badShowDefaultArguments', cmdConfigParser.__name__)
                return
            else:
                try:
                    dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
                    if len(ctx.message.channel_mentions) > 0:
                        channelID = ctx.message.channel_mentions[0].id
                    else:
                        channelID = int(args[2])
                    mpaConfig = {key.lower() for key in dbQuery['Items'][0]['mpaConfig'][f'{channelID}'].keys()}
                except IndexError:
                    channelID = None
                    mpaConfig = {key.lower() for key in dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()}
                except TypeError:
                    channelID = None
                    mpaConfig = {key.lower() for key in dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()}
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
                    traceback.print_exc(file=sys.stdout)
                    await sendErrorMessage.invalidArguments(ctx, 'badShowServerArguments', cmdConfigParser.__name__)
            else:
                await showNothing(ctx, args[1])
                return
        except IndexError:
            traceback.print_exc(file=sys.stdout)
            await sendErrorMessage.invalidArguments(ctx, 'badShowArguments', cmdConfigParser.__name__)
            return
    # Sets new configurations
    elif args[0] == 'set':
        try:
            print (args)
            if args[1].lower() == 'default':
                defaultConfigQuery = tonkDB.configDefaultQueryDB()
                mpaConfig = defaultConfigQuery = dbQuery['Items'][0]['mpaConfig'].keys()
                try:
                    if args[2].lower() in mpaConfig:
                        await setDefaultConfig(ctx, defaultConfigQuery, args[2], args[3])
                except IndexError:
                    traceback.print_exc(file=sys.stdout)
                    await sendErrorMessage.invalidArguments(ctx, 'badSetDefaultArguments', cmdConfigParser.__name__)
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
                pass
            if args[1] in mpaConfig:
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
                    traceback.print_exc(file=sys.stdout)
                    await sendErrorMessage.invalidArguments(ctx, 'badSetServerArguments', cmdConfigParser.__name__)
            else:
                await showNothing(ctx, args[1])
                return
        except IndexError:
            traceback.print_exc(file=sys.stdout)
            await sendErrorMessage.invalidArguments(ctx, 'badSetArguments', cmdConfigParser.__name__)
            return
    # Clears configurations
    elif args[0] == 'remove' or args[0] == 'clear':
        return
    return
async def showAllConfigs(ctx, dbQuery, channelID: str = 'allChannels'):
    em = discord.Embed()
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
    em = discord.Embed()
    em.set_author(name=f'Error')
    em.add_field(name='Nothing found!', value=f'Nothing was found for config {configName}')
    await ctx.send('', embed=em)
    return

async def showChannelConfig(ctx, dbQuery, configName, channelID: str = 'currentChannel'):
    em = discord.Embed()
    if channelID == 'currentChannel':
        channelID = str(ctx.channel.id)
        em.set_author(name=f'Results for config {configName}')
    else:
        em.set_author(name=f'Results for config {configName} for channel ID {channelID}')
    # Sets all keys to lowercase, making search arguments case insensitive
    dbQuery_lower = {k.lower():v for k,v in dbQuery['Items'][0]['mpaConfig'][f'{channelID}'].items()}
    configName = configName.lower()
    try:
        resultValue = dbQuery_lower[f'{configName}']
    except KeyError:
        traceback.print_exc(file=sys.stdout)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
    if type(resultValue) is list:
        # Probably not the best way to determine if a key is a role list or not
        if 'role' in configName.lower():
            if len(resultValue) > 1:
                for index, item in enumerate(resultValue):
                    foundRole = discord.utils.get(ctx.guild.roles, id=int(item))
                    em.add_field(name=f'{index + 1}', value=f'{foundRole.mention} (ID: {item})', inline=False)
                await ctx.send('', embed=em)
                return
        else:
            if len(resultValue) > 1:
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
    em = discord.Embed()
    em.set_author(name=f'Results for config {configName}')
    # Sets all keys to lowercase, making search arguments case insensitive
    dbQuery_lower = {k.lower():v for k,v in dbQuery['Items'][0]['mpaConfig']['global'].items()}
    configName = configName.lower()
    try:
        resultValue = dbQuery_lower[f'{configName}']
    except KeyError:
        traceback.print_exc(file=sys.stdout)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
    if type(resultValue) is list:
        # Probably not the best way to determine if a key is a role list or not
        if 'role' in configName.lower():
            if len(resultValue) > 1:
                for index, item in enumerate(resultValue):
                    foundRole = discord.utils.get(ctx.guild.roles, id=int(item))
                    em.add_field(name=f'{index + 1}', value=f'{foundRole.mention} (ID: {item})', inline=False)
                await ctx.send('', embed=em)
                return
        else:
            if len(resultValue) > 1:
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
    em = discord.Embed()
    em.set_author(name=f'Results for config {configName}')
    # Sets all keys to lowercase, making search arguments case insensitive
    dbQuery_lower = {k.lower():v for k,v in dbQuery['Items'][0]['mpaConfig'].items()}
    configName = configName.lower()
    try:
        resultValue = dbQuery_lower[f'{configName}']
    except KeyError:
        traceback.print_exc(file=sys.stdout)
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
    if type(resultValue) is list:
        # Probably not the best way to determine if a key is a role list or not
        if 'role' in configName.lower():
            if len(resultValue) > 1:
                for index, item in enumerate(resultValue):
                    foundRole = discord.utils.get(ctx.guild.roles, id=int(item))
                    em.add_field(name=f'{index + 1}', value=f'{foundRole.mention} (ID: {item})', inline=False)
                await ctx.send('', embed=em)
                return
        else:
            if len(resultValue) > 1:
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
    em = discord.Embed()
    if channelID == 'currentChannel':
        channelID = str(ctx.channel.id)
        em.set_author(name=f'Results for config {configName}')
    else:
        em.set_author(name=f'Results for config {configName} for channel ID {channelID}')
    # Sets all keys to lowercase, making search arguments case insensitive
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig'][f'{channelID}']
    except KeyError:
        traceback.print_exc(file=sys.stdout)
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
            except Exception:
                traceback.print_exc(file=sys.stdout)
                await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigRoleSet', setChannelConfig.__name__)
                return
        if str(configValue) in resultValue[f'{configName}']:
            await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setChannelConfig.__name__) 
            return
        else:
            updateDB = tonkDB.updateRoleList(ctx.guild.id, ctx.channel.id, configName, configValue, str(datetime.utcnow()))
        if updateDB is not None:
            em.add_field(name=f'Success:', value=f'added {foundRole.mention} (ID: {configValue}) to {configName}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigRoleSet', setChannelConfig.__name__)
            return
        await ctx.send('', embed=em)
        return
    else:
        updateDB = tonkDB.updateConfig(ctx.guild.id, ctx.channel.id, configName, configValue, str(datetime.utcnow()))
        if updateDB is not None:
            em.add_field(name=f'{configName}:', value=f'{resultValue}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidChannelConfigSet', setChannelConfig.__name__)
            return
        await ctx.send('', embed=em)
        return

async def setServerConfig(ctx, dbQuery, configName, configValue):
    em = discord.Embed()
    em.set_author(name=f'Results')
    # Sets all keys to lowercase, making search arguments case insensitive
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig']['global']
    except KeyError:
        traceback.print_exc(file=sys.stdout)
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
            except Exception:
                traceback.print_exc(file=sys.stdout)
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigRoleSet', setServerConfig.__name__)
                return
        try:
            if str(configValue) in resultValue[f'{configName}']:
                await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setServerConfig.__name__) 
                return
            else:
                updateDB = tonkDB.updateRoleList(ctx.guild.id, 'global', configName, configValue, str(datetime.utcnow()))
            if updateDB is not None:
                em.add_field(name=f'Success:', value=f'added {foundRole.mention} (ID: {configValue}) to {configName}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigRoleSet', setChannelConfig.__name__)
                return
        except KeyError:
            updateDB = tonkDB.updateRoleList(ctx.guild.id, 'globalKeyNotExists', configName, configValue, str(datetime.utcnow()))
            if updateDB is not None:
                em.add_field(name=f'Success:', value=f'added {foundRole.mention} (ID: {configValue}) to {configName}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigRoleSet', setChannelConfig.__name__)
                return
        await ctx.send('', embed=em)
        return
    else:
        try:
            if str(configValue) in resultValue[f'{configName}']:
                await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setServerConfig.__name__) 
                return
            else:
                updateDB = tonkDB.updateConfig(ctx.guild.id, 'global', configName, configValue, str(datetime.utcnow()))
            if updateDB is not None:
                em.add_field(name=f'{configName}:', value=f'{resultValue}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigRoleSet', setChannelConfig.__name__)
                return
        except KeyError:
            updateDB = tonkDB.updateConfig(ctx.guild.id, 'globalKeyNotExists', configName, configValue, str(datetime.utcnow()))
            if updateDB is not None:
                em.add_field(name=f'{configName}:', value=f'{resultValue}', inline=False)
            else:
                await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigSet', setChannelConfig.__name__)
                return
        await ctx.send('', embed=em)
        return
        # updateDB = tonkDB.updateConfig(ctx.guild.id, 'global', configName, configValue, str(datetime.utcnow()))
        # if updateDB is not None:
        #     em.add_field(name=f'{configName}:', value=f'{resultValue}', inline=False)
        # else:
        #     await sendErrorMessage.invalidArguments(ctx, 'invalidServerConfigSet', setServerConfig.__name__)
        #     return
        # await ctx.send('', embed=em)
        # return

async def setDefaultConfig(ctx, dbQuery, configName, configValue):
    em = discord.Embed()
    em.set_author(name=f'Results')
    # Sets all keys to lowercase, making search arguments case insensitive
    try:
        resultValue = dbQuery['Items'][0]['mpaConfig']
    except KeyError:
        traceback.print_exc(file=sys.stdout)
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
            except Exception:
                traceback.print_exc(file=sys.stdout)
                await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRoleSet', setDefaultConfig.__name__)
                return
        if str(configValue) in resultValue[f'{configName}']:
            await sendErrorMessage.invalidArguments(ctx, 'ItemAlreadyExists', setDefaultConfig.__name__) 
            return
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigRoleSet', setDefaultConfig.__name__)
            return
        await ctx.send('', embed=em)
        return
    else:
        updateDB = tonkDB.updateConfig(ctx.guild.id, 'default', configName, configValue, str(datetime.utcnow()))
        if updateDB is not None:
            em.add_field(name=f'{configName}:', value=f'{resultValue}', inline=False)
        else:
            await sendErrorMessage.invalidArguments(ctx, 'invalidDefaultConfigSet', setDefaultConfig.__name__)
            return
        await ctx.send('', embed=em)
        return