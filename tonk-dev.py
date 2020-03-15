## DEVELOPMENT VERSION
## DO NOT USE IN PRODUCTION! DUH!

import discord
import asyncio
import traceback
import sys
import os
import re
import datetime
import json
import shlex
import time
from datetime import datetime
from discord.utils import find
from discord.ext import commands
from assetsTonk import MpaMatchDev
from assetsTonk import classMatch
from assetsTonk import tonkHelper
from assetsTonk import tonkDB
from assetsTonk import utils
from assetsTonk import mpaControl
from assetsTonk import parseDB

# These are all the constants that will be used throughout the bot. Most if not all of these are dictionaries that allow for different settings per server/channel to be used.
print ('Beginning bot startup process...\n')

# Reads the config file and load it into memory
ConfigFile = open('assetsTonk/configs/TonkDevConfig.json')
ConfigDict = json.loads(ConfigFile.read())
APIKey = ConfigDict['APIKEY']

start = time.time()
# Main ist to track the actual MPA list
EQTest = {}
# Dictionary that tracks reserves list per MPA
SubDict = {}
# Some servers lock out non-approved roles that they request. Otherwise, this is ignored for any other servers.
# In short, this is a flag for these special servers to say if having non-approved roles are allowed or not.
guestEnabled = {}
# The message that displays the list for an MPA.
EQPostDict = {}
# The total count of MPAs that are active in this bot's running instance
MPACount = 0
# A counter that shows how many users are in an MPA
participantCount = {}
# A flag that reduces the total MPA size if a certain flag is passed when creating an MPA.
eightMan = {}
# An internal flag that tells the bot that a role has been added per channel ID
#roleAdded = {} - DEPRECATED
# Color of the embed per server (uses default if no special color was requested)
color = {}
# An internal flag that tells the bot if a player was removed from a server's MPA
# Deprecated?
#playerRemoved = {}
# Tracks the total people per MPA, changes only if the eightMan flag was set to true for an MPA.
totalPeople = {}
# The expiration time for a given MPA
expirationDate = {}
# The database for scheduled MPAs, separated by channel IDs
mpaScheduleDict = {}
# Internal flag
mpaRemoved = {}
# Internal flag
appended = False

commandPrefix = f"{ConfigDict['COMMAND_PREFIX']}"
client = commands.Bot(command_prefix=commandPrefix)
# Remove the default help command
client.remove_command('help')
lastRestart = str(datetime.now())
# Used with MPACount
ActiveMPA = list()
# Time in seconds until the MPA auto deletes itself
mpaExpirationCounter = 3500
# Time in seconds before the bot warns about inactivity and the deletion notice
mpaWarningCounter = 15
# Constants Dictionary
serverIDDict = {
"Ishana": 159184581830901761, 
"Okra": 153346891109761024,
"Bloop": 226835458552758275,
"RappyCasino": 410601412620320819,
"SupportServer": 518836534875652106
}
OtherIDDict = {
"Tenj": 153273725666590720,
"ControlPanel": 322466466479734784,
"EmojiStorage": 408395363762962432
}

RoleIDDict = {
"IshanaFamilia": 486809791948259328
}



# Checks used throughout the code
def is_bot(m):
   return m.author == client.user
    
def is_not_bot(m):
   return m.author != client.user

# A function that finds the roleID from a debugging message
def findRoleID(roleName, message):
    result = discord.utils.find(lambda m: m.name == roleName, message.guild.roles)
    if result is not None:
        return str(result.id)
    else:
        return 0

print ('Loading configuration database...')

# Create dummy dicts
mpaChannels = {}
mpaExpirationConfig = {}
mpaScheduleDict = {}
mpaBlockConfigDict = {}

# Functions that re-imports the Json Data to the dictionaries
def loadmpaChannels():
    global mpaChannels
    mpachannelsJsonFile = open('assetsTonk/devDB/mpaChannelsDev.json')
    mpachannelsJsonFileRead = mpachannelsJsonFile.read()
    mpaChannels = json.loads(mpachannelsJsonFileRead)
    print ('MPA Channels database loaded!')

def loadmpaAutoExpiration():
    global mpaExpirationConfig
    mpaExpirationJsonFile = open('assetsTonk/devDB/mpaAutoExpirationDev.json')
    mpaExpirationJsonFileRead = mpaExpirationJsonFile.read()
    mpaExpirationConfig = json.loads(mpaExpirationJsonFileRead)
    print ('MPA Auto expiration configs loaded!')

def loadscheduledMpa():
    global mpaScheduleDict
    scheduledMpaFile = open('assetsTonk/devDB/scheduledMpaDev.json')
    scheduledMpaFileRead = scheduledMpaFile.read()
    mpaScheduleDict = json.loads(scheduledMpaFileRead)
    print ('Scheduled MPA Database loaded!')

def loadmpaBlockConfigs():
    global mpaBlockConfigDict
    mpaBlockConfigJsonFile = open('assetsTonk/devDB/mpaBlocksdbDev.json')
    mpaBlockConfigFileRead = mpaBlockConfigJsonFile.read()
    mpaBlockConfigDict = json.loads(mpaBlockConfigFileRead)
    print ('MPA block configs loaded!')

# These functions dump the dictionary when something gets written to the dictionary.
def dumpMpaChannels(dictdata):
    with open('assetsTonk/devDB/mpaChannelsDev.json', 'w') as fp:
        json.dump(dictdata, fp)
    fp.close()
    loadmpaChannels()
    return
def dumpMpaAutoExpiration(dictdata):
    with open("assetsTonk/devDB/mpaAutoExpirationDev.json", 'w') as fp:
        json.dump(mpaExpirationConfig, fp)
    fp.close()
    loadmpaAutoExpiration()
    return
def dumpScheduledMpa(dictdata):
    with open('assetsTonk/devDB/scheduledMpaDev.json', 'w') as fp:
        json.dump(mpaScheduleDict, fp)
    fp.close()
    return
def dumpMpaBlockConfig(dictdata):
    with open("assetsTonk/devDB/mpaBlocksdbDev.json", 'w') as fp:
        json.dump(mpaBlockConfigDict, fp)
    fp.close()
    loadmpaBlockConfigs()
    return

# Reloads all the data files.
def runDataLoadup():
    print ('Running data loadup!')
    loadmpaChannels()
    loadmpaAutoExpiration()
    loadscheduledMpa()
    loadmpaBlockConfigs()

runDataLoadup()


print ('Loading classes list...\n')  
  
with open("assetsTonk/iconLists/classes.txt",'r') as e:
    classesread = e.readlines()
    classes = []
    for i in classesread:
        classes.append(i.strip())
        print (i.strip())

with open("assetsTonk/iconLists/heroClasses.txt",'r') as e:
    classesread = e.readlines()
    heroClasses = []
    for i in classesread:
        heroClasses.append(i.strip())
        print (i.strip())

with open("assetsTonk/iconLists/subbableheroClasses.txt",'r') as e:
    classesread = e.readlines()
    subbableHeroClasses = []
    for i in classesread:
        subbableHeroClasses.append(i.strip())
        print (i.strip())

BlankMpaClass = classMatch.findClass('NoneAtAll')
print ('Classes loaded.\n')

#getTime = datetime.now()

with open("assetsTonk/iconLists/activeServerSlots.txt",'r') as e:
    assRead = e.readlines()
    activeServerIcons = []
    for i in assRead:
        activeServerIcons.append(i.strip())
        
