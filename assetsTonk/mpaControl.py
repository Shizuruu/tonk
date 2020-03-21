import asyncio
import datetime
import discord
import time
import traceback
import sys
import re
from datetime import datetime
from dateutil.parser import parse

from assetsTonk import tonkDB
from assetsTonk import parseDB
from assetsTonk import classMatchDev as classMatch
from assetsTonk import sendErrorMessage
from assetsTonk import mpaBanner

def is_pinned(m):
   return m.pinned != True


# Converts EQ List Placeholder objects to strings and then updates the DB with the new batch of information.
async def convertAndUpdateMPADBTable(ctx, listMessage, EQList, SubList, privateMpa, participantCount, maxParticipants, expirationDate):
    tonkDB.updateMPATable(ctx.guild.id, ctx.channel.id, listMessage.id, EQList, SubList, privateMpa, participantCount, maxParticipants, str(expirationDate), str(datetime.utcnow()))
    return

# Same as above but this appends the MPA Start date onto the DB, which is used for message cleanup commands.
# Should be only used by the startmpa command.
async def convertAndStartMPADBTable(ctx, listMessage, EQList, SubList, privateMpa, participantCount, maxParticipants, expirationDate, startDate):
    tonkDB.startMPATable(ctx.guild.id, ctx.channel.id, listMessage.id, EQList, SubList, privateMpa, participantCount, maxParticipants, str(expirationDate), startDate)
    return

# Callable function to read from the DB the mandatory variables needed by the generateList and the updateDB functions.
# Returns a dictionary containing the variables and their mappings.
# This is more or less called by any function that modifies (Not creates!) an MPA list.
async def loadMpaVariables(ctx):
    try:
        varDict = {}
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        defaultConfigQuery = tonkDB.configDefaultQueryDB()
        for index, key in enumerate(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}']):
            listMessageID = int(key)
            break
        # Load the existing MPA Data from the DB
        varDict['dbQuery'] = dbQuery
        varDict['defaultConfigQuery'] = defaultConfigQuery
        varDict['mpaChannelList'] = dbQuery['Items'][0]['mpaChannels']
        varDict['activeMPAList'] = dbQuery['Items'][0]['activeMPAs']
        varDict['participantCount'] = int(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['participantCount'])
        varDict['EQTest'] = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['EQTest']
        varDict['SubDict'] = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['SubList']
        varDict['listMessage'] = await ctx.fetch_message(listMessageID)
        varDict['maxParticipant'] = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][f'{str(listMessageID)}']['maxParticipants']
        varDict['privateMpa'] = parseDB.getPrivateMpa(ctx.channel.id, dbQuery, defaultConfigQuery)
        varDict['classIcons'] = parseDB.getClassIcons(defaultConfigQuery)
        # Load configuration flags for the MPA
        varDict['mpaExpirationTime'] = parseDB.getMpaExpirationTime(ctx.channel.id, dbQuery, defaultConfigQuery)
        return varDict
    except KeyError as e:
        return KeyError
    except IndexError as e:
        return IndexError

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
        await sendErrorMessage.mpaChannelNotEnabled(ctx, startmpa.__name__)
        return
    except IndexError as e:
        print (e)
        await sendErrorMessage.mpaChannelNotEnabled(ctx, startmpa.__name__)
        return
    if (str(ctx.channel.id)) in (mpaChannelList):
        try:
            mpaBanner.getAlias(mpaType.lower())
            mpaFile = mpaBanner.getMpaBanner(mpaType.lower())
            if mpaFile is not None:
                await ctx.send(file=discord.File(mpaFile))
            else:
                await sendErrorMessage.mpaTypeNotFound(ctx, mpaType, startmpa.__name__)
        except FileNotFoundError as e:
            await sendErrorMessage.mpaTypeNotFound(ctx, mpaType, startmpa.__name__)
        # Dont call return here since banners are not required for an mpa to function.
        if mpaType.lower() in specialMPATypes.keys():
            maxParticipant = specialMPATypes[f'{mpaType}']
        else:
            maxParticipant = 12
        if not activeMPAList[f'{str(ctx.channel.id)}']:
            try:
                if broadcast == '':
                    pass
                else:
                    await ctx.channel.send(f' {broadcast}')
                participantCount = 0
                EQTest = []
                SubDict = []
                listMessage = await ctx.channel.send('Please wait... Building list')
                expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaExpirationTime))
                for indexEQTest in range(maxParticipant):
                    EQTest.append(f"PlaceHolder{ctx.channel.id}{listMessage.id}")
                startDate = datetime.utcnow()
                await generateList(ctx, listMessage.id, dbQuery, defaultConfigQuery, EQTest, SubDict, privateMpa, participantCount, maxParticipant, '```dsconfig\nStarting MPA. Please use !addme to sign up!```')
                # Update the DB with the MPA data
                await convertAndStartMPADBTable(ctx, listMessage, EQTest, SubDict, privateMpa, participantCount, maxParticipant, expirationDate, startDate)
                if mpaExpirationEnabled .lower() == 'true':
                    addToExpirationDict = {
                        'expirationDate': expirationDate,
                        'listMessageID': str(listMessage.id)
                    }
                    return addToExpirationDict
                else:
                    return
            except discord.Forbidden:
                print (ctx.author.name + f'Tried to start an MPA at {ctx.guild.name}, but failed.')
                await ctx.author.send('I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                return
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
        await sendErrorMessage.mpaChannelNotEnabled(ctx, startmpa.__name__)


#This function actually performs the removempa command. This is a separate function so that the bot can remove mpas as well.
async def removempa(ctx, client):
    try:
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        mpaChannelList = dbQuery['Items'][0]['mpaChannels']
        activeMpaChannels = dbQuery['Items'][0]['activeMPAs']
        mpaMessageID = next(iter(dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}']))
        startTime = dbQuery['Items'][0]['activeMPAs'][f'{str(ctx.channel.id)}'][mpaMessageID]['startDate']
        startTime = datetime.strptime(f"{startTime}", "%Y-%m-%d %H:%M:%S.%f")
        mpaMessage = await ctx.fetch_message(mpaMessageID)
    except KeyError as e:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, removempa.__name__)
        return
    except IndexError as e:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, removempa.__name__)
        return
    if str(ctx.channel.id) in activeMpaChannels.keys():
        try:
            def is_bot(m):
                return m.author == client.user
            tonkDB.removeMPATable(ctx.guild.id, ctx.channel.id, mpaMessageID, str(datetime.utcnow()))
            print(ctx.author.name + ' Closed an MPA on ' + ctx.guild.name)
            # This is to delete the list and the broadcast message, will only delete messages that are made by the bot
            await ctx.channel.purge(limit=2, around=startTime, check=is_bot)
            # Deletes the rest of the content in the channel, except for pinned messages
            await ctx.channel.purge(limit=100, after=startTime, check=is_pinned)
            return str(mpaMessage.id)
        except KeyError:
            pass
    else:
        await ctx.channel.send('There is no MPA to remove!')

