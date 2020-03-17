import asyncio
import datetime
import discord
import time
import traceback
import sys
import re
from datetime import datetime

from assetsTonk import tonkDB
from assetsTonk import sendErrorMessage


async def enablempachannel(ctx):
    try:
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        if (str(ctx.channel.id)) in (dbQuery['Items'][0]['mpaChannels']):
            await ctx.send('This channel is already an active MPA channel!')
            return
        else:
            if (len(dbQuery['Items'][0]['mpaChannels'])) > 0:
                tonkDB.updateMpaChannels(ctx.guild.id, ctx.channel.id, str(datetime.utcnow()))
            else:
                tonkDB.addMpaChannel(ctx.guild.id, ctx.channel.id, str(datetime.utcnow()))
    except KeyError:
        print (f'{ctx.guild.id} is not in the config table. Adding...')
        tonkDB.addMpaChannel(ctx.guild.id, ctx.channel.id, str(datetime.utcnow()))
    # This error indicates that this server is not in the database at all.
    except IndexError:
        if len(dbQuery['Items']) < 1:
            print (f'{ctx.guild.id} is not in the database at all. Adding...')
            tonkDB.addMpaChannel(ctx.guild.id, ctx.channel.id, str(datetime.utcnow()))
    print (f'{ctx.author.name} ({ctx.author.id}) has added {ctx.channel.id} to the MPA channels for {ctx.guild.id}.')
    await ctx.send(f'Added channel {ctx.channel.mention} as an MPA channel.')
    return

async def disablempachannel(ctx):
    dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
    try:
        if (str(ctx.channel.id)) in (dbQuery['Items'][0]['mpaChannels']):
            for index, item in enumerate(dbQuery['Items'][0]['mpaChannels']):
                if str(ctx.channel.id) == str(item):
                    tonkDB.removeMpaChannel(ctx.guild.id, ctx.channel.id, index, str(datetime.utcnow()))
                    await ctx.send(f'Removed channel {ctx.channel.mention} from the MPA channels list.')
                    break
    except Exception as e:
        await ctx.send('Error removing the channel from the list.')
        traceback.print_exc(file=sys.stdout)
        return


# This sets the value for the "Meeting in" section of the MPA list.
async def setmpablock(ctx, blockNumber):
    try:
        if isinstance(int(blockNumber), int):
            if len(str(blockNumber)) > 32:
                await ctx.send('That number is too big! Please try again with a smaller number!')
                return
        else:
            if blockNumber.lower() == 'clear':
                pass
            else:
                await ctx.send('Please provide just the number!')
                return
    except ValueError:
        if blockNumber.lower() == 'clear':
            pass
        else:
            await ctx.send('Please provide just the number!')
            return
    try:
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        if (str(ctx.channel.id)) not in (dbQuery['Items'][0]['mpaChannels']):
            await ctx.send(f'This channel is not enabled as an mpa channel. Please enable mpa functions for this channel with `{commandPrefix}enablempachannel`')
            return
        if blockNumber == dbQuery['Items'][0]['mpaConfig'][f'{ctx.channel.id}']['mpaBlock']:
            await ctx.send(f'This server is already set for block {blockNumber}!')
            return
        elif blockNumber.lower() == 'clear':
            tonkDB.removeMpaBlockNumber(ctx.guild.id, ctx.channel.id, str(datetime.utcnow()))
            await ctx.send('Successfully removed the block from the MPA configuration.')
            return
        else:
            tonkDB.addMpaBlockNumber(ctx.guild.id, ctx.channel.id, blockNumber, str(datetime.utcnow()))
            await ctx.send(f'The MPA block number for this channel is set to {blockNumber}.')
            return
    except IndexError:
        # If indexerror is called, it means the server that is calling this command does not exist in the database and they need to enable an mpachannel to be registered onto the db.
        if len(dbQuery['Items']) < 1:
            await ctx.send(f'Please enable the channel to be used as an MPA channel first with `{commandPrefix}enablempachannel`')
            return
    except KeyError as e:
        # There are a variety of different reasons why KeyErrors generate. Different missing keys will indicate different reasons.
        # If mpaConfig is the missing key, it means this server does not have any mpaConfigs applied to it previously.
        if e.args[0] == 'mpaConfig':
            tonkDB.addMpaBlockNumber(ctx.guild.id, ctx.channel.id, blockNumber, str(datetime.utcnow()))
            await ctx.send(f'The MPA block number for this channel is set to {blockNumber}.')
        # Channel ID being the missing key indicates the channel ID is not in the mpaConfig list before.
        elif e.args[0] == str(ctx.channel.id):
            tonkDB.addMpaBlockNumber(ctx.guild.id, ctx.channel.id, blockNumber, str(datetime.utcnow()))
            await ctx.send(f'The MPA block number for this channel is set to {blockNumber}.')
        # mpaBlock missing means the channel ID does exist in the mpaConfig item, but does not have any mpaBlock variables configured for it.
        elif e.args[0] == 'mpaBlock':
            tonkDB.addMpaBlockNumber(ctx.guild.id, ctx.channel.id, blockNumber, str(datetime.utcnow()))
            await ctx.send(f'The MPA block number for this channel is set to {blockNumber}.')
        # Dump any other errors I cant think of.
        else:
            traceback.print_exc(file=sys.stdout)
            await ctx.send('An error occurred attempting to set this config flag. Please check the console for more details.')
        return
