import asyncio
import sys
import re
import json
import discord

helpFile = open('assetsTonk/helpTexts/configUsage.json')
helpDict = json.loads(helpFile.read())
ConfigFile = open('assetsTonk/configs/TonkDevConfig.json')
ConfigDict = json.loads(ConfigFile.read())
commandPrefix = f"{ConfigDict['COMMAND_PREFIX']}"
commandPrefix = f"{commandPrefix}config"

async def mpaChannelNotEnabled(ctx, commandName):
    errorID = 'igama'
    print (f'Error {mpaChannelNotEnabled.__name__} called by {ctx.author.name} (ID: {ctx.author.id}), command called from: {commandName}')
    await ctx.send(f'This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.\nError ID: {errorID}')
    return

async def noCommandPermissions(ctx, commandName):
    errorID = 'ikubi'
    print (f'Error {noCommandPermissions.__name__} called by {ctx.author.name} (ID: {ctx.author.id}), command called from: {commandName}')
    await ctx.send(f'You do not have permissions to use this command.\nError ID: {errorID}')
    return

async def mpaTypeNotFound(ctx, mpaType, commandName):
    errorID = 'agurus'
    print (f'Error {noCommandPermissions.__name__} called by {ctx.author.name} (ID: {ctx.author.id}), command called from: {commandName}')
    await ctx.send(f'Unable to find a banner with the name {mpaType}! Please check your spelling.\nError ID: {errorID}')
    return

async def invalidArguments(ctx, invalidType, commandName, commandArgs):
    errorID = 'otamay'
    print (f'Error {invalidArguments.__name__} ({invalidType}) called by {ctx.author.name} (ID: {ctx.author.id}), command called from: {commandName}')
    #await ctx.send('Invalid parameter specified')
    em = discord.Embed(color=discord.Colour(value=int("ce0000", 16)))
    em.set_author(name="Invalid Parameter specified")
    if invalidType == 'invalidChannelConfigSet':
        changeType = 'set'
        if commandArgs in helpDict.keys():
            em.add_field(name='Usage', value=f"`{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['setUsage']}`", inline=False)
            em.add_field(name='Where', value=f"{helpDict[f'{commandArgs}']['where']}", inline=False)
            em.add_field(name='Example', value=f"```{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['example']}```", inline=False)
    elif invalidType == 'invalidChannelConfigRoleRemove':
        changeType = 'remove'
        if commandArgs in helpDict.keys():
            em.add_field(name='Usage', value=f"`{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['removeUsage']}`", inline=False)
            em.add_field(name='Where', value=f"{helpDict[f'{commandArgs}']['where']}", inline=False)
    elif invalidType == 'invalidChannelConfigRemove':
        changeType = 'remove'
        if commandArgs in helpDict.keys():
            em.add_field(name='Usage', value=f"`{commandPrefix} {helpDict[f'{commandArgs}']['removeUsage']}`", inline=False)
    elif invalidType == 'invalidServerConfigSet':
        changeType = 'set server'
        if commandArgs in helpDict.keys():
            em.add_field(name='Usage', value=f"`{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['setUsage']}`", inline=False)
            em.add_field(name='Where', value=f"{helpDict[f'{commandArgs}']['where']}", inline=False)
            em.add_field(name='Example', value=f"```{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['example']}```", inline=False)
    elif invalidType == 'invalidServerConfigRoleRemove':
        changeType = 'remove server'
        if commandArgs in helpDict.keys():
            em.add_field(name='Usage', value=f"`{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['removeUsage']}`", inline=False)
            em.add_field(name='Where', value=f"{helpDict[f'{commandArgs}']['where']}", inline=False)
    elif invalidType == 'invalidServerConfigRemove':
        changeType = 'remove server'
        if commandArgs in helpDict.keys():
            em.add_field(name='Usage', value=f"`{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['removeUsage']}`", inline=False)
    elif invalidType == 'invalidDefaultConfigSet':
        changeType = 'set default'
        if commandArgs in helpDict.keys():
            em.add_field(name='Usage', value=f"`{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['setUsage']}`", inline=False)
            em.add_field(name='Where', value=f"{helpDict[f'{commandArgs}']['where']}", inline=False)
            em.add_field(name='Example', value=f"```{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['example']}```", inline=False)
    elif invalidType == 'invalidDefaultConfigRoleRemove':
        changeType = 'remove default'
        if commandArgs in helpDict.keys():
            em.add_field(name='Usage', value=f"`{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['removeUsage']}`", inline=False)
            em.add_field(name='Where', value=f"{helpDict[f'{commandArgs}']['where']}", inline=False)
    elif invalidType == 'invalidDefaultConfigRemove':
        changeType = 'remove default'
        if commandArgs in helpDict.keys():
            em.add_field(name='Usage', value=f"`{commandPrefix} {changeType} {helpDict[f'{commandArgs}']['removeUsage']}`", inline=False)
    elif invalidType == 'ItemDoesntExist':
        em.add_field(name='Item does not exist', value='The item you specified was not found in the config.', inline=False)
    elif invalidType == 'ItemAlreadyExists':
        em.add_field(name='Item already exists', value='This item is already set to what you are trying to set it to.', inline=False)
    else:
        em.add_field(name='No help found', value="No Usage doc available for this flag.", inline=False)
    await ctx.send('', embed=em)
    return