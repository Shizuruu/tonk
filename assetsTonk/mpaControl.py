import asyncio
import datetime
from dateutil.parser import parse

import tonkDB
import parseDB
import MpaMatchDev

class PlaceHolder():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name)

def is_pinned(m):
   return m.pinned != True

# Function to start an MPA. The message arguement takes the Discord Message object instead of a string. The string is passed to the broadcast arguement
async def startmpa(message, broadcast, mpaType):
    maxParticipant = 12
    try:
        # Query the DB to see if there is an MPA and query for the configuration items
        dbQuery = tonkDB.gidQueryDB(message.guild.id)
        defaultConfigQuery = tonkDB.configDefaultQueryDB()
        mpaChannelList = dbQuery['Items'][0]['mpaChannels']
        activeMPAList = dbQuery['Items'][0]['activeMPAs'][f'{str(message.channel.id)}']
        specialMPATypes = defaultConfigQuery['Items'][0]['specialMpaTypeSize']
        # Load configuration items
        guestEnabled = parseDB.getGuestEnabled(message.channel.id, dbQuery, defaultConfigQuery)
        mpaExpirationEnabled = parseDB.getMpaExpirationEnabled(message.channel.id, dbQuery, defaultConfigQuery)
        mpaExpirationTime = parseDB.getMpaExpirationTime(message.channel.id, dbQuery, defaultConfigQuery)
    except KeyError:
        await message.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    except IndexError:
        await message.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    if (str(message.channel.id)) in (mpaChannelList):
        mpaMap = MpaMatchDev.get_class(mpaType)
        try:
            if mpaMap == 'default':
                pass
            else:
                # CHANGE: Convert to upload from AWS S3
                await message.channel.send(file=discord.File(mpaMap))
        except FileNotFoundError as e:
            await message.channel.send('Unable to find a file with that name! Please check your spelling.')    
            return
        #if mpaType == '8man' or mpaType == 'pvp' or mpaType == 'busterquest' or mpaType == 'hachiman':
        if mpaType in specialMPATypes.keys():
            maxParticipant = 8
        if not str(message.channel.id) in activeMPAList:
            if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator or message.author == client.user:
                try:
                    if broadcast == '':
                        pass
                    else:
                        await message.channel.send(f' {broadcast}')
                    EQTest = list()
                    SubDict = list()
                    #ActiveMPA.append(message.channel.id)
                   # roleAdded[message.channel.id] = False
                    #guestEnabled[message.channel.id] = False
                    #playerRemoved[message.channel.id] = False
                    if mpaExpirationEnabled:
                        expirationDate = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationTime)
                    else:
                        expirationDate = ''
                        # mpaRemoved[message.channel.id] = False
                        # print (expirationDate[message.channel.id])
                    # if eightMan[message.channel.id] == True:
                    #     for index in range(8):
                    #         EQTest[message.channel.id].append(PlaceHolder(""))
                    #     totalPeople[message.channel.id] = 8
                    # else:
                    for indexEQTest in range(maxParticipant):
                        EQTest.append(PlaceHolder(""))
                    startDate = datetime.utcnow()
                    # Since we cannot send placeholder objects up to the database, we convert them into a special string that will be traded out upon query.
                    if any(isinstance(EQItem, PlaceHolder) for EQItem in EQTest):
                        for index, item in enumerate(EQTest):
                            if isinstance(item, PlaceHolder):
                                EQTest[index] = f"PlaceHolder{message.channel.id}{message.id}"
                    # Update the DB with the MPA data
                    tonkDB.startMPATable(message.guild.id, message.channel.id, message.id, EQTest, SubDict, guestEnabled, expirationDate, startDate)
                    await generateList(message, dbQuery, EQTest, SubDict, maxParticipant, '```dsconfig\nStarting MPA. Please use !addme to sign up!```')
                except discord.Forbidden:
                    print (message.author.name + f'Tried to start an MPA at {message.guild.name}, but failed.')
                    await message.author.send('I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                    return

            else:
                await message.channel.send('You do not have the permission to do that, starfox.')
        else:
            await generateList(message, dbQuery, EQTest, SubDict, maxParticipant, '```fix\nThere is already an MPA being made here!```')
    else:
        await message.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')



#This function actually performs the removempa command. This is a separate function so that the bot can remove mpas as well.
async def removempa(message):
    #global MPACount
    try:
        dbQuery = tonkDB.gidQueryDB(message.guild.id)
        mpaChannelList = dbQuery['Items'][0]['mpaChannels']
        activeMpaChannels = dbQuery['Items'][0]['activeMPAs']
        startTime = parse(dbQuery['Items'][0]['activeMPAs'][f'{str(message.channel.id)}']['startDate'])
    except KeyError:
        await message.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    except IndexError:
        await message.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    if str(message.channel.id) in activeMpaChannels.keys():
        try:
            #await ctx.message.delete()
            #del EQTest[message.channel.id]
            tonkDB.removeMPATable(message.guild.id, message.channel.id, message.id)
            # MPACount -= 1
            # mpaRemoved[message.channel.id] = True
            # await client.get_channel(OtherIDDict['ControlPanel']).send('```diff\n- ' + message.author.name + '#' + message.author.discriminator + ' (ID: ' + str(message.author.id) + ') ' + 'Closed an MPA on ' + message.guild.name + '\n- Amount of Active MPAs: ' + str(MPACount) + '\nTimestamp: ' + str(datetime.now()) + '```')
            print(message.author.name + ' Closed an MPA on ' + message.guild.name)
            #print('Amount of Active MPAs: ' + str(MPACount))
            await message.channel.purge(limit=100, after=startTime, check=is_pinned)
            #  participantCount[message.channel.id] = 0
            # index = ActiveMPA.index(message.channel.id)
            # ActiveMPA.pop(index)
        except KeyError:
            pass
    else:
        await message.channel.send('There is no MPA to remove!')