# Utils.py
# Contains utility commands that may be useful in troubleshooting the bot such as role hierarchy.

import asyncio

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