import asyncio
import datetime
import discord
import json
import time
import traceback
import sys
import re
from datetime import datetime
from dateutil.parser import parse
#from discord.ext import commands

from assetsTonk import tonkDB
from assetsTonk import parseDB
from assetsTonk import MpaMatchDev
from assetsTonk import classMatchDev as classMatch

class PlaceHolder():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name)

def is_pinned(m):
   return m.pinned != True

# Converts EQ List Placeholder objects to strings and then updates the DB with the new batch of information.
async def convertAndUpdateMPADBTable(ctx, listMessage, EQList, SubList, privateMpa, participantCount, maxParticipants, expirationDate):
    if any(isinstance(EQItem, PlaceHolder) for EQItem in EQList):
        for index, item in enumerate(EQList):
            if isinstance(item, PlaceHolder):
                EQList[index] = f"PlaceHolder{ctx.channel.id}{listMessage.id}"
    tonkDB.updateMPATable(ctx.guild.id, ctx.channel.id, listMessage.id, EQList, SubList, privateMpa, participantCount, maxParticipants, str(expirationDate), str(datetime.utcnow()))
    return

# Same as above but this appends the MPA Start date onto the DB, which is used for message cleanup commands.
# Should be only used by the startmpa command.
async def convertAndStartMPADBTable(ctx, listMessage, EQList, SubList, privateMpa, participantCount, maxParticipants, expirationDate, startDate):
    if any(isinstance(EQItem, PlaceHolder) for EQItem in EQList):
        for index, item in enumerate(EQList):
            if isinstance(item, PlaceHolder):
                EQList[index] = f"PlaceHolder{ctx.channel.id}{listMessage.id}"
    tonkDB.startMPATable(ctx.guild.id, ctx.channel.id, listMessage.id, EQList, SubList, privateMpa, participantCount, maxParticipants, str(expirationDate), startDate)
    return

async def convertEQListFromDB(ctx, messageID, EQList):
    for index, item in enumerate(EQList):
        if item == f"PlaceHolder{ctx.channel.id}{messageID}":
            EQList[index] = PlaceHolder("")
    return EQList

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
        privateMpa = parseDB.getPrivateMpa(ctx.channel.id, dbQuery, defaultConfigQuery)
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
            if ctx.author.top_role.permissions.manage_emojis or ctx.author.top_role.permissions.administrator:
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
                    # if any(isinstance(EQItem, PlaceHolder) for EQItem in EQTest):
                    #     for index, item in enumerate(EQTest):
                    #         if isinstance(item, PlaceHolder):
                    #             EQTest[index] = f"PlaceHolder{ctx.channel.id}{listMessage.id}"
                    # Update the DB with the MPA data
                    await convertAndStartMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate, startDate)
                    #tonkDB.startMPATable(ctx.guild.id, ctx.channel.id, listMessage.id, EQTest, SubDict, privateMpa, participantCount, maxParticipant, str(expirationDate), startDate)
                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, '```dsconfig\nStarting MPA. Please use !addme to sign up!```')
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
            maxParticipant = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['maxParticipants']
            privateMpa = parseDB.getPrivateMpa(ctx.channel.id, dbQuery, defaultConfigQuery)
            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, '```fix\nThere is already an MPA being made here!```')
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