async def addme(ctx, mpaArg: str = 'none'):
    allowJoinMpa = False
    personInMPA = False
    personInReserve = False
    appended = False
    mpaDBDict = await loadMpaVariables(ctx)
    if type(mpaDBDict) is dict:
        classIcons = parseDB.getClassIcons(mpaDBDict['defaultConfigQuery'])
        heroClasses = parseDB.getHeroClasses(mpaDBDict['defaultConfigQuery'])
        subbableHeroClasses = parseDB.getSubbableHeroClasses(mpaDBDict['defaultConfigQuery'])
        allowedMpaRoles = []
        if bool(mpaDBDict['privateMpa']):
            allowedMpaRoles = parseDB.getAllowedMpaRoles(ctx.channel.id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'])
    else:
        if mpaDBDict is KeyError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, addme.__name__)
        elif mpaDBDict is IndexError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, addme.__name__)
        return
    if (str(ctx.channel.id)) in (mpaDBDict['mpaChannelList']):
        for index in range(len(ctx.author.roles)):
            if bool(mpaDBDict['privateMpa']):
                if str(ctx.channel.id) in allowedMpaRoles:
                    allowJoinMpa = True
            else:
                allowJoinMpa = True
        if (allowJoinMpa == False and bool(mpaDBDict['privateMpa'])):
            await ctx.send('You are not whitelisted to join this MPA.')
            await ctx.message.delete()
            return
        else:
            if mpaDBDict['activeMPAList'][f'{str(ctx.channel.id)}']:
                # Determine if the user is already in the MPA List or not.
                for index, item in enumerate(mpaDBDict['EQTest']):
                    if (mpaDBDict['EQTest'][index] == f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}"):
                        pass
                    elif ctx.author.name in item:
                        personInMPA = True
                        break
                 # Determine if the user is already in the Reserve List or not.
                for index, item in enumerate(mpaDBDict['SubDict']):
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
                expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaDBDict['mpaExpirationTime']))
                if mpaArg == 'reserve' or 'reserveme' in ctx.message.content:
                    if not personInMPA: 
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```fix\nReserve list requested. Adding...```")
                        await ctx.message.delete()
                        if personInReserve == False:
                            mpaDBDict['SubDict'].append(ctx.message.author.name)
                            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n+ Added {ctx.author.name} to the Reserve list```')
                        else:
                            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```diff\n+ You are already in the Reserve List```")
                    else:
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```fix\nYou are already in the MPA```")
                        await ctx.message.delete()
                    await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
                    return
                await ctx.message.delete()
                for index, word in enumerate(mpaDBDict['EQTest']):
                    if (word == f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}"):
                        if personInMPA == False:
                            # Is the user in the reserve list?
                            if (ctx.author.name in mpaDBDict['SubDict']):
                                index = mpaDBDict['SubDict'].index(ctx.author.name)
                                if (mpaDBDict['EQTest'][index] == f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}"):
                                    mpaDBDict['EQTest'].pop(index)
                                    EQTest[index] = classRole + '|' + mpaDBDict['SubDict'].pop(index)
                                    mpaDBDict['participantCount'] += 1
                                    await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                            # If user is not in the sublist then we will treat the user as a new member being added in the list.
                            else:
                                if (mpaDBDict['EQTest'][index] == f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}"):
                                    mpaDBDict['EQTest'].pop(index)
                                    mpaDBDict['EQTest'].insert(index, classRole + '|' + ctx.author.name)
                                    mpaDBDict['participantCount'] += 1
                                    await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                        else:
                            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```fix\nYou are already in the MPA```")
                            break
                if not appended:
                    if personInMPA == False: 
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```css\nThe MPA is full. Adding to reserve list.```")
                        if personInReserve == False:
                            mpaDBDict['SubDict'].append(ctx.author.name)
                            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n+ Added {ctx.author.name} to the Reserve list```')
                        else:
                            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```css\nYou are already in the Reserve List```")
                    else:
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```css\nYou are already in the MPA```")
                # End of main function, Update DB here
                await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
                appended = False
                return
            else:
                await ctx.send('There is no MPA to add yourself to!')
                return
    else:
        await ctx.message.delete()
        return

