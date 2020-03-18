# Utils.py
# Contains utility commands that may be useful in troubleshooting the bot such as role hierarchy.

import asyncio
import datetime
from datetime import datetime

from assetsTonk import mpaControl
from assetsTonk import sendErrorMessage



def getHighestRole(ctx):
    return ctx.author.top_role



def listRoles(ctx):
    roleList = ''
    for index in range(len(ctx.author.roles)):
        if len(ctx.author.roles) == 0:
            roleList = ('You either dont have a role, or I was not able to get your list of roles.')
        else:
            roleList += (f"{str(index)} - {ctx.author.roles[index].mention} (ID: {ctx.author.roles[index].id})\n")
    return roleList

async def quickClean(ctx, amount):
    try:
        value = int(amount)
    except ValueError:
        await ctx.send('Please provide a number!')
        return
    await ctx.channel.purge(limit=int(amount))
    return

async def checkmpamanagerperm(ctx):
    doIHavePermission = ctx.author.top_role.permissions.manage_emojis
    if doIHavePermission:
        await ctx.send('You have the permissions to start an MPA.')
        return
    else:
        await ctx.send('You do not have the permission to start an MPA. Take a hike.')
        return


async def ffs(ctx, client):
    mpaDBDict = await mpaControl.loadMpaVariables(ctx)
    if type(mpaDBDict) is dict:
        mpaMessageID = next(iter(mpaDBDict['dbQuery']['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}']))
        startTime = mpaDBDict['dbQuery']['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][mpaMessageID]['startDate']
        startTime = datetime.strptime(f"{startTime}", "%Y-%m-%d %H:%M:%S.%f")
        mpaMessage = await ctx.fetch_message(mpaMessageID)
    else:
        if mpaDBDict is KeyError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, ffs.__name__)
        elif mpaDBDict is IndexError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, ffs.__name__)
        return
    if (str(ctx.channel.id)) in (mpaDBDict['mpaChannelList']):
        if mpaDBDict['activeMPAList'][f'{str(ctx.channel.id)}']:
            def is_not_bot(m):
                return m.author != client.user
            await ctx.channel.purge(limit=100, after=startTime, check=is_not_bot)
            return
    else:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, ffs.__name__)