async def addme(ctx, mpaArg: str = 'none'):
    allowJoinMpa = False
    personInMPA = False
    personInReserve = False
    appended = False
    try:
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        defaultConfigQuery = tonkDB.configDefaultQueryDB()
        for index, key in enumerate(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}']):
            listMessageID = int(key)
            break
        # Load the existing MPA Data from the DB
        mpaChannelList = dbQuery['Items'][0]['mpaChannels']
        activeMPAList = dbQuery['Items'][0]['activeMPAs']
        participantCount = int(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['participantCount'])
        EQTest = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['EQTest']
        EQTest = await convertEQListFromDB(ctx, listMessageID, EQTest)
        SubDict = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['SubList']
        listMessage = await ctx.fetch_message(listMessageID)
        maxParticipant = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['maxParticipants']
        privateMpa = parseDB.getPrivateMpa(ctx.channel.id, dbQuery, defaultConfigQuery)
        # Load configuration flags for the MPA
        mpaExpirationEnabled = parseDB.getMpaExpirationEnabled(ctx.channel.id, dbQuery, defaultConfigQuery)
        mpaExpirationTime = parseDB.getMpaExpirationTime(ctx.channel.id, dbQuery, defaultConfigQuery)
        # Load static variables from the defaults table
        classIcons = parseDB.getClassIcons(defaultConfigQuery)
        heroClasses = parseDB.getHeroClasses(defaultConfigQuery)
        subbableHeroClasses = parseDB.getSubbableHeroClasses(defaultConfigQuery)
        allowedMpaRoles = []
        # Now we need to convert the placeholder strings pulled from the DB over to PlaceHolder objects.
        if bool(privateMpa):
            allowedMpaRoles = parseDB.getAllowedMpaRoles(ctx.channel.id, dbQuery, defaultConfigQuery)
    except KeyError as e:
        await ctx.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    except IndexError as e:
        await ctx.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    if (str(ctx.channel.id)) in (mpaChannelList):
        for index in range(len(ctx.author.roles)):
            if bool(privateMpa):
                if str(ctx.channel.id) in allowedMpaRoles:
                    allowJoinMpa = True
            else:
                allowJoinMpa = True
        if (allowJoinMpa == False and bool(privateMpa) == False):
            await ctx.send('You are not whitelisted to join this MPA.')
            await ctx.message.delete()
            return
        else:
            if activeMPAList[f'{str(ctx.channel.id)}']:
                # Determine if the user is already in the MPA List or not.
                for index, item in enumerate(EQTest):
                    if (type(EQTest[index]) is PlaceHolder):
                        pass
                    elif ctx.author.name in item:
                        personInMPA = True
                        break
                 # Determine if the user is already in the Reserve List or not.
                for index, item in enumerate(SubDict):
                    if ctx.author.name in item:
                        personInReserve = True
                        break
                if len(mpaArg) > 2:
                    if len(mpaArg) == 4:
                        classSplit = re.findall('..', mpaArg)
                        for item in classSplit:
                            print(item)
                        mpaClass1 = classMatch.findClass(classSplit[0])
                        mpaClass2 = classMatch.findClass(classSplit[1])
                        if mpaClass1 == mpaClass2:
                            mpaClass2 = classMatch.findClass('NoClass')
                        if classSplit[0] not in heroClasses and classSplit[1] in subbableHeroClasses or mpaClass2 == classMatch.findClass('NoClass'):
                            classRole = classIcons[mpaClass1] + classIcons[mpaClass2]
                        elif classSplit[0] in heroClasses or classSplit[1] in heroClasses or mpaClass2 == classMatch.findClass('NoClass'):
                            classRole = classIcons[mpaClass1]
                        else:
                            classRole = classIcons[mpaClass1] + classIcons[mpaClass2]
                    elif len(mpaArg) > 1:
                        classSplit = re.findall('..', mpaArg)
                        for item in classSplit:
                            print(item)
                        mpaClass1 = classMatch.findClass(classSplit[0])
                        classRole = classIcons[mpaClass1]
                        print(classRole)
                else:
                    mpaClass = classMatch.findClass(mpaArg)
                    classRole = classIcons[mpaClass]
                if mpaExpirationEnabled:
                    expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaExpirationTime))
                else:
                    expirationDate = ''
                if mpaArg == 'reserve' or 'reserveme' in ctx.message.content:
                    if not personInMPA: 
                        await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```fix\nReserve list requested. Adding...```")
                        await ctx.message.delete()
                        if personInReserve == False:
                            SubDict.append(ctx.message.author.name)
                            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n+ Added {ctx.author.name} to the Reserve list```')
                        else:
                            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```diff\n+ You are already in the Reserve List```")
                    else:
                        await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```fix\nYou are already in the MPA```")
                        await ctx.message.delete()
                    await convertAndUpdateMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate)
                    return
                await ctx.message.delete()
                for index, word in enumerate(EQTest):
                    if isinstance(word, PlaceHolder):
                        if personInMPA == False:
                            # Is the user in the reserve list?
                            if (ctx.author.name in SubDict):
                                index = SubDict.index(ctx.author.name)
                                if isinstance(EQTest[index], PlaceHolder):
                                    EQTest.pop(index)
                                    EQTest[index] = classRole + '|' + SubDict.pop(index)
                                    participantCount += 1
                                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                            # If user is not in the sublist then we will treat the user as a new member being added in the list.
                            else:
                                if isinstance(EQTest[index], PlaceHolder):
                                    EQTest.pop(index)
                                    EQTest.insert(index, classRole + '|' + ctx.author.name)
                                    participantCount += 1
                                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                        else:
                            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```fix\nYou are already in the MPA```")
                           # roleAdded[ctx.channel.id] = False
                            break
                if not appended:
                    if personInMPA == False: 
                        await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```css\nThe MPA is full. Adding to reserve list.```")
                        if personInReserve == False:
                            SubDict.append(ctx.author.name)
                            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n+ Added {ctx.author.name} to the Reserve list```')
                        else:
                            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```css\nYou are already in the Reserve List```")
                    else:
                        await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```css\nYou are already in the MPA```")
                # End of main function, Update DB here
                await convertAndUpdateMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate)
                appended = False
                return
            else:
                await ctx.send('There is no MPA to add yourself to!')
                return
    else:
        await ctx.message.delete()
        return

