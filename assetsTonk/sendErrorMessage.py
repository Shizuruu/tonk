import asyncio
import sys
import re


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

async def invalidArguments(ctx, invalidType, commandName):
    errorID = 'otamay'
    print (f'Error {invalidArguments.__name__} called by {ctx.author.name} (ID: {ctx.author.id}), command called from: {commandName}')
    await ctx.send('Invalid parameter specified')
    return