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
                    print (f'{ctx.author.name} ({ctx.author.id}) has removed {ctx.channel.id} from the MPA channels on {ctx.guild.id}.')
                    await ctx.send(f'Removed channel {ctx.channel.mention} from the MPA channels list.')
                    break
    except Exception as e:
        await ctx.send('Error removing the channel from the list.')
        traceback.print_exc(file=sys.stdout)
        return