with open("assetsTonk/iconLists/grayServerSlots.txt",'r') as e:
    iassRead = e.readlines()
    inactiveServerIcons = []
    for i in iassRead:
        inactiveServerIcons.append(i.strip())


# Background task that runs every second to check if there's any MPA that will be expiring soon.
async def expiration_checker():
    global mpaWarningCounter
    await client.wait_until_ready()
    for key in expirationDate:
        nowTime = int(time.mktime(datetime.now().timetuple()))
        if (expirationDate[key] - 15) == nowTime and mpaRemoved[key] == False:
            await client.get_channel(key).send(f":warning: **Inactivity Detected! This MPA will be automatically closed in `{mpaWarningCounter}` seconds if no actions are taken!** :warning:")
        if expirationDate[key] == nowTime and mpaRemoved[key] == False:
            print ("Expiration reached")
            await client.get_channel(key).send(f"{command_prefix}removempa")
            mpaRemoved[key] = False

# Background task that ticks every second and will start an mpa if the scheduled time comes
async def mpa_schedulerclock():
    await client.wait_until_ready()
    for key in mpaScheduleDict:
        alreadyHasMPA = False
        nowTime = int(time.mktime(datetime.now().timetuple()))
        try:
            if EQTest[key] is not None:
                alreadyHasMPA = True
        except KeyError:
            pass
        if mpaScheduleDict[key]['scheduledTime'] <= nowTime and alreadyHasMPA == False:
            await client.get_channel(key).send(f"{command_prefix}startmpa {mpaScheduleDict[key]['arguments']}")
            del mpaScheduleDict[key]
            try:
                dumpScheduledMpa(mpaScheduleDict)
                return
            except Exception as e:
                print ('An error occurred while trying to automatically dump the mpaschedule dict to JSON')
                print (e)
                return
        elif alreadyHasMPA == True:
            await client.get_channel(key).send('You know there was supposed to be an MPA scheduled for now but there is already an MPA here! Ignoring the scheduled MPA..')
            del mpaScheduleDict[key]
            try:
                dumpScheduledMpa(mpaScheduleDict)
                return
            except Exception as e:
                print ('An error occurred while trying to automatically dump the mpaschedule dict to JSON')
                print (e)
                return

