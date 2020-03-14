import asyncio
import datetime
import discord
import time
from datetime import datetime
from dateutil.parser import parse

from assetsTonk import tonkDB
from assetsTonk import parseDB
from assetsTonk import MpaMatchDev

class PlaceHolder():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name)

def is_pinned(m):
   return m.pinned != True

# Function to start an MPA. The message arguement takes the Discord Message object instead of a string. The string is passed to the broadcast arguement
async def startmpa(ctx, broadcast, mpaType):
    maxParticipant = 12
    try:
        # Query the DB to see if there is an MPA and query for the configuration items
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        defaultConfigQuery = tonkDB.configDefaultQueryDB()
        mpaChannelList = dbQuery['Items'][0]['mpaChannels']
        activeMPAList = dbQuery['Items'][0]['activeMPAs']
        specialMPATypes = defaultConfigQuery['Items'][0]['specialMpaTypeSize']
        # Load configuration items
        guestEnabled = parseDB.getGuestEnabled(ctx.channel.id, dbQuery, defaultConfigQuery)
        mpaExpirationEnabled = parseDB.getMpaExpirationEnabled(ctx.channel.id, dbQuery, defaultConfigQuery)
        mpaExpirationTime = parseDB.getMpaExpirationTime(ctx.channel.id, dbQuery, defaultConfigQuery)
    except KeyError as e:
        print (e)
        await ctx.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    except IndexError as e:
        print (e)
        await ctx.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    if (str(ctx.channel.id)) in (mpaChannelList):
        mpaMap = MpaMatchDev.get_class(mpaType)
        try:
            if mpaMap == 'default':
                pass
            else:
                # CHANGE: Convert to upload from AWS S3
                await ctx.channel.send(file=discord.File(mpaMap))
        except FileNotFoundError as e:
            await ctx.channel.send('Unable to find a file with that name! Please check your spelling.')    
            return
        if mpaType in specialMPATypes.keys():
            maxParticipant = 8
        if not activeMPAList[f'{str(ctx.channel.id)}']:
            print ('Pass condition #1')
            if ctx.author.top_role.permissions.manage_emojis or ctx.author.top_role.permissions.administrator or ctx.author == client.user:
                try:
                    if broadcast == '':
                        pass
                    else:
                        await ctx.channel.send(f' {broadcast}')
                    EQTest = list()
                    SubDict = list()
                    if mpaExpirationEnabled:
                        expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaExpirationTime))
                    else:
                        expirationDate = ''
                    for indexEQTest in range(maxParticipant):
                        EQTest.append(PlaceHolder(""))
                    startDate = datetime.utcnow()
                    # Since we cannot send placeholder objects up to the database, we convert them into a special string that will be traded out upon query.
                    if any(isinstance(EQItem, PlaceHolder) for EQItem in EQTest):
                        for index, item in enumerate(EQTest):
                            if isinstance(item, PlaceHolder):
                                EQTest[index] = f"PlaceHolder{ctx.channel.id}{ctx.message.id}"
                    # Update the DB with the MPA data
                    tonkDB.startMPATable(ctx.guild.id, ctx.channel.id, ctx.message.id, EQTest, SubDict, guestEnabled, maxParticipant, str(expirationDate), startDate)
                    await generateList(ctx, dbQuery, EQTest, SubDict, maxParticipant, '```dsconfig\nStarting MPA. Please use !addme to sign up!```')
                except discord.Forbidden:
                    print (ctx.author.name + f'Tried to start an MPA at {ctx.guild.name}, but failed.')
                    await ctx.author.send('I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                    return

            else:
                await ctx.channel.send('You do not have the permission to do that, starfox.')
        else:
            await generateList(message, dbQuery, EQTest, SubDict, maxParticipant, '```fix\nThere is already an MPA being made here!```')
    else:
        await ctx.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')



#This function actually performs the removempa command. This is a separate function so that the bot can remove mpas as well.
async def removempa(ctx):
    try:
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        mpaChannelList = dbQuery['Items'][0]['mpaChannels']
        activeMpaChannels = dbQuery['Items'][0]['activeMPAs']
        mpaMessageID = next(iter(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}']))
        startTime = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][mpaMessageID]
    except KeyError as e:
        await ctx.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    except IndexError as e:
        await ctx.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    if str(ctx.channel.id) in activeMpaChannels.keys():
        try:
            tonkDB.removeMPATable(ctx.guild.id, ctx.channel.id, mpaMessageID, str(datetime.utcnow()))
            print(ctx.author.name + ' Closed an MPA on ' + ctx.guild.name)
            await ctx.channel.purge(limit=100, after=startTime, check=is_pinned)
        except KeyError:
            pass
    else:
        await ctx.channel.send('There is no MPA to remove!')