async def addUser(ctx, user, mpaArg):
   # global appended
    if ctx.author.top_role.permissions.manage_emojis or ctx.author.top_role.permissions.administrator:
        try:
            dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
            defaultConfigQuery = tonkDB.configDefaultQueryDB()
            for index, key in enumerate(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}']):
                listMessageID = int(key)
                break
            # Load the existing MPA Data from the DB
            mpaChannelList = dbQuery['Items'][0]['mpaChannels']
            activeMPAList = dbQuery['Items'][0]['activeMPAs']
            participantCount = int(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['participantCount'])
            EQTest = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['EQTest']
            EQTest = await convertEQListFromDB(ctx, listMessageID, EQTest)
            SubDict = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['SubList']
            listMessage = await ctx.fetch_message(listMessageID)
            maxParticipant = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['maxParticipants']
            privateMpa = parseDB.getPrivateMpa(ctx.channel.id, dbQuery, defaultConfigQuery)
            # Load configuration flags for the MPA
            mpaExpirationEnabled = parseDB.getMpaExpirationEnabled(ctx.channel.id, dbQuery, defaultConfigQuery)
            mpaExpirationTime = parseDB.getMpaExpirationTime(ctx.channel.id, dbQuery, defaultConfigQuery)
            # Load static variables from the defaults table
            classIcons = parseDB.getClassIcons(defaultConfigQuery)
            heroClasses = parseDB.getHeroClasses(defaultConfigQuery)
            subbableHeroClasses = parseDB.getSubbableHeroClasses(defaultConfigQuery)
            allowedMpaRoles = []
            # Now we need to convert the placeholder strings pulled from the DB over to PlaceHolder objects.
            if bool(privateMpa):
                allowedMpaRoles = parseDB.getAllowedMpaRoles(ctx.channel.id, dbQuery, defaultConfigQuery)
        except KeyError as e:
            await ctx.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
            return
        except IndexError as e:
            await ctx.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
            return
        classRole = ''
        if str(ctx.channel.id) in mpaChannelList:
            if activeMPAList[f'{str(ctx.channel.id)}']:
                if user == "":
                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```fix\nYou can't add nobody. Are you drunk?```")
                    appended = True
                else:
                    if mpaArg != 'none':
                        if len(mpaArg) > 2:
                            if len(mpaArg) == 4:
                                classSplit = re.findall('..', mpaArg)
                                for item in classSplit:
                                    print(item)
                                mpaClass1 = classMatch.findClass(classSplit[0])
                                mpaClass2 = classMatch.findClass(classSplit[1])
                                if mpaClass1 == mpaClass2:
                                    mpaClass2 = classMatch.findClass('NoClass')
                                if classSplit[0] not in heroClasses and classSplit[1] in subbableHeroClasses or mpaClass2 == classMatch.findClass('NoClass'):
                                    classRole = classIcons[mpaClass1] + classIcons[mpaClass2]
                                elif classSplit[0] in heroClasses or classSplit[1] in heroClasses or mpaClass2 == classMatch.findClass('NoClass'):
                                    classRole = classIcons[mpaClass1]
                                else:
                                    classRole = classIcons[mpaClass1] + classIcons[mpaClass2]

                            elif len(mpaArg) > 1:
                                classSplit = re.findall('..', mpaArg)
                                for item in classSplit:
                                    print(item)
                                mpaClass1 = classMatch.findClass(classSplit[0])
                                classRole = classIcons[mpaClass1]
                                print(classRole)
                        else:
                            mpaClass = classMatch.findClass(mpaArg)
                            classRole = classIcons[mpaClass]
                    #    roleAdded[ctx.channel.id] = True
                    if mpaExpirationEnabled:
                        expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaExpirationTime))
                    else:
                        expirationDate = ''
                    if mpaArg == 'reserve' or 'reserve' in ctx.message.content:
                        if not user in EQTest: 
                            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```fix\nReserve list requested. Adding...```")
                            if not user in SubDict:
                                SubDict.append(user)
                                await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n+ Added {user} to the Reserve list```')
                            else:
                                await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```diff\n+ That user is already in the Reserve List```")
                        else:
                            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```fix\nThat user is already in the MPA```")
                        # End of the function, update DB here.
                        await convertAndUpdateMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate)
                        return
                    for index, word in enumerate(EQTest):
                        if isinstance(word, PlaceHolder):
                            if not user in EQTest:
                                if isinstance(EQTest[index], PlaceHolder):
                                    EQTest.pop(index)
                                    EQTest.insert(index, classRole + '|' + user)
                                    participantCount += 1
                                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n+ Added {user} to the MPA list```')
                                    appended = True
                                    break
                if not appended:
                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, "```css\nThe MPA is full. Adding to reserve list.```")
                    SubDict.append(user)
                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n+ Added {user} to the Reserve list```')
                # End of main function, update DB here.
                await convertAndUpdateMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate)
                appended = False
            else:
                await ctx.send('There is no MPA.')
            await ctx.message.delete()
        else:
            await ctx.send('This command can only be used in a MPA channel!')
    else:
        await ctx.send("You don't have permissions to use this command")

# Removes the caller from the MPA.
async def removeme(ctx):
   # global BlankMpaClass
    inMPA = False
    try:
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        defaultConfigQuery = tonkDB.configDefaultQueryDB()
        for index, key in enumerate(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}']):
            listMessageID = int(key)
            break
        # Load the existing MPA Data from the DB
        mpaChannelList = dbQuery['Items'][0]['mpaChannels']
        activeMPAList = dbQuery['Items'][0]['activeMPAs']
        participantCount = int(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['participantCount'])
        EQTest = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['EQTest']
        EQTest = await convertEQListFromDB(ctx, listMessageID, EQTest)
        SubDict = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['SubList']
        listMessage = await ctx.fetch_message(listMessageID)
        maxParticipant = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['maxParticipants']
        privateMpa = parseDB.getPrivateMpa(ctx.channel.id, dbQuery, defaultConfigQuery)
        classIcons = parseDB.getClassIcons(defaultConfigQuery)
        # Load configuration flags for the MPA
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
        if activeMPAList[f'{str(ctx.channel.id)}']:
            if mpaExpirationEnabled:
                expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaExpirationTime))
            else:
                expirationDate = ''
            await ctx.message.delete()
            for index, item in enumerate(EQTest):
                if (type(EQTest[index]) is PlaceHolder):
                    pass
                # If the user is found in the MPA list, remove that item from the list and then push the change to the DB.
                elif ctx.author.name in item:
                    EQTest.pop(index)
                    EQTest.insert(index, PlaceHolder(''))
                    participantCount -= 1
                   # playerRemoved[ctx.channel.id] = True
                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n- Removed {ctx.author.name} from the MPA list```')
                    if len(SubDict) > 0:
                        classRole = classIcons['noclass']
                        EQTest[index] = classRole + '|' + SubDict.pop(0)
                        participantCount += 1
                        await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n- Removed {ctx.author.name} from the MPA list and added {EQTest[index]}```')
                    inMPA = True
                    # End of function with a change made to list, update DB
                    await convertAndUpdateMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate)
                    return
            if inMPA == False:
                # Check the reserve list to see if the user is in this list, and if so remove the user from that list, update DB
                for index, item in enumerate(SubDict):
                    if ctx.author.name in item:
                        SubDict.pop(index)
                        await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n- Removed {ctx.author.name} from the Reserve list```')
                        # End of function with a change made to list, update DB
                        await convertAndUpdateMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate)
                        return
                # These cases deal with the user not being in any list at all, and nothing needs to be done in this event.
                    else:
                        await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, '```fix\nYou were not in the MPA list in the first place.```')
                if len(SubDict) == 0:
                    await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, '```fix\nYou were not in the MPA list in the first place.```')