@client.event
##  GENERAL COMMANDS ##
async def on_message(message):
    global appended
    global MPACount
    global ActiveMPA
    global classes
    global inactiveServerIcons
    global activeServerIcons
    global OtherIDDict
    global serverIDDict
    global RoleIDDict
    global mpaExpirationCounter
    if message.content.startswith('!'):
        print (f'{message.author.name} ({message.author.id}) has called for the command {message.content}')
        # These commands are for Me (Tenj), or whoever runs this bot. 
        if message.content.lower() == '!!shutdown':
            if message.author.id == OtherIDDict['Tenj']:
                if message.guild.id == serverIDDict['Ishana']:
                    await message.channel.send('Shutting down. If anything goes wrong during the downtime, please blame yui.')
                else:
                    await message.channel.send('DONT DO THIS TO ME MA-')
                    shutdownRole = discord.utils.get(client.get_guild(226835458552758275).roles, id=370340076527288321)
                    await client.get_channel(OtherIDDict['ControlPanel']).send(f'Tonk is {shutdownRole.mention}')
                await client.logout()
            else:
                await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        # Closes all MPAs the bot has ever known to be active at this moment. Easy to use before shutting the bot down.
        elif message.content.lower() == '!!burnbabyburn':
            if message.author.id == OtherIDDict['Tenj']:
                if len(ActiveMPA) > 0:
                    for index in range(len(ActiveMPA)):
                        await client.get_channel(ActiveMPA[index]).send('!removempa')
                    await message.channel.send('Successfully closed all existing MPAs on all servers.')
                else:
                    await message.channel.send('No MPAs currently exist.')
            else:
                await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        elif message.content.lower().startswith('!!leaveserver'):
            if message.author.id == OtherIDDict['Tenj']:
                userstr = message.content
                userstr = userstr.replace("!!leaveserver", "")
                userstr = userstr.replace(" ", "")
                await client.get_guild(int(userstr)).leave()
            else:
                await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        elif message.content.lower().startswith('!!findroleid'):
            if message.author.id == OtherIDDict['Tenj']:
                userstr = message.content
                userstr = userstr.replace("!!findroleid", "")
                userstr = userstr.replace(" ", "")
                foundRole = discord.utils.get(message.guild.roles, name=userstr)
                if foundRole is not None:
                    em = discord.Embed(colour=foundRole.colour)
                    em.add_field(name='Role Name:', value=foundRole.name, inline=False)
                    em.add_field(name='Role ID', value=foundRole.id, inline=False)
                    await message.channel.send('', embed=em)
                else:
                    await message.channel.send('Unable to find a role with that name!')
            else:
                await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        elif message.content.lower().startswith('!!announce'):
            if message.author.id == OtherIDDict['Tenj']:
                userstr = message.content
                if message.content.startswith('!!announce'):
                    userstr = userstr.replace("!!announce", "")
                else:
                    userstr = userstr.replace("!!announce", "")
                if message.guild.id == OtherIDDict['EmojiStorage']:
                    return
                else:
                    for item in client.guilds:
                        if item.id == serverIDDict['Bloop'] or item.id == OtherIDDict['EmojiStorage']:
                            pass
                        try:
                            await client.get_channel(item.default_channel.id).send(f'{userstr}')
                            await client.get_channel(OtherIDDict['ControlPanel']).send('Sent announcement to ' + item.name)
                        except AttributeError:
                            await client.get_channel(OtherIDDict['ControlPanel']).send('Error trying to send announcement to ' + item.name)
                            pass
                        await client.get_channel(OtherIDDict['ControlPanel']).send('All announcements sent.')
                # await client.send_message(client.get_channel('326883995641970689'), userstr)
            await message.delete()
        elif message.content.lower() == '!!lastrestart':
            if message.author.id == OtherIDDict['Tenj']:
                await message.channel.send(str(lastRestart))
            else:
                await message.channel.send('Only Tenj may use this command.')
        elif message.content.lower() == '!!listservers':
            serverlist = ''
            if message.author.id == OtherIDDict['Tenj']:
                for item in client.guilds:
                    serverlist += (item.name + f'\n{item.id}' + '\n')
                em = discord.Embed(description=serverlist, colour=0x0099FF)
                em.set_author(name='Joined Servers')
                await message.channel.send('', embed=em)
            else:
                await message.channel.send('CANT LET YOU DO THAT, STARFOX.') 
        elif message.content.lower() == '!!restart':
            if message.author.id == OtherIDDict['Tenj']:
                await message.channel.send('Tonk will now restart!')
                print ('The restart command was issued! Restarting Bot...')
                end = time.time()
                runTime = (end - start)
                restartRole = discord.utils.get(client.get_guild(226835458552758275).roles, id=370339592055947266)
                await client.get_channel(OtherIDDict['ControlPanel']).send(f'Tonk is {restartRole.mention}' + '\nRun time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(runTime)))
                os.execl(sys.executable, *([sys.executable]+sys.argv))
            else:
                await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        elif message.content.lower() == '!!clearconsole':
            if message.author.id == OtherIDDict['Tenj']:
                await message.channel.send('Clearing Console')
                os.system('cls' if os.name == 'nt' else 'clear')
            else:
                await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        # Self calling command to remove MPAs, made specifically so that the bot may call it's own command.
        elif message.content.lower() == '!removempa':
            if message.author == client.user:
                await function_removempa(message)
        elif message.content.lower().startswith('!startmpa'):
            if message.author == client.user:
                splitcmd = shlex.split(f'{message.content}')
                await function_startmpa(message, splitcmd[1], splitcmd[2])
                await message.delete()
        await client.process_commands(message)


# Gets the highesr role for the user calling this command
@client.command(name='gethighestrole')
async def cmd_gethighestrole(ctx):
    result = utils.getHighestRole(ctx)
    await ctx.send(result)
    # if ctx.channel.id not in mpaChannels[str(ctx.guild.id)]:
    #     await ctx.send(ctx.author.top_role)

# Lists all the roles for the user calling this command
@client.command(name='listroles')
async def cmd_listroles(ctx):
    result = utils.listRoles(ctx)
    em = discord.Embed()
    em.add_field(name='Result:', value=result, inline=False)
    await ctx.send('', embed=em)

# Mass purges the channel with a number given. Does not check for anything.
@client.command(name='quickclean')
async def cmd_quickclean(ctx, amount):
    if ctx.author.top_role.permissions.manage_channels:
        await utils.quickClean(ctx, amount)
        return
    else:
        await ctx.send('http://i.imgur.com/FnKySHo.png')
        return

# Checks if the caller has permissions to start an MPA.
@client.command(name='checkmpamanagerperm')
async def cmd_checkmpamanagerperm(ctx):
    await utils.checkmpamanagerperm(ctx)
    return

# Clears out anything that wasn't posted by the bot in an MPA channel. Useful for servers where the MPA channel was filled with chatter and the list was hard to see.
@client.command(name='ffs')
async def cmd_ffs(ctx):
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
        if ctx.author.top_role.permissions.manage_emojis or ctx.author.id == OtherIDDict['Tenj']:
            await ctx.channel.purge(limit=100, after=getTime, check=is_not_bot)
        else:
            await ctx.channel.send('You lack the permissions to use this command.')
    else:
        await ctx.channel.send('This command can only be used in a MPA channel.')

# Starts an MPA with the given arguements. Message and mpaType is optional, and will just fill in with the given data if nothing was put into the command.
# Calls function_startmpa to actually do the legwork
@client.command(name='startmpa')
async def cmd_startmpa(ctx, mpaType: str = 'default', *, message: str = ''):
    # This checks if Tonk has the deleting permission. If it doesn't, don't run the script at all and just stop.
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        print (ctx.author.name + f' Tried to start an MPA at {ctx.message.guild.name}, but failed.')
        await ctx.author.send('I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
        return
    # if message == '':
    #     #newmessage = "ouEPO*#T*#$TH(QETH(PHFGWOUDT#PWIJOYAYAYAYYAYAYAYYAYAYAYAYYAYAYAYYAYAA{IOUHIJ(*)YH#RIOjewfO*HEFU(*Y#@R"
    #     await mpaControl.startmpa(ctx, message, mpaType)
    # else:
    await mpaControl.startmpa(ctx, message, mpaType)

# Closes out the MPA and flushes related data so another MPA can be opened in the same channel at a later date.
@client.command(name='removempa')
async def cmd_removempa(ctx):
    if ctx.author.top_role.permissions.manage_emojis or ctx.author.top_role.permissions.administrator or ctx.author.id == client.user.id:
        await mpaControl.removempa(ctx)
    else:
        await ctx.send('You do not have permissions to remove the mpa.')

# Adds the user into the EQ list in the EQ channel. Optionally takes a class as an arguement. If one is passed, add the class icon and the user's name into the EQ list.
@client.command(name='addme', aliases=['reserveme'])
async def cmd_addme(ctx, mpaArg: str = 'none'):
    await mpaControl.addme(ctx, mpaArg)
#     global appended
#     bypassCheck = False
#     classRole = ''
#     index = 0
#     personInMPA = False
#     personInReserve = False
#    # roleAdded[ctx.channel.id] = False
#     if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
#         for index in range(len(ctx.author.roles)):
#             if ctx.author.roles[index].id == RoleIDDict['IshanaFamilia']:
#                 bypassCheck = True
#                 break
#             elif ctx.author.id == OtherIDDict['Tenj']:
#                 bypassCheck = True
#                 break
#             elif ctx.author.top_role.permissions.manage_emojis:
#                 bypassCheck = True
#                 break
#             elif ctx.guild.id == serverIDDict['Ishana']:
#                 bypassCheck = False
#             else:
#                 bypassCheck = True
#         if (bypassCheck == False and guestEnabled[ctx.channel.id] == False):
#             await generateList(ctx.message, '```fix\nGuests are not allowed to join this MPA.```')
#             await ctx.message.delete()
#             return
#         else:
#             if ctx.channel.id in EQTest:
#                 for index, item in enumerate(EQTest[ctx.channel.id]):
#                     if (type(EQTest[ctx.channel.id][index]) is PlaceHolder):
#                         pass
#                     elif ctx.author.name in item:
#                         personInMPA = True
#                         break
#                 for index, item in enumerate(SubDict[ctx.channel.id]):
#                     if ctx.author.name in item:
#                         personInReserve = True
#                         break
#                 if len(mpaArg) > 2:
#                     if len(mpaArg) == 4:
#                         classSplit = re.findall('..', mpaArg)
#                         for item in classSplit:
#                             print(item)
#                         mpaClass1 = classMatch.findClass(classSplit[0])
#                         mpaClass2 = classMatch.findClass(classSplit[1])
#                         if mpaClass1 == mpaClass2:
#                             mpaClass2 = classMatch.findClass('NoClass')
#                         if classSplit[0] not in heroClasses and classSplit[1] in subbableHeroClasses or mpaClass2 == BlankMpaClass:
#                             classRole = classes[mpaClass1] + classes[mpaClass2]
#                         elif classSplit[0] in heroClasses or classSplit[1] in heroClasses or mpaClass2 == BlankMpaClass:
#                             classRole = classes[mpaClass1]
#                         else:
#                             classRole = classes[mpaClass1] + classes[mpaClass2]

#                     elif len(mpaArg) > 1:
#                         classSplit = re.findall('..', mpaArg)
#                         for item in classSplit:
#                             print(item)
#                         mpaClass1 = classMatch.findClass(classSplit[0])
#                         classRole = classes[mpaClass1]
#                         print(classRole)
#                 else:
#                     mpaClass = classMatch.findClass(mpaArg)
#                     classRole = classes[mpaClass]
#                # roleAdded[ctx.channel.id] = True
#                 if mpaArg == 'reserve' or 'reserveme' in ctx.message.content:
#                     if personInMPA == False: 
#                         await generateList(ctx.message, "```fix\nReserve list requested. Adding...```")
#                         await ctx.message.delete()
#                         if personInReserve == False:
#                             SubDict[ctx.channel.id].append(ctx.message.author.name)
#                             await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the Reserve list```')
#                         else:
#                             await generateList(ctx.message, "```diff\n+ You are already in the Reserve List```")
#                     else:
#                         await generateList(ctx.message, "```fix\nYou are already in the MPA```")
#                         await ctx.message.delete()
#                     return
#                 if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
#                     expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
#                     print (expirationDate[ctx.channel.id])
#                 await ctx.message.delete()
#                 for word in EQTest[ctx.channel.id]:
#                     if isinstance(word, PlaceHolder):
#                         if personInMPA == False:
#                             if (ctx.author.name in SubDict[ctx.channel.id]):
#                                 index = SubDict[ctx.channel.id].index(ctx.author.name)
#                                 if isinstance(EQTest[ctx.channel.id][0], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(0)
#                                     EQTest[ctx.channel.id][0] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][1], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(1)
#                                     EQTest[ctx.channel.id][1] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][2], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(2)
#                                     EQTest[ctx.channel.id][2] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][3], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(3)
#                                     EQTest[ctx.channel.id][3] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][4], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(4)
#                                     EQTest[ctx.channel.id][4] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][5], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(5)
#                                     EQTest[ctx.channel.id][5] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][6], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(6)
#                                     EQTest[ctx.channel.id][6] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][7], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(7)
#                                     EQTest[ctx.channel.id][7] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                     appended = True
#                                     break
#                                 if eightMan[ctx.channel.id] == False:
#                                     if isinstance(EQTest[ctx.channel.id][8], PlaceHolder):
#                                         EQTest[ctx.channel.id].pop(8)
#                                         EQTest[ctx.channel.id][8] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                         participantCount[ctx.channel.id] += 1
#                                         await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                         appended = True
#                                         break
#                                     elif isinstance(EQTest[ctx.channel.id][9], PlaceHolder):
#                                         EQTest[ctx.channel.id].pop(9)
#                                         EQTest[ctx.channel.id][9] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                         participantCount[ctx.channel.id] += 1
#                                         await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                         appended = True
#                                         break
#                                     elif isinstance(EQTest[ctx.channel.id][10], PlaceHolder):
#                                         EQTest[ctx.channel.id].pop(10)
#                                         EQTest[ctx.channel.id][10] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                         participantCount[ctx.channel.id] += 1
#                                         await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                         appended = True
#                                         break
#                                     elif isinstance(EQTest[ctx.channel.id][11], PlaceHolder):
#                                         EQTest[ctx.channel.id].pop(11)
#                                         EQTest[ctx.channel.id][11] = classRole + '|' + SubDict[ctx.channel.id].pop(index)
#                                         participantCount[ctx.channel.id] += 1
#                                         await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
#                                         appended = True
#                                         break
#                             else:
#                                 if isinstance(EQTest[ctx.channel.id][0], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(0)
#                                     EQTest[ctx.channel.id].insert(0, classRole + '|' + ctx.author.name)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][1], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(1)
#                                     EQTest[ctx.channel.id].insert(1, classRole + '|' + ctx.author.name)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][2], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(2)
#                                     EQTest[ctx.channel.id].insert(2, classRole + '|' + ctx.author.name)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][3], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(3)
#                                     EQTest[ctx.channel.id].insert(3, classRole + '|' + ctx.author.name)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][4], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(4)
#                                     EQTest[ctx.channel.id].insert(4, classRole + '|' + ctx.author.name)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][5], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(5)
#                                     EQTest[ctx.channel.id].insert(5, classRole + '|' + ctx.author.name)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][6], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(6)
#                                     EQTest[ctx.channel.id].insert(6, classRole + '|' + ctx.author.name)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                     appended = True
#                                     break
#                                 elif isinstance(EQTest[ctx.channel.id][7], PlaceHolder):
#                                     EQTest[ctx.channel.id].pop(7)
#                                     EQTest[ctx.channel.id].insert(7, classRole + '|' + ctx.author.name)
#                                     participantCount[ctx.channel.id] += 1
#                                     await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                     appended = True
#                                     break
#                                 if eightMan[ctx.channel.id] == False:
#                                     if isinstance(EQTest[ctx.channel.id][8], PlaceHolder):
#                                         EQTest[ctx.channel.id].pop(8)
#                                         EQTest[ctx.channel.id].insert(8, classRole + '|' + ctx.author.name)
#                                         participantCount[ctx.channel.id] += 1
#                                         await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                         appended = True
#                                         break
#                                     elif isinstance(EQTest[ctx.channel.id][9], PlaceHolder):
#                                         EQTest[ctx.channel.id].pop(9)
#                                         EQTest[ctx.channel.id].insert(9, classRole + '|' + ctx.author.name)
#                                         participantCount[ctx.channel.id] += 1
#                                         await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                         appended = True
#                                         break
#                                     elif isinstance(EQTest[ctx.channel.id][10], PlaceHolder):
#                                         EQTest[ctx.channel.id].pop(10)
#                                         EQTest[ctx.channel.id].insert(10, classRole + '|' + ctx.author.name)
#                                         participantCount[ctx.channel.id] += 1
#                                         await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                         appended = True
#                                         break
#                                     elif isinstance(EQTest[ctx.channel.id][11], PlaceHolder):
#                                         EQTest[ctx.channel.id].pop(11)
#                                         EQTest[ctx.channel.id].insert(11, classRole + '|' + ctx.author.name)
#                                         participantCount[ctx.channel.id] += 1
#                                         await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
#                                         appended = True
#                                         break
#                         else:
#                             await generateList(ctx.message, "```fix\nYou are already in the MPA```")
#                            # roleAdded[ctx.channel.id] = False
#                             break
#                 if not appended:
#                     if personInMPA == False: 
#                         await generateList(ctx.message, "```css\nThe MPA is full. Adding to reserve list.```")
#                         if personInReserve == False:
#                             SubDict[ctx.channel.id].append(ctx.author.name)
#                             await generateList(ctx.message, f'```diff\n+ Added {ctx.author.name} to the Reserve list```')
#                         else:
#                             await generateList(ctx.message, "```css\nYou are already in the Reserve List```")
#                     else:
#                         await generateList(ctx.message, "```css\nYou are already in the MPA```")
#                 appended = False     
#             else:
#                 await ctx.send('There is no MPA to add yourself to!')
#     else:
#         await ctx.message.delete()

# Manager command that adds a custom name to the MPA.
@client.command(name='add', aliases=['reserve'])
async def cmd_add(ctx, user: str = '', mpaArg: str = 'none'):
    await mpaControl.addUser(ctx, user, mpaArg)
    # global appended
    # if ctx.author.top_role.permissions.manage_emojis or ctx.author.id == OtherIDDict or ctx.guild.id == serverIDDict['RappyCasino'] or ctx.author.top_role.permissions.administrator:
    #     classRole = ''
    #     if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
    #         if ctx.channel.id in EQTest:
    #             if user == "":
    #                 await generateList(ctx.message, "```fix\nYou can't add nobody. Are you drunk?```")
    #                 appended = True
    #             else:
    #                 if mpaArg != 'none':
    #                     if len(mpaArg) > 2:
    #                         if len(mpaArg) == 4:
    #                             classSplit = re.findall('..', mpaArg)
    #                             for item in classSplit:
    #                                 print(item)
    #                             mpaClass1 = classMatch.findClass(classSplit[0])
    #                             mpaClass2 = classMatch.findClass(classSplit[1])
    #                             if mpaClass1 == mpaClass2:
    #                                 mpaClass2 = classMatch.findClass('NoClass')
    #                             if classSplit[0] not in heroClasses and classSplit[1] in subbableHeroClasses or mpaClass2 == BlankMpaClass:
    #                                 classRole = classes[mpaClass1] + classes[mpaClass2]
    #                             elif classSplit[0] in heroClasses or classSplit[1] in heroClasses or mpaClass2 == BlankMpaClass:
    #                                 classRole = classes[mpaClass1]
    #                             else:
    #                                 classRole = classes[mpaClass1] + classes[mpaClass2]

    #                         elif len(mpaArg) > 1:
    #                             classSplit = re.findall('..', mpaArg)
    #                             for item in classSplit:
    #                                 print(item)
    #                             mpaClass1 = classMatch.findClass(classSplit[0])
    #                             classRole = classes[mpaClass1]
    #                             print(classRole)
    #                     else:
    #                         mpaClass = classMatch.findClass(mpaArg)
    #                         classRole = classes[mpaClass]
    #                 else:
    #                     # As all servers share the same icons, there should always be a "class" added to each string. If there is no class, just use the no class icon.
    #                     mpaClass = classMatch.findClass('NoClass')
    #                     classRole = classes[mpaClass]
    #                 #    roleAdded[ctx.channel.id] = True
    #                 if mpaArg == 'reserve' or 'reserve' in ctx.message.content:
    #                     if not user in EQTest[ctx.channel.id]: 
    #                         await generateList(ctx.message, "```fix\nReserve list requested. Adding...```")
    #                         if not user in SubDict[ctx.channel.id]:
    #                             SubDict[ctx.channel.id].append(user)
    #                             await generateList(ctx.message, f'```diff\n+ Added {user} to the Reserve list```')
    #                         else:
    #                             await generateList(ctx.message, "```diff\n+ That user is already in the Reserve List```")
    #                     else:
    #                         await generateList(ctx.message, "```fix\nThat user is already in the MPA```")
    #                     return
    #                 if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
    #                     expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
    #                 for word in EQTest[ctx.channel.id]:
    #                     if isinstance(word, PlaceHolder):
    #                         if not user in EQTest[ctx.channel.id]:
    #                             if isinstance(EQTest[ctx.channel.id][0], PlaceHolder):
    #                                 EQTest[ctx.channel.id].pop(0)
    #                                 EQTest[ctx.channel.id].insert(0, classRole + '|' + user)
    #                                 participantCount[ctx.channel.id] += 1
    #                                 await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                 appended = True
    #                                 break
    #                             elif isinstance(EQTest[ctx.channel.id][1], PlaceHolder):
    #                                 EQTest[ctx.channel.id].pop(1)
    #                                 EQTest[ctx.channel.id].insert(1, classRole + '|' + user)
    #                                 participantCount[ctx.channel.id] += 1
    #                                 await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                 appended = True
    #                                 break
    #                             elif isinstance(EQTest[ctx.channel.id][2], PlaceHolder):
    #                                 EQTest[ctx.channel.id].pop(2)
    #                                 EQTest[ctx.channel.id].insert(2, classRole + '|' + user)
    #                                 participantCount[ctx.channel.id] += 1
    #                                 await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                 appended = True
    #                                 break
    #                             elif isinstance(EQTest[ctx.channel.id][3], PlaceHolder):
    #                                 EQTest[ctx.channel.id].pop(3)
    #                                 EQTest[ctx.channel.id].insert(3, classRole + '|' + user)
    #                                 participantCount[ctx.channel.id] += 1
    #                                 await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                 appended = True
    #                                 break
    #                             elif isinstance(EQTest[ctx.channel.id][4], PlaceHolder):
    #                                 EQTest[ctx.channel.id].pop(4)
    #                                 EQTest[ctx.channel.id].insert(4, classRole + '|' + user)
    #                                 participantCount[ctx.channel.id] += 1
    #                                 await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                 appended = True
    #                                 break
    #                             elif isinstance(EQTest[ctx.channel.id][5], PlaceHolder):
    #                                 EQTest[ctx.channel.id].pop(5)
    #                                 EQTest[ctx.channel.id].insert(5, classRole + '|' + user)
    #                                 participantCount[ctx.channel.id] += 1
    #                                 await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                 appended = True
    #                                 break
    #                             elif isinstance(EQTest[ctx.channel.id][6], PlaceHolder):
    #                                 EQTest[ctx.channel.id].pop(6)
    #                                 EQTest[ctx.channel.id].insert(6, classRole + '|' + user)
    #                                 participantCount[ctx.channel.id] += 1
    #                                 await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                 appended = True
    #                                 break
    #                             elif isinstance(EQTest[ctx.channel.id][7], PlaceHolder):
    #                                 EQTest[ctx.channel.id].pop(7)
    #                                 EQTest[ctx.channel.id].insert(7, classRole + '|' + user)
    #                                 participantCount[ctx.channel.id] += 1
    #                                 await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                 appended = True
    #                                 break
    #                             if eightMan[ctx.channel.id] == False:    
    #                                 if isinstance(EQTest[ctx.channel.id][8], PlaceHolder):
    #                                     EQTest[ctx.channel.id].pop(8)
    #                                     EQTest[ctx.channel.id].insert(8, classRole + '|' + user)
    #                                     participantCount[ctx.channel.id] += 1
    #                                     await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                     appended = True
    #                                     break
    #                                 elif isinstance(EQTest[ctx.channel.id][9], PlaceHolder):
    #                                     EQTest[ctx.channel.id].pop(9)
    #                                     EQTest[ctx.channel.id].insert(9, classRole + '|' + user)
    #                                     participantCount[ctx.channel.id] += 1
    #                                     await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                     appended = True
    #                                     break
    #                                 elif isinstance(EQTest[ctx.channel.id][10], PlaceHolder):
    #                                     EQTest[ctx.channel.id].pop(10)
    #                                     EQTest[ctx.channel.id].insert(10, classRole + '|' + user)
    #                                     participantCount[ctx.channel.id] += 1
    #                                     await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                     appended = True
    #                                     break
    #                                 elif isinstance(EQTest[ctx.channel.id][11], PlaceHolder):
    #                                     EQTest[ctx.channel.id].pop(11)
    #                                     EQTest[ctx.channel.id].insert(11, classRole + '|' + user)
    #                                     participantCount[ctx.channel.id] += 1
    #                                     await generateList(ctx.message, f'```diff\n+ Added {user} to the MPA list```')
    #                                     appended = True
    #                                     break
    #             if not appended:
    #                 await generateList(ctx.message, "```css\nThe MPA is full. Adding to reserve list.```")
    #                 SubDict[ctx.channel.id].append(user)
    #                 await generateList(ctx.message, f'```diff\n+ Added {user} to the Reserve list```')
    #         else:
    #             await ctx.send('There is no MPA.')
    #         await ctx.message.delete()
    #     else:
    #         await ctx.send('This command can only be used in a MPA channel!')
    # else:
    #     await ctx.send("You don't have permissions to use this command")
    # appended = False

# Removes the caller from the MPA.
@client.command(name='removeme')
async def cmd_removeme(ctx):
    await mpaControl.removeme(ctx)
    return
    # global BlankMpaClass
    # inMPA = False
    # if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
    #     if ctx.channel.id in EQTest:
    #         if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
    #             expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
    #         await ctx.message.delete()
    #         for index, item in enumerate(EQTest[ctx.channel.id]):
    #             if (type(EQTest[ctx.channel.id][index]) is PlaceHolder):
    #                 pass
    #             elif ctx.author.name in item:
    #                 EQTest[ctx.channel.id].pop(index)
    #                 EQTest[ctx.channel.id].insert(index, PlaceHolder(''))
    #                 participantCount[ctx.channel.id] -= 1
    #                # playerRemoved[ctx.channel.id] = True
    #                 await generateList(ctx, f'```diff\n- Removed {ctx.author.name} from the MPA list```')
    #                 if len(SubDict[ctx.channel.id]) > 0:
    #                     classRole = classes[BlankMpaClass]
    #                     EQTest[ctx.channel.id][index] = classRole + '|' + SubDict[ctx.channel.id].pop(0)
    #                     participantCount[ctx.channel.id] += 1
    #                     await generateList(ctx, f'```diff\n- Removed {ctx.author.name} from the MPA list and added {EQTest[ctx.channel.id][index]}```')
    #                 inMPA = True
    #                 return
    #         if inMPA == False:
    #             for index, item in enumerate(SubDict[ctx.channel.id]):
    #                 if ctx.author.name in item:
    #                     SubDict[ctx.channel.id].pop(index)
    #                     await generateList(ctx, f'```diff\n- Removed {ctx.author.name} from the Reserve list```')
    #                     return
    #                 else:
    #                     await generateList(ctx, '```fix\nYou were not in the MPA list in the first place.```')
    #             if len(SubDict[ctx.channel.id]) == 0:
    #                 await generateList(ctx, '```fix\nYou were not in the MPA list in the first place.```')

# Manager command to remove a user from the MPA.
@client.command(name='remove')
async def cmd_remove(ctx, user):
    if ctx.author.top_role.permissions.manage_emojis or ctx.author.top_role.permissions.administrator:
        await mpaControl.removeUser(ctx, user)
        return
    else:
        await ctx.send('You do not have permissions to use this command.')
    # global BlankMpaClass
    # if ctx.author.top_role.permissions.manage_emojis or ctx.author.id == OtherIDDict or ctx.guild.id == serverIDDict['RappyCasino'] or ctx.author.top_role.permissions.administrator:
    #     if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
    #         if ctx.channel.id in EQTest:
    #             if len(EQTest[ctx.channel.id]):
    #                     for index in range(len(EQTest[ctx.channel.id])):
    #                         appended = False
    #                         if (type(EQTest[ctx.channel.id][index]) is PlaceHolder):
    #                             pass
    #                         elif user.lower() in EQTest[ctx.channel.id][index].lower():
    #                             toBeRemoved = EQTest[ctx.channel.id][index]
    #                             EQTest[ctx.channel.id][index] = user
    #                             EQTest[ctx.channel.id].remove(user)
    #                             EQTest[ctx.channel.id].insert(index, PlaceHolder(''))
    #                             user = user
    #                             participantCount[ctx.channel.id] -= 1
    #                             #playerRemoved[ctx.channel.id] = True
    #                             toBeRemovedName = toBeRemoved.split('|')
    #                             toBeRemovedName2 = toBeRemovedName[1]
    #                             await generateList(ctx, f'```diff\n- Removed {toBeRemovedName2} from the MPA list```')
    #                             if len(SubDict[ctx.channel.id]) > 0:
    #                                 classRole = classes[BlankMpaClass]
    #                                 EQTest[ctx.channel.id][index] = classRole + '|' + SubDict[ctx.channel.id].pop(0)
    #                                 tobenamed = EQTest[ctx.channel.id][index].split()
    #                                 toBeNamed2 = tobenamed[1]
    #                                 participantCount[ctx.channel.id] += 1
    #                                 await generateList(ctx, f'```diff\n- Removed {toBeRemoved} from the MPA list and added {toBeNamed2}```')
    #                             appended = True
    #                             break
    #                     if not appended:
    #                         for index in range(len(SubDict[ctx.channel.id])):
    #                             appended = False
    #                             if user in SubDict[ctx.channel.id][index]:
    #                                 toBeRemoved = SubDict[ctx.channel.id][index]
    #                                 SubDict[ctx.channel.id][index] = user
    #                                 SubDict[ctx.channel.id].remove(user)
    #                                 user = user
    #                              #   playerRemoved[ctx.channel.id] = True
    #                                 await generateList(ctx, f'```diff\n- Removed {toBeRemoved} from the Reserve list```')
    #                                 appended = True
    #                                 break
    #                     if not appended:    
    #                         await generateList(ctx, f"```fix\nPlayer {user} does not exist in the MPA list```")
    #             else:
    #                 await ctx.send("There are no players in the MPA.")
    #         else:
    #             await ctx.send('There is no MPA.')
    #         if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
    #             expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
    #         await ctx.message.delete()
    #     else:
    #         await ctx.send('This command can only be used in a MPA Channel!')
    # else:
    #     await generateList(ctx, "You don't have permissions to use this command")

# Changes the class of the caller to another one they specify. Or none if they call for none of the classes.
@client.command(name='changeclass')
async def cmd_changeclass(ctx, mpaArg: str = 'none'):
    inMPA = False
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)] or ctx.author.top_role.permissions.administrator:
        if ctx.channel.id in EQTest:
            if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
                expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
            await ctx.message.delete()
            if len(mpaArg) > 2:
                if len(mpaArg) == 4 and mpaArg != 'none':
                    classSplit = re.findall('..', mpaArg)
                    for item in classSplit:
                        print(item)
                    mpaClass1 = classMatch.findClass(classSplit[0])
                    mpaClass2 = classMatch.findClass(classSplit[1])
                    print (mpaClass2)
                    print (BlankMpaClass)
                    newRoleName = classMatch.findClassName(mpaClass1)
                    if mpaClass1 == mpaClass2:
                        mpaClass2 = classMatch.findClass('NoClass')
                    if classSplit[0] not in heroClasses and classSplit[1] in subbableHeroClasses or str(mpaClass2) == str(BlankMpaClass):
                        newRole = classes[mpaClass1] + classes[mpaClass2]
                    elif classSplit[0] in heroClasses or classSplit[1] in heroClasses or str(mpaClass2) == str(BlankMpaClass):
                        newRole = classes[mpaClass1]
                    else:
                        newRole = classes[mpaClass1] + classes[mpaClass2]
                        newRoleName += f'/{classMatch.findClassName(mpaClass2)}'

                elif len(mpaArg) > 1:
                    classSplit = re.findall('..', mpaArg)
                    for item in classSplit:
                        print(item)
                    mpaClass1 = classMatch.findClass(classSplit[0])
                    newRole = classes[mpaClass1]
                    newRoleName = classMatch.findClassName(mpaClass1)
                    print(newRole)
            else:
                mpaClass = classMatch.findClass(mpaArg)
                newRole = classes[mpaClass]
                newRoleName = classMatch.findClassName(mpaClass)
            for index, item in enumerate(EQTest[ctx.channel.id]):
                if (type(EQTest[ctx.channel.id][index]) is PlaceHolder):
                    pass
                elif ctx.author.name in item:
                    EQTest[ctx.channel.id].pop(index)
                    EQTest[ctx.channel.id].insert(index, newRole + '|' + ctx.author.name)
                    await generateList(ctx, f'```diff\n+ Changed {ctx.author.name}\'s class to ' + newRoleName + '```')
                    inMPA = True
                    return
            if inMPA == False:
                await generateList(ctx, '```fix\nYou are not in the MPA!```')