async def addUser(ctx, user, mpaArg):
    mpaDBDict = await loadMpaVariables(ctx)
    if type(mpaDBDict) is dict:
        classIcons = parseDB.getClassIcons(mpaDBDict['defaultConfigQuery'])
        heroClasses = parseDB.getHeroClasses(mpaDBDict['defaultConfigQuery'])
        subbableHeroClasses = parseDB.getSubbableHeroClasses(mpaDBDict['defualtConfigQuery'])
        allowedMpaRoles = []
        if bool(mpaDBDict['privateMpa']):
            allowedMpaRoles = parseDB.getAllowedMpaRoles(ctx.channel.id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'])
    else:
        if mpaDBDict is KeyError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, addUser.__name__)
        elif mpaDBDict is IndexError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, addUser.__name__)
        return
    classRole = ''
    if str(ctx.channel.id) in mpaDBDict['mpaChannelList']:
        if mpaDBDict['activeMPAList'][f'{str(ctx.channel.id)}']:
            if user == "":
                await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```fix\nYou can't add nobody. Are you drunk?```")
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
                expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaDBDict['mpaExpirationTime']))
                if mpaArg == 'reserve' or 'reserve' in ctx.message.content:
                    if not user in mpaDBDict['EQTest']: 
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```fix\nReserve list requested. Adding...```")
                        if not user in mpaDBDict['SubDict']:
                            mpaDBDict['SubDict'].append(user)
                            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n+ Added {user} to the Reserve list```')
                        else:
                            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```diff\n+ That user is already in the Reserve List```")
                    else:
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```fix\nThat user is already in the MPA```")
                    # End of the function, update DB here.
                    await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
                    return
                for index, word in enumerate(mpaDBDict['EQTest']):
                    if (mpaDBDict['EQTest'][index] == f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}"):
                        if not user in mpaDBDict['EQTest']:
                            if (mpaDBDict['EQTest'][index] == f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}"):
                                mpaDBDict['EQTest'].pop(index)
                                mpaDBDict['EQTest'].insert(index, classRole + '|' + user)
                                mpaDBDict['participantCount'] += 1
                                await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n+ Added {user} to the MPA list```')
                                appended = True
                                break
            if not appended:
                await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], "```css\nThe MPA is full. Adding to reserve list.```")
                mpaDBDict['SubDict'].append(user)
                await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n+ Added {user} to the Reserve list```')
            # End of main function, update DB here.
            await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
            appended = False
        else:
            await ctx.send('There is no MPA.')
        await ctx.message.delete()
    else:
        await ctx.send('This command can only be used in a MPA channel!')

# Removes the caller from the MPA.
async def removeme(ctx):
   # global BlankMpaClass
    inMPA = False
    mpaDBDict = await loadMpaVariables(ctx)
    if type(mpaDBDict) is dict:
        classIcons = parseDB.getClassIcons(mpaDBDict['defaultConfigQuery'])
    else:
        if mpaDBDict is KeyError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, removeme.__name__)
        elif mpaDBDict is IndexError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, removeme.__name__)
        return
    if (str(ctx.channel.id)) in (mpaDBDict['mpaChannelList']):
        if mpaDBDict['activeMPAList'][f'{str(ctx.channel.id)}']:
            expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaDBDict['mpaExpirationTime']))
            await ctx.message.delete()
            for index, item in enumerate(mpaDBDict['EQTest']):
                if (mpaDBDict['EQTest'][index] == f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}"):
                    pass
                # If the user is found in the MPA list, remove that item from the list and then push the change to the DB.
                elif ctx.author.name in item:
                    mpaDBDict['EQTest'].pop(index)
                    mpaDBDict['EQTest'].insert(index, f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}")
                    mpaDBDict['participantCount'] -= 1
                    await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n- Removed {ctx.author.name} from the MPA list```')
                    if len(mpaDBDict['SubDict']) > 0:
                        classRole = classIcons['noclass']
                        mpaDBDict['EQTest'][index] = classRole + '|' + mpaDBDict['SubDict'].pop(0)
                        mpaDBDict['participantCount'] += 1
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n- Removed {ctx.author.name} from the MPA list and added {mpaDBDict["EQTest"][index]}```')
                    inMPA = True
                    # End of function with a change made to list, update DB
                    await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
                    return
            if inMPA == False:
                # Check the reserve list to see if the user is in this list, and if so remove the user from that list, update DB
                for index, item in enumerate(mpaDBDict['SubDict']):
                    if ctx.author.name in item:
                        mpaDBDict['SubDict'].pop(index)
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n- Removed {ctx.author.name} from the Reserve list```')
                        # End of function with a change made to list, update DB
                        await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
                        return
                # These cases deal with the user not being in any list at all, and nothing needs to be done in this event.
                    else:
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], '```fix\nYou were not in the MPA list in the first place.```')
                if len(mpaDBDict['SubDict']) == 0:
                    await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], '```fix\nYou were not in the MPA list in the first place.```')