# Manager command to remove a user from the MPA.
async def removeUser(ctx, user):
   # global BlankMpaClass
    try:
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        defaultConfigQuery = tonkDB.configDefaultQueryDB()
        for index, key in enumerate(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}']):
            listMessageID = int(key)
            break
        # Load the existing MPA Data from the DB
        mpaChannelList = dbQuery['Items'][0]['mpaChannels']
        activeMPAList = dbQuery['Items'][0]['activeMPAs']
        participantCount = int(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['participantCount'])
        EQTest = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['EQTest']
        EQTest = await convertEQListFromDB(ctx, listMessageID, EQTest)
        SubDict = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['SubList']
        listMessage = await ctx.fetch_message(listMessageID)
        maxParticipant = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['maxParticipants']
        privateMpa = parseDB.getPrivateMpa(ctx.channel.id, dbQuery, defaultConfigQuery)
        classIcons = parseDB.getClassIcons(defaultConfigQuery)
        # Load configuration flags for the MPA
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
        if mpaExpirationEnabled:
            expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaExpirationTime))
        else:
            expirationDate = ''
        if activeMPAList[f'{str(ctx.channel.id)}']:
            if len(EQTest):
                    for index in range(len(EQTest)):
                        appended = False
                        if (type(EQTest[index]) is PlaceHolder):
                            pass
                        elif user.lower() in EQTest[index].lower():
                            # Why so much overhead? Because an item in the EQTest list contains both class information and the name of the user, separated by a | character. So we need to split them up and only use the name part of the item.
                            toBeRemoved = EQTest[index]
                            EQTest[index] = user
                            EQTest.remove(user)
                            EQTest.insert(index, PlaceHolder(''))
                            user = user
                            participantCount -= 1
                            #playerRemoved[ctx.channel.id] = True
                            toBeRemovedName = toBeRemoved.split('|')
                            toBeRemovedName2 = toBeRemovedName[1]
                            await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n- Removed {toBeRemovedName2} from the MPA list```')
                            if len(SubDict) > 0:
                                classRole = classIcons['noclass']
                                EQTest[index] = classRole + '|' + SubDict.pop(0)
                                tobenamed = EQTest[index].split()
                                toBeNamed2 = tobenamed[1]
                                participantCount += 1
                                await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n- Removed {toBeRemoved} from the MPA list and added {toBeNamed2}```')
                            appended = True
                            # Write was made, updating the DB
                            await convertAndUpdateMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate)
                            return
                    if not appended:
                        for index in range(len(SubDict)):
                            appended = False
                            if user in SubDict[index]:
                                toBeRemoved = SubDict[index]
                                SubDict[index] = user
                                SubDict.remove(user)
                                user = user
                                #   playerRemoved[ctx.channel.id] = True
                                await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f'```diff\n- Removed {toBeRemoved} from the Reserve list```')
                                appended = True
                                # Write was made, updating DB
                                await convertAndUpdateMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate)
                                return
                    if not appended:    
                        await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, f"```fix\nPlayer {user} does not exist in the MPA list```")
            else:
                await ctx.send("There are no players in the MPA.")
        else:
            await ctx.send('There is no MPA.')
        # if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
        #     expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
        await ctx.message.delete()
    else:
        await ctx.send('This command can only be used in a MPA Channel!')