# Private messages the caller information. Special instructions are added if calling from a certain server.
@client.command(name='help')
async def cmd_help(ctx):
    if ctx.guild.id == serverIDDict["Ishana"] or ctx.guild.id == serverIDDict['SupportServer']:
        await tonkHelper.tonk_help("ishanahelp", ctx.message)
    else:
        await tonkHelper.tonk_help("standardhelp", ctx.message)
        return

# Private messages the caller information to help them get started with using this bot.
@client.command(name='gettingstarted')
async def cmd_gettingstarted(ctx):
    await tonkHelper.tonk_help('gettingstarted', ctx.message)
    return

# Test if the bot works or not.
@client.command(name='test')
async def cmd_test(ctx):
    await ctx.channel.send(f'At this point, you should just give up me, {ctx.author.mention}.')  

# Enables the MPA channel so that the MPA commands can be used.
# By default, Admins need to run this command so not every channel can have MPA commands be run on it.
@client.command(name='enablempachannel')
async def cmd_enablempachannel(ctx):
    serverOnBoarded = ''
    if ctx.author.top_role.permissions.administrator:
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
            serverOnBoarded = 'done'
        # This error indicates that this server is not in the database at all.
        except IndexError:
            if len(dbQuery['Items']) < 1:
                print (f'{ctx.guild.id} is not in the database at all. Adding...')
                tonkDB.addMpaChannel(ctx.guild.id, ctx.channel.id, str(datetime.utcnow()))
                serverOnBoarded = 'done'
        print (f'{ctx.author.name} ({ctx.author.id}) has added {ctx.channel.id} to the MPA channels for {ctx.guild.id}.')
        await ctx.send(f'Added channel {ctx.channel.mention} as an MPA channel.')
        # Check to see if addMpaChannel was called, if it was that means we do not need to run the second batch of read/write ops and stop here.
        if serverOnBoarded == 'done':
            return
        # # Add a blank expiration config to the json file
        # try:
        #     dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        #     if (str(ctx.channel.id)) in (dbQuery['Items'][0]['mpaAutoExpirationChannels']):
        #         pass
        #     else:
        #         print (f'Adding {ctx.channel.id} to the MPA auto expiration config for {ctx.guild.id}')
        #         tonkDB.updateMpaAutoExpirationChannels(ctx.guild.id, ctx.channel.id, dbQuery)
        # except KeyError:
        #     print (f'{ctx.guild.id} is not in the mpa auto-expiration dictionary. Adding...')
        #     tonkDB.updateMpaAutoExpirationChannels(ctx.guild.id, ctx.channel.id, dbQuery)
        
    else:
        await ctx.send('You do not have permissions to do this.')
        return