# Manager command to remove a user from the MPA.
async def removeUser(ctx, user):
    mpaDBDict = await loadMpaVariables(ctx)
    if type(mpaDBDict) is dict:
        classIcons = parseDB.getClassIcons(mpaDBDict['defaultConfigQuery'])
    else:
        if mpaDBDict is KeyError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, removeUser.__name__)
        elif mpaDBDict is IndexError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, removeUser.__name__)
        return
    if (str(ctx.channel.id)) in (mpaDBDict['mpaChannelList']):
        expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaDBDict['mpaExpirationTime']))
        if mpaDBDict['activeMPAList'][f'{str(ctx.channel.id)}']:
            if len(mpaDBDict['EQTest']):
                    for index in range(len(mpaDBDict['EQTest'])):
                        appended = False
                        if (mpaDBDict['EQTest'][index] == f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}"):
                            pass
                        elif user.lower() in mpaDBDict['EQTest'][index].lower():
                            # Why so much overhead? Because an item in the EQTest list contains both class information and the name of the user, separated by a | character. So we need to split them up and only use the name part of the item.
                            toBeRemoved = mpaDBDict['EQTest'][index]
                            mpaDBDict['EQTest'][index] = user
                            mpaDBDict['EQTest'].remove(user)
                            mpaDBDict['EQTest'].insert(index, f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}")
                            user = user
                            mpaDBDict['participantCount'] -= 1
                            toBeRemovedName = toBeRemoved.split('|')
                            toBeRemovedName2 = toBeRemovedName[1]
                            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n- Removed {toBeRemovedName2} from the MPA list```')
                            if len(mpaDBDict['SubDict']) > 0:
                                classRole = classIcons['noclass']
                                mpaDBDict['EQTest'][index] = classRole + '|' + mpaDBDict['SubDict'].pop(0)
                                tobenamed = mpaDBDict['EQTest'][index].split()
                                toBeNamed2 = tobenamed[1]
                                mpaDBDict['participantCount'] += 1
                                await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n- Removed {toBeRemoved} from the MPA list and added {toBeNamed2}```')
                            appended = True
                            # Write was made, updating the DB
                            await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
                            return
                    if not appended:
                        for index in range(len(mpaDBDict['SubDict'])):
                            appended = False
                            if user in mpaDBDict['SubDict'][index]:
                                toBeRemoved = mpaDBDict['SubDict'][index]
                                mpaDBDict['SubDict'][index] = user
                                mpaDBDict['SubDict'].remove(user)
                                user = user
                                await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n- Removed {toBeRemoved} from the Reserve list```')
                                appended = True
                                # Write was made, updating DB
                                await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
                                return
                    if not appended:    
                        await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f"```fix\nPlayer {user} does not exist in the MPA list```")
            else:
                await ctx.send("There are no players in the MPA.")
        else:
            await ctx.send('There is no MPA.')
        await ctx.message.delete()
    else:
        await ctx.send('This command can only be used in a MPA Channel!')

# Opens the MPA to non-approved roles.
async def openmpa(ctx):
    mpaDBDict = await loadMpaVariables(ctx)
    if type(mpaDBDict) is dict:
        classIcons = parseDB.getClassIcons(mpaDBDict['defaultConfigQuery'])
    else:
        if mpaDBDict is KeyError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, openmpa.__name__)
        elif mpaDBDict is IndexError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, openmpa.__name__)
        return
    if (str(ctx.channel.id)) in (mpaDBDict['mpaChannelList']):
        if mpaDBDict['guestEnabled'] == True:
            await ctx.send('This MPA is already open!')
            return
        else:
            mpaDBDict['guestEnabled'] = True
            await ctx.send('Opened MPA to non-members!')
            expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaDBDict['mpaExpirationTime']))
            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], '```fix\nMPA is now open to non-members.```')
            await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
            return

# Closes the MPA to only approved roles.
async def closempa(ctx):
    mpaDBDict = await loadMpaVariables(ctx)
    if type(mpaDBDict) is dict:
        classIcons = parseDB.getClassIcons(mpaDBDict['defaultConfigQuery'])
    else:
        if mpaDBDict is KeyError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, closempa.__name__)
        elif mpaDBDict is IndexError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, closempa.__name__)
        return
    if (str(ctx.channel.id)) in (mpaDBDict['mpaChannelList']):
        if mpaDBDict['guestEnabled'] == False:
            await ctx.send('This MPA is already closed!')
            return
        else:
            mpaDBDict['guestEnabled'] = False
            await ctx.send('Closed MPA to Members only.')
            expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaDBDict['mpaExpirationTime']))
            await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], '```fix\nMPA is now closed to non-members```')
            await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
            return

# Changes the class of the caller to another one they specify. Or none if they call for none of the classes.
async def changeClass(ctx, mpaArg):
    inMPA = False
    mpaDBDict = await loadMpaVariables(ctx)
    if type(mpaDBDict) is dict:
        classIcons = parseDB.getClassIcons(mpaDBDict['defaultConfigQuery'])
        heroClasses = parseDB.getHeroClasses(mpaDBDict['defaultConfigQuery'])
        subbableHeroClasses = parseDB.getSubbableHeroClasses(mpaDBDict['defaultConfigQuery'])
    else:
        if mpaDBDict is KeyError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, changeClass.__name__)
        elif mpaDBDict is IndexError:
            await sendErrorMessage.mpaChannelNotEnabled(ctx, changeClass.__name__)
        return
    if str(ctx.channel.id) in mpaDBDict['mpaChannelList']:
        if mpaDBDict['activeMPAList'][f'{str(ctx.channel.id)}']:
            expirationDate = (int(time.mktime(datetime.now().timetuple())) + int(mpaDBDict['mpaExpirationTime']))
            await ctx.message.delete()
            if len(mpaArg) > 2:
                if len(mpaArg) == 4 and mpaArg != 'none':
                    classSplit = re.findall('..', mpaArg)
                    #for item in classSplit:
                     #   print(item)
                    mpaClass1 = classMatch.findClass(classSplit[0])
                    mpaClass2 = classMatch.findClass(classSplit[1])
                    newRoleName = mpaClass1.capitalize()
                    if mpaClass1 == mpaClass2:
                        mpaClass2 = classMatch.findClass('NoClass')
                    if classSplit[0] not in heroClasses and classSplit[1] in subbableHeroClasses or str(mpaClass2) == str(classMatch.findClass('NoClass')):
                        newRole = classIcons[mpaClass1] + classIcons[mpaClass2]
                    elif classSplit[0] in heroClasses or classSplit[1] in heroClasses or str(mpaClass2) == str(classMatch.findClass('NoClass')):
                        newRole = classIcons[mpaClass1]
                    else:
                        newRole = classIcons[mpaClass1] + classIcons[mpaClass2]
                        newRoleName += f'/{mpaClass2.capitalize()}'

                elif len(mpaArg) > 1:
                    classSplit = re.findall('..', mpaArg)
                  #  for item in classSplit:
                   #     print(item)
                    mpaClass1 = classMatch.findClass(classSplit[0])
                    newRole = classIcons[mpaClass1]
                    newRoleName = classMatch.findClassName(mpaClass1)
                    print(newRole)
            else:
                mpaClass = classMatch.findClass(mpaArg)
                newRole = classIcons[mpaClass]
                newRoleName = classMatch.findClassName(mpaClass)
            for index, item in enumerate(mpaDBDict['EQTest']):
                if (mpaDBDict['EQTest'][index]) == f"PlaceHolder{ctx.channel.id}{mpaDBDict['listMessage'].id}":
                    pass
                elif ctx.author.name in item:
                    mpaDBDict['EQTest'].pop(index)
                    mpaDBDict['EQTest'].insert(index, newRole + '|' + ctx.author.name)
                    await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], f'```diff\n+ Changed {ctx.author.name}\'s class to ' + newRoleName + '```')
                    inMPA = True
                    await convertAndUpdateMPADBTable(ctx, mpaDBDict['listMessage'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], expirationDate)
                    return
            if inMPA == False:
                await generateList(ctx, mpaDBDict['listMessage'].id, mpaDBDict['dbQuery'], mpaDBDict['defaultConfigQuery'], mpaDBDict['EQTest'], mpaDBDict['SubDict'], mpaDBDict['privateMpa'], mpaDBDict['participantCount'], mpaDBDict['maxParticipant'], '```fix\nYou are not in the MPA!```')
        else:
            await ctx.send('There is no MPA.')
    else:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, changeClass.__name__)



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
    for word in EQList:
        if (word == f"PlaceHolder{ctx.channel.id}{listMessageID}"):
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

    if privateMpa.lower() == 'true':
        mpaFriendly = 'Yes'
    else:
        mpaFriendly = 'No'
        
    em = discord.Embed(description='Use `!addme` to sign up \nOptionally you can add your class & subclass after addme. Example. `!addme brhu` \nUse `!removeme` to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.', colour=embedColor)
    em.add_field(name='Meeting at', value=f'`Block {mpaBlockNumber}`', inline=True)
    em.add_field(name='Party Status', value='`' + str(participantCount) + '/' + str(maxParticipants) + '`', inline=True)
    em.add_field(name='MPA Open to everyone?', value='`' + mpaFriendly + '`', inline=False)
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
        traceback.print_exc(file=sys.stdout)
        #MPACount += 1
       # await client.get_channel(OtherIDDict['ControlPanel']).send('```css\n' + ctx.author.name + '#' + str(ctx.author.discriminator) + ' (ID: ' + str(ctx.author.id) + ') ' + 'Started an MPA on ' + ctx.guild.name + '\nAmount of Active MPAs: ' + str(MPACount) + '\nTimestamp: ' + str(datetime.now()) + '```')
        #print('Amount of Active MPAs: ' + str(MPACount))
        #mpaMessage = await ctx.channel.send('', embed=em)
    except Exception:
        traceback.print_exc(file=sys.stdout)

