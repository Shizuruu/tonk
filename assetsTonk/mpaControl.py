import asyncio
import datetime
import discord
import json
import time
import traceback
import sys
from datetime import datetime
from dateutil.parser import parse
#from discord.ext import commands

from assetsTonk import tonkDB
from assetsTonk import parseDB
from assetsTonk import MpaMatchDev

# ConfigFile = open('assetsTonk/configs/TonkDevConfig.json')
# ConfigDict = json.loads(ConfigFile.read())
# commandPrefix = f"{ConfigDict['COMMAND_PREFIX']}"
# client = commands.Bot(command_prefix=commandPrefix)

class PlaceHolder():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name)

def is_pinned(m):
   return m.pinned != True

# Function to start an MPA. The message arguement takes the Discord Message object instead of a string. The string is passed to the broadcast arguement
async def startmpa(ctx, broadcast, mpaType):
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
        #listMessage = None
        if mpaType in specialMPATypes.keys():
            maxParticipant = specialMPATypes[f'{mpaType}']
        else:
            maxParticipant = 12
        if not activeMPAList[f'{str(ctx.channel.id)}']:
            if ctx.author.top_role.permissions.manage_emojis or ctx.author.top_role.permissions.administrator or ctx.author == client.user:
                try:
                    if broadcast == '':
                        pass
                    else:
                        await ctx.channel.send(f' {broadcast}')
                    participantCount = 0
                    EQTest = []
                    SubDict = []
                    listMessage = await ctx.channel.send('Please wait... Building list')
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
                                EQTest[index] = f"PlaceHolder{ctx.channel.id}{listMessage.id}"
                    # Update the DB with the MPA data
                    tonkDB.startMPATable(ctx.guild.id, ctx.channel.id, listMessage.id, EQTest, SubDict, guestEnabled, participantCount, maxParticipant, str(expirationDate), startDate)
                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, guestEnabled, participantCount, maxParticipant, '```dsconfig\nStarting MPA. Please use !addme to sign up!```')
                except discord.Forbidden:
                    print (ctx.author.name + f'Tried to start an MPA at {ctx.guild.name}, but failed.')
                    await ctx.author.send('I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                    return

            else:
                await ctx.channel.send('You do not have the permission to do that, starfox.')
        else:
            for index, key in enumerate(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}']):
                listMessageID = int(key)
                break
                # Future code to support multiple MPAs in one channel
                #if (mpaID - 1) == index:
                #    break
            # Because we don't want to accidentally override any list variables if there is already an existing MPA, we take the current data that already exists and pass it into generateList
            participantCount = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['participantCount']
            EQTest = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['EQTest']
            SubDict = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['SubList']
            listMessage = await ctx.fetch_message(listMessageID)
            maxParticipant = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['maxParticipant']
            guestEnabled = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['guestEnabled']
            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, guestEnabled, participantCount, maxParticipant, '```fix\nThere is already an MPA being made here!```')
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