# Disables the MPA functions on the channel the command is called in. Removes the channel data from all the related json files.
@client.command(name='disablempachannel')
async def cmd_disablempachannel(ctx):
    if ctx.author.top_role.permissions.administrator:
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        try:
            if (str(ctx.channel.id)) in (dbQuery['Items'][0]['mpaChannels']):
                print (dbQuery['Items'][0]['mpaChannels'])
                for index, item in enumerate(dbQuery['Items'][0]['mpaChannels']):
                    if str(ctx.channel.id) == str(item):
                        tonkDB.removeMpaChannel(ctx.guild.id, index, str(datetime.utcnow()))
                        await ctx.send(f'Removed channel {ctx.channel.mention} from the MPA channels list.')
                        break
        except Exception as e:
            await ctx.send('Error removing the channel from the list.')
            traceback.print_exc(file=sys.stdout)
            return
    return


# This sets the value for the "Meeting in" section of the MPA list.
@client.command(name='setmpablock')
async def cmd_setmpablock(ctx, blockNumber):
    if ctx.author.top_role.permissions.administrator:
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

        # try: 
        #     if mpaBlockNumber == mpaBlockConfigDict[str(ctx.guild.id)]:
        #         await ctx.send(f'This server is already set for block {mpaBlockNumber}!')
        #         return
        #     elif blockNumber.lower() == 'clear' and mpaBlockNumber == 99999999999999999999999999999999:
        #         del mpaBlockConfigDict[str(ctx.guild.id)]
        #         await ctx.send('Successfully removed the block from the MPA configuration.')
        #     else:
        #         mpaBlockConfigDict[str(ctx.guild.id)] = mpaBlockNumber
        # except KeyError:
        #     print (f'{ctx.guild.id} is not in the dictionary. Adding that in..')
        #     if blockNumber.lower() == 'clear':
        #         await ctx.send("You can't just clear nothing, are you drunk?")
        #         return
        #     else:
        #         mpaBlockConfigDict[str(ctx.guild.id)] = mpaBlockNumber
        # try:
        #     dumpMpaBlockConfig(mpaBlockConfigDict)
        #     if blockNumber.lower() != 'clear':
        #         print (f"{ctx.author.name} has set {ctx.guild.name}'s block number to {mpaBlockNumber}.")
        #         await ctx.send(f'Set the server block to {mpaBlockNumber}')
        #     return
        # except Exception as e:
        #     print (e)
        #     await ctx.send('Something went wrong! AAAAA')
        #     return


