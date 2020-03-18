import asyncio
import sys
import re
import discord 

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
            dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
            try:
                channelID = int(args[2])
                mpaConfig = {key.lower() for key in dbQuery['Items'][0]['mpaConfig'][f'{channelID}'].keys()}
            except TypeError:
                channelID = None
                mpaConfig = {key.lower() for key in dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}'].keys()}
            if args[1] == 'all':
                if channelID is not None:
                    await showAllConfigs(ctx, dbQuery, channelID)
                else:
                    showAllConfigs(ctx, dbQuery)
                return
            elif args[1].lower() in mpaConfig:
                if channelID is not None:
                    await showChannelConfig(ctx, dbQuery, args[1], channelID)
                else:
                    await showChannelConfig(ctx, dbQuery, args[1])
                return
            elif args[1].lower() == 'server':
                mpaConfig = {key.lower() for key in dbQuery['Items'][0]['mpaServerConfig'].keys()}
                try:
                    if args[2].lower() in mpaConfig:
                        await showServerConfig(ctx, dbQuery, args[2])
                except IndexError:
                    await sendErrorMessage.invalidArguments(ctx, 'badServerArguments', cmdConfigParser.__name__)
        except IndexError:
            await sendErrorMessage.invalidArguments(ctx, 'badArguments', cmdConfigParser.__name__)
            return
    # Sets new configurations
    elif args[0] == 'set':
        return
    # Clears configurations
    elif args[0] == 'remove' or args[0] == 'clear':
        return
    return


async def showAllConfigs(ctx, dbQuery, channelID: str = 'allChannels'):
    return


async def showChannelConfig(ctx, dbQuery, configName, channelID: str = 'currentChannel'):
    if channelID == 'currentChannel':
        channelID = str(ctx.channel.id)
    em = discord.Embed()
    em.set_author(name=f'Results for config {configName}', icon_url=ctx.guild.icon_url)
    try:
        resultValue = dbQuery['Items'][0][f'{channelID}'][f'{configName}']
    except KeyError:
        em.add_field(name='Nothing found!', value='Nothing was found.')
        await ctx.send('', embed=em)
        return
    if type(resultValue) is list:
        # Probably not the best way to determine if a key is a role list or not
        if 'role' in configName:
            if len(resultValue) > 1:
                for item in resultValue:
                    foundRole = discord.utils.get(ctx.guild.roles, id=int(item))
                    em.add_field(name='', value=f'{foundRole.mention} (ID {item})')
                await ctx.send('', embed=em)
                return
        else:
            if len(resultValue) > 1:
                for item in resultValue:
                    em.add_field(name='', value=f'{item}')
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
    return