# Arguements to be taken in DB revision: message, dbQuery, EQList, SubDict, maxParticipants, inputstring)
# message: The message object to modify when updating the EQ List display on the channel
# dbQuery: Dictionary object to query configuration items for user/server preferences
# EQList: Actual EQ list data, which will be parsed and displayed on the channel
# SubDict: Reserve list data, same behavior as previously
# guestEnabled: Yes/no for guest enabled
# maxParticipants: Max amount of people in the MPA.
# inputstring: Same behavior as before.
async def generateList(ctx, listMessageID, dbQuery, defaultConfigQuery, EQList, SubDict, guestEnabled, participantCount, maxParticipants, inputstring):
    # global MPACount
    # global BlankMpaClass
    # global inactiveServerIcons
    # global activeServerIcons
    # global classes
    # global OtherIDDict
    # global serverIDDict
    sCount = 1
    mpaFriendly = ''
    classlist = '\n'
    playerlist = '\n'
    splitstr = ''
    ## Start Configuration Queries
    activeServerIcon = parseDB.getActiveServerSlotID(ctx.channel.id, dbQuery, defaultConfigQuery)
    inactiveServerIcon = parseDB.getInactiveServerSlotID(ctx.channel.id, dbQuery, defaultConfigQuery)
    embedColorHex = parseDB.getEmbedColor(ctx.channel.id, dbQuery, defaultConfigQuery)
    mpaBlockNumber = parseDB.getMpaBlock(ctx.channel.id, dbQuery, defaultConfigQuery)
    classIcons = parseDB.getClassIcons(defaultConfigQuery)
    embedColor = embedColorHex.lstrip('#')
    # embedColor = (tuple(int(embedColor[i:i+2], 16) for i in (0, 2, 4)))
    # embedRed = (embedColor[0])
    # embedGreen = (embedColor[1])
    # embedBlue = (embedColor[2])
    embedColor = discord.Colour(value=int(embedColor, 16))
    ## End Configuration queries
    # Get the message object to edit
    #hasAnMPABlock = False
    # Servers with a class.
    for index, item in enumerate(EQList):
        if item == f"PlaceHolder{ctx.channel.id}{listMessageID}":
            EQList[index] = PlaceHolder("")
    for word in EQList:
        if (type(word) is PlaceHolder):
            # CHANGE: Call mpaConfig dict for this setting.
            playerlist += (f'{inactiveServerIcon}\n')
            classlist += (f"{classIcons['noclass']}\n")
            # if ctx.guild.id == serverIDDict['Ishana']:
            #     color[ctx.channel.id] = 0x0196ef
            #     playerlist += (inactiveServerIcons[0] + '\n')
            #     classlist += (classes[BlankMpaClass] + '\n')
            # else:
            #     color[ctx.channel.id] = 0xcc0000
            #     playerlist += (inactiveServerIcons[2] + '\n')
            #     classlist += (classes[BlankMpaClass] + '\n')
        else:
            splitstr = word.split('|')
            classRole = splitstr[0]
            if not classRole.startswith('<'):
                classRole = classIcons['noclass']
                if len(splitstr) < 2:
                    player = splitstr[0]
                else:
                    player = splitstr[1]
            else:
                player = splitstr[1]
            ## I believe this was originally coded to handle some other action when a player is removed, but after some code changes this ended up just being the same task in every
            # if else block.. so this variable might actually not be needed anymore.
                # if playerRemoved[ctx.channel.id] == True:
                #     player = splitstr[1]
                #     playerRemoved[ctx.channel.id] = False
                # else:
            #     player = splitstr[1]
            # else:

            # CHANGE: Instead of activeserverIcons, use the emoji ID from the database. Can pass the dbQuery object and just query that variable here for the information.
            # if ctx.guild.id == serverIDDict['Ishana']:
            #     playerlist += (activeServerIcons[0] + ' ' + player + '\n')
            # else:
            playerlist += (f"{activeServerIcon} {player}\n")
            classlist += (f"{classRole}\n")

    if len(SubDict) > 0:
        playerlist += ('\n**Reserve List**:\n')
        for word in SubDict:
            playerlist += (f"{str(sCount)}. {word}\n")
            sCount += 1 

    # # CHANGE: Call mpaConfig dict for this setting.
    # if str(ctx.guild.id) in mpaBlockConfigDict:
    #     mpaBlockNumber = mpaBlockConfigDict[str(ctx.guild.id)]
    #     hasAnMPABlock = True

    # CHANGE: Call mpaConfig dict for this setting.        
    if guestEnabled:
        mpaFriendly = 'Yes'
    else:
        mpaFriendly = 'No'
        
    em = discord.Embed(description='Use `!addme` to sign up \nOptionally you can add your class & subclass after addme. Example. `!addme brhu` \nUse `!removeme` to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.', colour=embedColor)
    #if hasAnMPABlock == True:
    em.add_field(name='Meeting at', value=f'`Block {mpaBlockNumber}`', inline=True)
    # if ctx.guild.id == serverIDDict['Ishana']:
    #     em.add_field(name='Party Status', value='`' + str(participantCount[ctx.channel.id]) + '/' + str(totalPeople[ctx.channel.id]) + '`', inline=True)
    # else:
    em.add_field(name='Party Status', value='`' + str(participantCount) + '/' + str(maxParticipants) + '`', inline=True)
   # if ctx.guild.id == serverIDDict['Ishana']:
    em.add_field(name='MPA Open?', value='`' + mpaFriendly + '`', inline=False)
    # if ctx.guild.id == serverIDDict['Ishana']:
    #     em.add_field(name='Participant List', value=playerlist, inline=True)
    # else:
    em.add_field(name='Participant List', value=playerlist, inline=True)
    em.add_field(name='Class', value=classlist, inline=True)
    em.add_field(name='Last Action', value=inputstring, inline=False)
    em.set_author(name='An MPA is starting!', icon_url=ctx.guild.icon_url)
    try:
        mpaMessage = await ctx.fetch_message(listMessageID)
        await mpaMessage.edit(content='', embed=em)
    except (KeyError, discord.NotFound):
        print(ctx.author.name + ' Started an MPA on ' + ctx.guild.name)
        mpaMessage = await ctx.fetch_message(listMessageID)
        #await mpaMessage.send(embed=em)
        traceback.print_exc(file=sys.stdout)
        #MPACount += 1
       # await client.get_channel(OtherIDDict['ControlPanel']).send('```css\n' + ctx.author.name + '#' + str(ctx.author.discriminator) + ' (ID: ' + str(ctx.author.id) + ') ' + 'Started an MPA on ' + ctx.guild.name + '\nAmount of Active MPAs: ' + str(MPACount) + '\nTimestamp: ' + str(datetime.now()) + '```')
        #print('Amount of Active MPAs: ' + str(MPACount))
        #mpaMessage = await ctx.channel.send('', embed=em)
    except Exception:
        traceback.print_exc(file=sys.stdout)