# # Enables automatic MPA deletion after a certain period of inactivity that was configured at the top of this file.
# @client.command(name='enablempaexpiration')
# async def cmd_enablempaexpiration(ctx):
#     if ctx.author.top_role.permissions.administrator:
#         try:
#             if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
#                 await ctx.send('This channel already has auto expiration enabled!')
#                 return
#             else:
#                 mpaExpirationConfig[str(ctx.guild.id)].append(ctx.channel.id)
#         except KeyError:
#             print (f'{ctx.guild.id} is not in the mpa auto-expiration dictionary. Adding...')
#             mpaExpirationConfig[str(ctx.guild.id)] = []
#             mpaExpirationConfig[str(ctx.guild.id)].append(ctx.channel.id)
#         try:
#             dumpMpaAutoExpiration(mpaExpirationConfig)
#             print (f'{ctx.author.name} has enabled auto-expiration for {ctx.channel.id} from the server {ctx.guild.id}')
#             await ctx.channel.send(f'Enabled MPA auto expiration for {ctx.channel.mention}')
#         except Exception as e:
#             await ctx.send('Error enabling the channel.')
#             print (e)
#         return

# # Disables automatic MPA deletion in the channel this comamnd was called in.
# # Note that this automatically runs if the disablempachannel was called.
# @client.command(name='disablempaexpiration')
# async def cmd_disablempaexpiration(ctx):
#     if ctx.author.top_role.permissions.administrator:
#         if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
#             try:
#                 for index, item in enumerate(mpaExpirationConfig[str(ctx.guild.id)]):
#                     if ctx.channel.id == item:
#                         mpaExpirationConfig[str(ctx.guild.id)].pop(index)
#                         try:
#                             dumpMpaAutoExpiration(mpaExpirationConfig)
#                             channel = client.get_channel(item)
#                             await ctx.send(f'Disabled auto expiration for {ctx.channel.mention}')
#                             return
#                         except Exception as e:
#                             await ctx.send('Error removing the channel from the list.')
#                             print (e)
#             except Exception as e:
#                 await ctx.send('Error removing the channel.')
#                 print (e)
#         else:
#             await ctx.send("The channel was not found! It may have already been disabled or wasn''t enabled in the first place!")
#             return