# Arguements to be taken in DB revision: message, dbQuery, EQList, SubDict, maxParticipants, inputstring)
# message: The message object to modify when updating the EQ List display on the channel
# dbQuery: Dictionary object to query configuration items for user/server preferences
# EQList: Actual EQ list data, which will be parsed and displayed on the channel
# SubDict: Reserve list data, same behavior as previously
# privateMpa: Yes/no for guest enabled
# maxParticipants: Max amount of people in the MPA.
# inputstring: Same behavior as before.
async def generateList(ctx, listMessageID, dbQuery, defaultConfigQuery, EQList, SubDict, privateMpa, participantCount, maxParticipants, inputstring):
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
    embedColor = discord.Colour(value=int(embedColor, 16))
    ## End Configuration queries
    EQList = await convertEQListFromDB(ctx, listMessageID, EQList)
    for word in EQList:
        if (type(word) is PlaceHolder):
            playerlist += (f'{inactiveServerIcon}\n')
            classlist += (f"{classIcons['noclass']}\n")
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
            playerlist += (f"{activeServerIcon} {player}\n")
            classlist += (f"{classRole}\n")

    if len(SubDict) > 0:
        playerlist += ('\n**Reserve List**:\n')
        for word in SubDict:
            playerlist += (f"{str(sCount)}. {word}\n")
            sCount += 1 

    if privateMpa:
        mpaFriendly = 'Yes'
    else:
        mpaFriendly = 'No'
        
    em = discord.Embed(description='Use `!addme` to sign up \nOptionally you can add your class & subclass after addme. Example. `!addme brhu` \nUse `!removeme` to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.', colour=embedColor)
    em.add_field(name='Meeting at', value=f'`Block {mpaBlockNumber}`', inline=True)
    em.add_field(name='Party Status', value='`' + str(participantCount) + '/' + str(maxParticipants) + '`', inline=True)
    em.add_field(name='MPA Open?', value='`' + mpaFriendly + '`', inline=False)
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