# Debugging command
# @client.command(name='eval')
# async def cmd_eval(ctx, *code):
#     if ctx.author.id == OtherIDDict['Tenj']:
#         try:
#             result = eval(code)
#         except Exception:
#             formatted_lines = traceback.format_exc().splitlines()
#             await ctx.send('Failed to Evaluate.\n```py\n{}\n{}\n```'.format(formatted_lines[-1], '/n'.join(formatted_lines[4:-1])))
#             return

#         if asyncio.iscoroutine(result):
#             result = await result

#         if result:
#             await ctx.send('Evaluated Successfully.\n```{}```'.format(result))
#             return
#     else:
#         await ctx.send('No.')

# Opens the MPA to non-approved roles. Only usable in certain servers.
@client.command(name='openmpa')
async def cmd_openmpa(ctx):
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
        if ctx.author.top_role.permissions.manage_emojis or ctx.author.id == OtherIDDict or ctx.author.top_role.permissions.administrator:
            if guestEnabled[ctx.channel.id] == True:
                await ctx.send('This MPA is already open!')
            else:
                guestEnabled[ctx.channel.id] = True
                for index in range(len(ctx.guild.roles)):
                    if ctx.guild.id == serverIDDict['Okra']:
                        if (ctx.guild.roles[index].id == 224757670823985152):
                            await ctx.send(f'{ctx.guild.roles[index].mention} can now join in the MPA!')
                            await generateList(ctx, '```fix\nMPA is now open to non-members.```')
                    elif ctx.guild.id == serverIDDict['Ishana']:
                        if (ctx.guild.roles[index].id == 561910935107665949):
                            print ('Reached here')
                            await ctx.send(f'{ctx.guild.roles[index].mention} can now join in the MPA!')
                            await generateList(ctx, '```fix\nMPA is now open to non-members.```')
                    else:
                        await ctx.send('Opened MPA to non-members!')
                        await generateList(ctx, '```fix\nMPA is now open to non-members.```')
                        break
# Closes the MPA to only approved roles. Only usable in certain servers.
@client.command(name='closempa')
async def cmd_closempa(ctx):
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
        if ctx.author.top_role.permissions.manage_emojis or ctx.author.id == OtherIDDict or ctx.author.top_role.permissions.administrator:
            if guestEnabled[ctx.channel.id] == False:
                await ctx.send('This MPA is already closed!')
            else:
                guestEnabled[ctx.channel.id] = False
                await ctx.send('Closed MPA to Members only.')
                await generateList(ctx, '```fix\nMPA is now closed to non-members```')
        else:
            await ctx.send('You do not have the permission to do this.')

# Schedules an MPA for to be made at a later time. This converts a time in hours/minutes/seconds and converts it into seconds, which will then put it in a dictionary
# and a function that runs every second will check to see if it's time to start an MPA with the arguements provided in this command.
@client.command(name='schedulempa')
async def cmd_schedulempa(ctx, requestedTime, message: str = '', mpaType: str = 'default'):
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
        if ctx.author.top_role.permissions.manage_emojis or ctx.author.top_role.permissions.administrator or ctx.author.id == OtherIDDict['Tenj']:
            scheduledTime = 0
            timesplit = re.findall(r'[A-Za-z]+|\d+', requestedTime)
            message = f'"{message}"'
            try:
                timeNumber = int(timesplit[0])
            except ValueError:
                await ctx.send('Please provide a number for the time!')
                return
            if len(timesplit) != 2:
                print (len(timesplit))
                await ctx.send('Wrong timeformat stated! Please state your time in <number>h/m/s (Example: 12h)')
                return
            if 'h' in timesplit[1].lower():
                timestat = 'hour'
                scheduledTime = int(time.mktime(datetime.now().timetuple())) + (timeNumber * 3600)
            elif 'm' in timesplit[1].lower():
                timestat = 'minute(s)'
                scheduledTime = int(time.mktime(datetime.now().timetuple())) + (timeNumber * 60)
            elif 's' in timesplit[1].lower():
                timestat = 'second(s)'
                scheduledTime = int(time.mktime(datetime.now().timetuple())) + (timeNumber)
            else:
                await ctx.send('Invalid formatted stated!')
                return
            try:
                mpaScheduleDict[ctx.channel.id]['scheduledTime'] = scheduledTime
                mpaScheduleDict[ctx.channel.id]['arguments'] = f'{message} {mpaType}'
            except KeyError:
                mpaScheduleDict[ctx.channel.id] = {}
                mpaScheduleDict[ctx.channel.id]['scheduledTime'] = scheduledTime
                mpaScheduleDict[ctx.channel.id]['arguments'] = f'{message} {mpaType}'
            try:
                dumpScheduledMpa(mpaScheduleDict)
                await ctx.send(f'Scheduled an MPA `{timeNumber} {timestat}` from now')
                return
            except Exception as e:
                await ctx.send('Error scheduling the MPA. Please see error in console')
                print (e)
                return
    else:
        await ctx.send('This is not an MPA channel! See `!help` for more information')
        return

# Finishing bootup, prints uptime/status information to my control panel server/channel.
print ('Logging into Discord...\n')
@client.event
async def on_ready():
    FreshStart = False
    connectedServers = 0
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print ('Logged in to servers:')
    for item in client.guilds:
        print (item)
        connectedServers += 1
    end = time.time()
    loadupTime = (end - start)
    if loadupTime < 20:
        FreshStart = True
    reconnectRole = discord.utils.get(client.get_guild(226835458552758275).roles, id=503296384070320149)
    print ('Tonk-Dev is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)))
    print('------')
    game = discord.Game(name='just tonk things')
    await client.change_presence(activity=game, status=discord.Status.online)
    onlineRole = discord.utils.get(client.get_guild(226835458552758275).roles, id=370337403769978880)
    if FreshStart == True:
        await client.get_channel(322466466479734784).send(f'Tonk-Dev is now {onlineRole.mention}' + '\nStartup time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nConnected to **' + str(connectedServers) + '** servers' + '\nLast Restarted: ' + lastRestart)
    else:
        await client.get_channel(322466466479734784).send(f'Tonk has {reconnectRole.mention}')
    while True:
        await expiration_checker()
        await mpa_schedulerclock()
        await asyncio.sleep(1)

# Global command handler
#@client.event
#async def on_command_error(ctx, error):
#    print (error)
    #print ('...but that command was not found.')
#    return

# Behavior every time this bot joins another server. Tries to send a message to the general channel as well as logging the join event to the control panel server.
@client.event
async def on_server_join(server):
    await client.get_channel(OtherIDDict['ControlPanel']).send(f'```diff\n+ Joined {server.name} ```' + f'(ID: {str(server.id)})')
    general = find(lambda x: x.name == 'general',  server.channels)
    if general and general.permissions_for(server.me).send_messages:
        await general.send('**Greetings!**\nI am Tonk, a MPA organization bot for PSO2! Please type **!gettingstarted** to set my functions up!')

# Logs the leave event on the control panel server.
@client.event
async def on_server_remove(server):
    await client.get_channel(OtherIDDict['ControlPanel']).send(f'```diff\n- Left {server.name} ```'.format(server.name) + f'(ID: {str(server.id)})')
    

@client.event
async def on_resumed():
    connectedServers = 0
    print ('Tonk has resumed from a disconnect.')
    for item in client.guilds:
        connectedServers += 1
    resumeRole = discord.utils.get(client.get_guild(serverIDDict['Bloop']).roles, id=405620919541694464)
    await client.get_channel(OtherIDDict['ControlPanel']).send(f'Tonk has {resumeRole.mention}' + '\nConnected to **' + str(connectedServers) + '** servers')
# WOOHOO    
client.run(APIKey)
