## TEST VERSION
## DO NOT USE IN PRODUCTION! DUH!

import discord
import asyncio
import aiohttp
import traceback
import sys
import os
import re
import datetime
import shlex
import json
import time
from datetime import datetime,tzinfo,timedelta
from random import randint
from discord.utils import find
from discord.ext import commands
from assetsTonk import MpaMatchDev
from assetsTonk import classMatch
from assetsTonk import tonkHelper

from tendo import singleton

# Only allows one instance of the bot running.
#me = singleton.SingleInstance()


class FakeMember():
    def __init__(self, name):
        self.name = name
 
class PlaceHolder():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name)
        
# All these batches of lines here declare the constants and dictionaries to be used.       
print ('Beginning bot startup process...\n')
start = time.time()
EQTest = {}
SubDict = {}
guestEnabled = {}
EQPostDict = {}
MPACount = 0
mpaRemoved = {}
participantCount = {}
eightMan = {}
roleAdded = {}
color = {}
playerRemoved = {}
totalPeople = {}
expirationDate = {}
appended = False
#client = discord.Client()
commandPrefix = '!'
client = commands.Bot(command_prefix=commandPrefix)
# Remove the default help command
client.remove_command('help')
lastRestart = str(datetime.now())
ActiveMPA = list()
mpaExpirationCounter = 5400
mpaWarningCounter = 15
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


# Imports Json data for mpaChannels on startup
mpachannelsJsonFile = open('mpaChannels.json')
mpachannelsJsonFileRead = mpachannelsJsonFile.read()
mpaChannels = json.loads(mpachannelsJsonFileRead)

mpaExpirationJsonFile = open('assetsTonk/mpaAutoExpiration.json')
mpaExpirationJsonFileRead = mpaExpirationJsonFile.read()
mpaExpirationConfig = json.loads(mpaExpirationJsonFileRead)

scheduledMpaFile = open('assetsTonk/scheduledMpa.json')
scheduledMpaFileRead = scheduledMpaFile.read()
mpaScheduleDict = json.loads(scheduledMpaFileRead)

def is_bot(m):
	return m.author == client.user
    
def is_not_bot(m):
    return m.author != client.user
def is_pinned(m):
    return m.pinned != True

def findRoleID(roleName, message):
    result = discord.utils.find(lambda m: m.name == roleName, message.guild.roles)
    if result is not None:
        return str(result.id)
    else:
        return 0
def loadmpaChannels():
    mpachannelsJsonFile = open('mpaChannels.json')
    mpachannelsJsonFileRead = mpachannelsJsonFile.read()
    mpaChannels = json.loads(mpachannelsJsonFileRead)
    return
def loadmpaAutoExpiration():
    mpaExpirationJsonFile = open('assetsTonk/mpaAutoExpiration.json')
    mpaExpirationJsonFileRead = mpaExpirationJsonFile.read()
    mpaExpirationConfig = json.loads(mpaExpirationJsonFileRead)
    return

def loadscheduledMpa():
    scheduledMpaFile = open('assetsTonk/scheduledMpa.json')
    scheduledMpaFileRead = scheduledMpaFile.read()
    mpaScheduleDict = json.loads(scheduledMpaFileRead)

KeyFile = open('assetsTonk/TonkTestConfig.json')
KeyRead = KeyFile.read()
KeyDict = json.loads(KeyRead)
Key = KeyDict['APIKEY']

print ('Loading classes list...\n')  
  
with open(os.path.join('assetsTonk',"classes.txt"),'r') as e:
    classesread = e.readlines()
    classes = []
    for i in classesread:
        classes.append(i.strip())
        
print ('Classes loaded.\n')  

getTime = datetime.now()

with open(os.path.join('assetsTonk',"activeServerSlots.txt"),'r') as e:
    assRead = e.readlines()
    activeServerIcons = []
    for i in assRead:
        activeServerIcons.append(i.strip())
        
with open(os.path.join("assetsTonk","grayServerSlots.txt"),'r') as e:
    iassRead = e.readlines()
    inactiveServerIcons = []
    for i in iassRead:
        inactiveServerIcons.append(i.strip())


# Background task that runs every second to check if there's any MPA that will be expiring soon.
async def expiration_checker():
    global mpaWarningCounter
    for key in expirationDate:
        nowTime = int(time.mktime(datetime.now().timetuple()))
        if (expirationDate[key] - 15) == nowTime and mpaRemoved[key] == False:
            await client.get_channel(key).send(f":warning: **Inactivity Detected! This MPA will be automatically closed in `{mpaWarningCounter}` seconds if no actions are taken!** :warning:")
        if expirationDate[key] == nowTime and mpaRemoved[key] == False:
            print ("Expiration reached")
            await client.get_channel(key).send("!removempa")
# Background task that ticks every second and will start an mpa if the scheduled time comes
async def mpa_schedulerclock():
    for key in mpaScheduleDict:
        alreadyHasMPA = False
        nowTime = int(time.mktime(datetime.now().timetuple()))
        print (nowTime)
        try:
            if EQTest[key] is not None:
                alreadyHasMPA = True
        except KeyError:
            pass
        if mpaScheduleDict[key]['scheduledTime'] <= nowTime and alreadyHasMPA == False:
            print (key)
            await client.get_channel(key).send(f"!startmpa {mpaScheduleDict[key]['arguments']}")
            del mpaScheduleDict[key]
            try:
                with open('assetsTonk/scheduledMpa.json', 'w') as fp:
                    json.dump(mpaScheduleDict, fp)
                    fp.close()
                return
            except Exception as e:
                print ('An error occurred while trying to automatically dump the mpaschedule dict to JSON')
                print (e)
                return
        elif alreadyHasMPA == True:
            await client.get_channel(key).send('You know there was supposed to be an MPA scheduled for now but there is already an MPA here! Ignoring the scheduled MPA..')
            del mpaScheduleDict[key]
            try:
                with open('assetsTonk/scheduledMpa.json', 'w') as fp:
                    json.dump(mpaScheduleDict, fp)
                    fp.close()
                return
            except Exception as e:
                print ('An error occurred while trying to automatically dump the mpaschedule dict to JSON')
                print (e)
                return


async def generateList(message, inputstring):
    global MPACount
    global inactiveServerIcons
    global activeServerIcons
    global classes
    global OtherIDDict
    global serverIDDict
    global ChannelIDDict
    sCount = 1
    mpaFriendly = ''
    classlist = '\n'
    playerlist = '\n'
    splitstr = ''
    # Servers with a class.
    for word in EQTest[message.channel.id]:
        if (type(word) is PlaceHolder):
            if message.guild.id == serverIDDict['Ishana']:
                color[message.channel.id] = 0x0196ef
                playerlist += (inactiveServerIcons[0] + '\n')
                classlist += (classes[10] + '\n') 
            else:
                color[message.channel.id] = 0xcc0000
                playerlist += (inactiveServerIcons[2] + '\n')
                classlist += (classes[10] + '\n')
        else:
            splitstr = word.split()
            classRole = splitstr[0]
            if not classRole.startswith('<'):
                classRole = classes[10]
                if playerRemoved[message.channel.id] == True:
                    player = splitstr[1]
                    playerRemoved[message.channel.id] = False
                else:
                    player = splitstr[0]
                if len(splitstr) > 2:
                    for index in range(len(splitstr)):
                        if index == 0 or index == 1:
                            pass
                        else:
                            player+= splitstr[index] + ' '
            else:
                player = splitstr[1]
                if len(splitstr) > 2:
                    for index in range(len(splitstr)):
                        if index == 0 or index == 1:
                            pass
                        else:
                            player+= splitstr[index] + ' '
            if message.guild.id == serverIDDict['Ishana']:
                playerlist += (activeServerIcons[0] + ' ' + player + '\n')
            else:
                playerlist += (activeServerIcons[2] + ' ' + player + '\n')
            classlist += (classRole + '\n')
    if len(SubDict[message.channel.id]) > 0:
        playerlist += ('\n**Reserve List**:\n')
        for word in SubDict[message.channel.id]:
            playerlist += (str(sCount) + ". " + word + '\n')
            sCount += 1  
            
    if guestEnabled[message.channel.id] == True:
        mpaFriendly = 'Yes'
    else:
        mpaFriendly = 'No'
        
    em = discord.Embed(description='Use `!addme` to sign up \nOptionally you can add your class after addme. Example. `!addme br` \nUse `!removeme` to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.', colour=color[message.channel.id])
    if message.guild.id == serverIDDict['Ishana']:
        em.add_field(name='Meeting at', value='`' + 'Block 03`', inline=True)
    if message.guild.id == serverIDDict['Ishana']:
        em.add_field(name='Party Status', value='`' + str(participantCount[message.channel.id]) + '/' + str(totalPeople[message.channel.id]) + '`', inline=True)
    else:
        em.add_field(name='Party Status', value='`' + str(participantCount[message.channel.id]) + '/' + str(totalPeople[message.channel.id]) + '`', inline=False)
    if message.guild.id == serverIDDict['Ishana']:
        em.add_field(name='MPA Open?', value='`' + mpaFriendly + '`', inline=False)
    if message.guild.id == serverIDDict['Ishana']:
        em.add_field(name='Participant List', value=playerlist, inline=True)
    else:
        em.add_field(name='Participant List', value=playerlist, inline=True)
    em.add_field(name='Class', value=classlist, inline=True)
    em.add_field(name='Last Action', value=inputstring, inline=False)
    em.set_author(name='An MPA is starting!', icon_url=message.guild.icon_url)

    # Test function, attempts to do the thing where we dump json files and stuff.
    # dumpDict = {
    #     "playerlist": playerlist,
    #     "classlist": classlist,
    #     "mpalist": mpaFriendly,
    #     "inputstring": inputstring
    # }
    # with open (f'{message.channel.id}.json', 'w') as fp:
    #     json.dump(dumpDict, fp)
    try:
        await EQPostDict[message.channel.id].edit(embed=em)
    except (KeyError, discord.NotFound):
        print(message.author.name + ' Started an MPA on ' + message.guild.name)
        MPACount += 1
        await client.get_channel(OtherIDDict['ControlPanel']).send('```css\n' + message.author.name + '#' + str(message.author.discriminator) + ' (ID: ' + str(message.author.id) + ') ' + 'Started an MPA on ' + message.guild.name + '\nAmount of Active MPAs: ' + str(MPACount) + '\nTimestamp: ' + str(datetime.now()) + '```')
        print('Amount of Active MPAs: ' + str(MPACount))
        EQPostDict[message.channel.id] = await message.channel.send('', embed=em)
    except Exception as e:
        print (type(e))
        print (e)
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
    global ChannelIDDict
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
        await client.process_commands(message)
# Section to convert the commands to the new format

@client.command(name='gethighestrole')
async def cmd_gethighestrole(ctx):
    if ctx.channel.id not in mpaChannels[str(ctx.guild.id)]:
        await ctx.send(ctx.author.top_role)
@client.command(name='listroles')
async def cmd_listroles(ctx):
    if ctx.channel.id not in mpaChannels[str(ctx.guild.id)]:
        for index in range(len(ctx.author.roles)):
            if len(ctx.author.roles) == 0:
                await ctx.send('You either dont have a role, or w command is bugged.')
            else:
                await ctx.send(ctx.author.roles[index].name + str(index))
@client.command(name='quickclean')
async def cmd_quickclean(ctx, amount):
    if ctx.author.top_role.permissions.manage_channels or ctx.author.id == OtherIDDict['Tenj']:
        try:
            value = int(amount)
        except ValueError:
            await ctx.send('Please provide a number!')
            return
        await ctx.channel.purge(limit=int(amount))
    else:
        await ctx.send('http://i.imgur.com/FnKySHo.png')
    return
@client.command(name='checkmpamanagerperm')
async def cmd_checkmpamanagerperm(ctx):
    if ctx.channel.id not in mpaChannels[str(ctx.guild.id)]:
        doIHavePermission = ctx.author.top_role.permissions.manage_emojis
        if doIHavePermission:
            await ctx.send('You have the permissions to start an MPA.')
        else:
            await ctx.send('You do not have the permission to start an MPA. Take a hike.')
@client.command(name='ffs')
async def cmd_ffs(ctx):
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
        if ctx.author.top_role.permissions.manage_emojis or ctx.author.id == OtherIDDict['Tenj']:
            await ctx.channel.purge(limit=100, after=getTime, check=is_not_bot)
        else:
            await ctx.channel.send('You lack the permissions to use this command.')
    else:
        await ctx.channel.send('This command can only be used in a MPA channel.')

async def function_startmpa(message, broadcast, mpaType):
    if message.channel.id in mpaChannels[str(message.guild.id)]:
        inTesting = False
        if message.guild.id == serverIDDict['Ishana'] or message.guild.id == serverIDDict['SupportServer']:
            mpaMap = MpaMatchDev.get_class(mpaType)
            try:
                if mpaMap == 'default':
                    pass
                else:
                    await message.channel.send(file=discord.File(os.path.join('assetsTonk', mpaMap)))
            except FileNotFoundError:
                await message.channel.send('Unable to find a file with that name! Please check your spelling.')    
                return
        if mpaType == '8man' or mpaType == 'pvp' or mpaType == 'busterquest' or mpaType == 'hachiman':
            eightMan[message.channel.id] = True
        else:
            eightMan[message.channel.id] = False
        if not message.channel.id in EQTest:
            if message.author.top_role.permissions.manage_emojis or message.author.id == OtherIDDict or message.author.top_role.permissions.administrator or message.author == client.user:
                try:
                    if inTesting != True:
                        if message != '' and message != '|':
                            await message.channel.send(f' {broadcast}')
                        else:
                            pass
                    EQTest[message.channel.id] = list()
                    SubDict[message.channel.id] = list()
                    ActiveMPA.append(message.channel.id)
                    roleAdded[message.channel.id] = False
                    guestEnabled[message.channel.id] = False
                    playerRemoved[message.channel.id] = False
                    participantCount[message.channel.id] = 0
                    if message.channel.id in mpaExpirationConfig[str(message.guild.id)]:
                        expirationDate[message.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
                        mpaRemoved[message.channel.id] = False
                        print (expirationDate[message.channel.id])
                    if eightMan[message.channel.id] == True:
                        for index in range(8):
                            EQTest[message.channel.id].append(PlaceHolder(""))
                        totalPeople[message.channel.id] = 8
                    else:
                        for index in range(12):
                            EQTest[message.channel.id].append(PlaceHolder(""))
                        totalPeople[message.channel.id] = 12
                    await generateList(message, '```dsconfig\nStarting MPA. Please use !addme to sign up!```')
                except discord.Forbidden:
                    print (message.author.name + f'Tried to start an MPA at {message.guild.name}, but failed.')
                    await message.author.send('I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                    return

            else:
                await message.channel.send('You do not have the permission to do that, starfox.')
        else:
            await generateList(message, '```fix\nThere is already an MPA being made here!```')
    else:
        await message.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')

@client.command(name='startmpa')
async def cmd_startmpa(ctx, message: str = '', mpaType: str = 'default'):
    inTesting = False
    # This checks if Tonk has the deleting permission. If it doesn't, don't run the script at all and just stop.
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        print (ctx.author.name + f' Tried to start an MPA at {ctx.message.guild.name}, but failed.')
        await ctx.author.send('I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
        return
    await function_startmpa(ctx, message, mpaType)
@client.command(name='help')
async def cmd_help(ctx):
    if ctx.guild.id == serverIDDict["Ishana"] or ctx.guild.id == serverIDDict['SupportServer']:
        await tonkHelper.tonk_help("ishanahelp", ctx.message)
    else:
        await tonkHelper.tonk_help("standardhelp", ctx.message)
        return
@client.command(name='gettingstarted')
async def cmd_gettingstarted(ctx):
    await tonkHelper.tonk_help('gettingstarted', ctx.message)
    return
@client.command(name='test')
async def cmd_test(ctx):
    await ctx.channel.send(f'At this point, you should just give up me, {ctx.author.mention}.')  

@client.command(name='enablempachannel')
async def cmd_enablempachannel(ctx):
    if ctx.author.top_role.permissions.administrator:
        try:
            if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
                await ctx.send('This channel is already an active MPA channel!')
                return
            else:
                mpaChannels[str(ctx.guild.id)].append(ctx.channel.id)
        except KeyError:
            print (f'{ctx.guild.id} is not in the MPA Channels Dictionary. Adding...')
            mpaChannels[str(ctx.guild.id)] = []
            mpaChannels[str(ctx.guild.id)].append(ctx.channel.id)
        try:
            with open('mpaChannels.json', 'w') as fp:
                json.dump(mpaChannels, fp)
            fp.close()
            loadmpaChannels()
            print (f'{ctx.author.name} ({ctx.author.id}) has added {ctx.channel.id} to the MPA channels for {ctx.guild.id}.')
            await ctx.send(f'Added channel {ctx.channel.mention} as an MPA channel.')
        except:
            await ctx.send('Error adding channel.')
        # Add a blank expiration config to the json file
        try:
            if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
                print ('Yay')
        except KeyError:
            print (f'{ctx.guild.id} is not in the mpa auto-expiration dictionary. Adding...')
            mpaExpirationConfig[str(ctx.guild.id)] = []
        try:
            with open("assetsTonk/mpaAutoExpiration.json", 'w') as fp:
                json.dump(mpaExpirationConfig, fp)
                fp.close()
                loadmpaAutoExpiration()
                return
        except Exception as e:
            await ctx.send('An internal error occurred.')
            print (e)
    else:
        await ctx.send('You do not have permissions to do this.')
        return
@client.command(name='disablempachannel')
async def cmd_disablempachannel(ctx):
    if ctx.author.top_role.permissions.administrator:
        if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
            try:
                for index, item in enumerate(mpaChannels[str(ctx.guild.id)]):
                    if ctx.channel.id == item:
                        mpaChannels[str(ctx.guild.id)].pop(index)
                        try:
                            with open('mpaChannels.json', 'w') as fp:
                                json.dump(mpaChannels, fp)
                            fp.close()
                            loadmpaChannels()
                            channel = client.get_channel(item)
                            await ctx.send(f'Removed channel {ctx.channel.mention} from the MPA channels list.')
                            break
                        except Exception as e:
                            await ctx.send('Error removing the channel from the list.')
                            print (e)
            except Exception as e:
                await ctx.send('Error removing the channel.')
                print (e)
    print ('Deactivating the auto expiration...')
    # When the channel is deactivated, also deactivate the auto expiration function for the channel.
    if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
        try:
            for index, item in enumerate(mpaExpirationConfig[str(ctx.guild.id)]):
                if ctx.channel.id == item:
                    mpaExpirationConfig[str(ctx.guild.id)].pop(index)
                    try:
                        with open('assetsTonk/mpaAutoExpiration.json', 'w') as fp:
                            json.dump(mpaExpirationConfig, fp)
                        fp.close()
                        loadmpaAutoExpiration()
                        channel = client.get_channel(item)
                        return
                    except Exception as e:
                        print (e)
        except Exception as e:
            await ctx.send('Error removing the channel.')
            print (e)
    return
@client.command(name='enablempaexpiration')
async def cmd_enablempaexpiration(ctx):
    if ctx.author.top_role.permissions.administrator:
        try:
            if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
                await ctx.send('This channel already has auto expiration enabled!')
                return
            else:
                mpaExpirationConfig[str(ctx.guild.id)].append(ctx.channel.id)
        except KeyError:
            print (f'{ctx.guild.id} is not in the mpa auto-expiration dictionary. Adding...')
            mpaExpirationConfig[str(ctx.guild.id)] = []
            mpaExpirationConfig[str(ctx.guild.id)].append(ctx.channel.id)
        try:
            with open("assetsTonk/mpaAutoExpiration.json", 'w') as fp:
                json.dump(mpaExpirationConfig, fp)
                fp.close()
                loadmpaAutoExpiration()
                print (f'{ctx.author.name} has enabled auto-expiration for {ctx.channel.id} from the server {ctx.guild.id}')
                await ctx.channel.send(f'Enabled MPA auto expiration for {ctx.channel.mention}')
        except Exception as e:
            await ctx.send('Error enabling the channel.')
            print (e)
        return
@client.command(name='disablempaexpiration')
async def cmd_disablempaexpiration(ctx):
    if ctx.author.top_role.permissions.administrator:
        if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
            try:
                for index, item in enumerate(mpaExpirationConfig[str(ctx.guild.id)]):
                    if ctx.channel.id == item:
                        mpaExpirationConfig[str(ctx.guild.id)].pop(index)
                        try:
                            with open('assetsTonk/mpaAutoExpiration.json', 'w') as fp:
                                json.dump(mpaExpirationConfig, fp)
                            fp.close()
                            loadmpaAutoExpiration()
                            channel = client.get_channel(item)
                            await ctx.send(f'Disabled auto expiration for {ctx.channel.mention}')
                            return
                        except Exception as e:
                            await ctx.send('Error removing the channel from the list.')
                            print (e)
            except Exception as e:
                await ctx.send('Error removing the channel.')
                print (e)
        else:
            await ctx.send("The channel was not found! It may have already been disabled or wasn''t enabled in the first place!")
            return
# Adds the user into the EQ list in the EQ channel. Optionally takes a class as an arguement. If one is passed, add the class icon and the user's name into the EQ list.
@client.command(name='addme', aliases=['reserveme'])
async def cmd_addme(ctx, mpaArg: str = 'none'):
    bypassCheck = False
    classRole = ''
    index = 0
    personInMPA = False
    personInReserve = False
    roleAdded[ctx.channel.id] = False
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
        for index in range(len(ctx.author.roles)):
            if ctx.author.roles[index].id == RoleIDDict['IshanaFamilia']:
                bypassCheck = True
                break
            elif ctx.author.id == OtherIDDict['Tenj']:
                bypassCheck = True
                break
            elif ctx.author.top_role.permissions.manage_emojis:
                bypassCheck = True
                break
            elif ctx.guild.id == serverIDDict['Ishana']:
                bypassCheck = False
            else:
                bypassCheck = True
        if (bypassCheck == False and guestEnabled[ctx.channel.id] == False):
            await generateList(ctx, '```fix\nGuests are not allowed to join this MPA.```')
            await ctx.message.delete()
            return
        else:
            if ctx.channel.id in EQTest:
                for index, item in enumerate(EQTest[ctx.channel.id]):
                    if (type(EQTest[ctx.channel.id][index]) is PlaceHolder):
                        pass
                    elif ctx.author.name in item:
                        personInMPA = True
                        break
                for index, item in enumerate(SubDict[ctx.channel.id]):
                    if ctx.author.name in item:
                        personInReserve = True
                        break
                mpaClass = classMatch.findClass(mpaArg)
                classRole += ' ' + classes[mpaClass]
                roleAdded[ctx.channel.id] = True
                if mpaArg == 'reserve' or 'reserveme' in ctx.message.content:
                    if personInMPA == False: 
                        await generateList(ctx, "```fix\nReserve list requested. Adding...```")
                        await ctx.message.delete()
                        if personInReserve == False:
                            SubDict[ctx.channel.id].append(ctx.message.author.name)
                            await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the Reserve list```')
                        else:
                            await generateList(ctx, "```diff\n+ You are already in the Reserve List```")
                    else:
                        await generateList(ctx, "```fix\nYou are already in the MPA```")
                        await ctx.message.delete()
                    return
                if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
                    expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
                    print (expirationDate[ctx.channel.id])
                await ctx.message.delete()
                for word in EQTest[ctx.channel.id]:
                    appended = False
                    if isinstance(word, PlaceHolder):
                        if personInMPA == False:
                            if (ctx.author.name in SubDict[ctx.channel.id]):
                                index = SubDict[ctx.channel.id].index(ctx.author.name)
                                if isinstance(EQTest[ctx.channel.id][0], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(0)
                                    EQTest[ctx.channel.id][0] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][1], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(1)
                                    EQTest[ctx.channel.id][1] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][2], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(2)
                                    EQTest[ctx.channel.id][2] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][3], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(3)
                                    EQTest[ctx.channel.id][3] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][4], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(4)
                                    EQTest[ctx.channel.id][4] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][5], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(5)
                                    EQTest[ctx.channel.id][5] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][6], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(6)
                                    EQTest[ctx.channel.id][6] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][7], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(7)
                                    EQTest[ctx.channel.id][7] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                    appended = True
                                    break
                                if eightMan[ctx.channel.id] == False:
                                    if isinstance(EQTest[ctx.channel.id][8], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(8)
                                        EQTest[ctx.channel.id][8] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                        appended = True
                                        break
                                    elif isinstance(EQTest[ctx.channel.id][9], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(9)
                                        EQTest[ctx.channel.id][9] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                        appended = True
                                        break
                                    elif isinstance(EQTest[ctx.channel.id][10], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(10)
                                        EQTest[ctx.channel.id][10] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                        appended = True
                                        break
                                    elif isinstance(EQTest[ctx.channel.id][11], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(11)
                                        EQTest[ctx.channel.id][11] = classRole + ' ' + SubDict[ctx.channel.id].pop(index) 
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {ctx.author.name} from the reserves to the MPA list.```')
                                        appended = True
                                        break
                            else:
                                if isinstance(EQTest[ctx.channel.id][0], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(0)
                                    EQTest[ctx.channel.id].insert(0, classRole + ' ' + ctx.author.name)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][1], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(1)
                                    EQTest[ctx.channel.id].insert(1, classRole + ' ' + ctx.author.name)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][2], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(2)
                                    EQTest[ctx.channel.id].insert(2, classRole + ' ' + ctx.author.name)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][3], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(3)
                                    EQTest[ctx.channel.id].insert(3, classRole + ' ' + ctx.author.name)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][4], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(4)
                                    EQTest[ctx.channel.id].insert(4, classRole + ' ' + ctx.author.name)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][5], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(5)
                                    EQTest[ctx.channel.id].insert(5, classRole + ' ' + ctx.author.name)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][6], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(6)
                                    EQTest[ctx.channel.id].insert(6, classRole + ' ' + ctx.author.name)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][7], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(7)
                                    EQTest[ctx.channel.id].insert(7, classRole + ' ' + ctx.author.name)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                    appended = True
                                    break
                                if eightMan[ctx.channel.id] == False:
                                    if isinstance(EQTest[ctx.channel.id][8], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(8)
                                        EQTest[ctx.channel.id].insert(8, classRole + ' ' + ctx.author.name)
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                        appended = True
                                        break
                                    elif isinstance(EQTest[ctx.channel.id][9], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(9)
                                        EQTest[ctx.channel.id].insert(9, classRole + ' ' + ctx.author.name)
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                        appended = True
                                        break
                                    elif isinstance(EQTest[ctx.channel.id][10], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(10)
                                        EQTest[ctx.channel.id].insert(10, classRole + ' ' + ctx.author.name)
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                        appended = True
                                        break
                                    elif isinstance(EQTest[ctx.channel.id][11], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(11)
                                        EQTest[ctx.channel.id].insert(11, classRole + ' ' + ctx.author.name)
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the MPA list```')
                                        appended = True
                                        break
                        else:
                            await generateList(ctx, "```fix\nYou are already in the MPA```")
                            roleAdded[ctx.channel.id] = False
                            break
                    if not appended:
                        if personInMPA == False: 
                            await generateList(ctx, "```css\nThe MPA is full. Adding to reserve list.```")
                            if personInReserve == False:
                                SubDict[ctx.channel.id].append(ctx.author.name)
                                await generateList(ctx, f'```diff\n+ Added {ctx.author.name} to the Reserve list```')
                            else:
                                await generateList(ctx, "```css\nYou are already in the Reserve List```")
                        else:
                            await generateList(ctx, "```css\nYou are already in the MPA```")
                appended = False     
            else:
                await ctx.send('There is no MPA to add yourself to!')
    else:
        await ctx.message.delete()

@client.command(name='eval')
async def cmd_eval(ctx, *arg):
    if ctx.author.id == OtherIDDict['Tenj']:
        try:
            result = eval(arg)
        except Exception:
            formatted_lines = traceback.format_exc().splitlines()
            await ctx.send('Failed to Evaluate.\n```py\n{}\n{}\n```'.format(formatted_lines[-1], '/n'.join(formatted_lines[4:-1])))
            return

        if asyncio.iscoroutine(result):
            result = await result

        if result:
            await ctx.send('Evaluated Successfully.\n```{}```'.format(result))
            return
    else:
        await ctx.send('No.')

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
                        if (ctx.guild.roles[index].id == '224757670823985152'):
                            await ctx.send(f'{ctx.guild.roles[index].mention} can now join in the MPA!')
                            await generateList(ctx, '```fix\nMPA is now open to non-members.```')
                    else:
                        await ctx.send('Opened MPA to non-members!')
                        await generateList(ctx, '```fix\nMPA is now open to non-members.```')
                        break

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


#This function actually performs the removempa command. This is a separate function so that the bot can remove mpas as well.
async def function_removempa(message):
    global MPACount
    if message.author.top_role.permissions.manage_emojis or message.author.id == OtherIDDict or message.author.top_role.permissions.administrator or message.author.id == client.user.id:
        if message.channel.id in mpaChannels[str(message.guild.id)]:
            if message.channel.id in EQTest:
                try:
                    #await ctx.message.delete()
                    del EQTest[message.channel.id]
                    MPACount -= 1
                    mpaRemoved[message.channel.id] = True
                    await client.get_channel(OtherIDDict['ControlPanel']).send('```diff\n- ' + message.author.name + '#' + message.author.discriminator + ' (ID: ' + str(message.author.id) + ') ' + 'Closed an MPA on ' + message.guild.name + '\n- Amount of Active MPAs: ' + str(MPACount) + '\nTimestamp: ' + str(datetime.now()) + '```')
                    print(message.author.name + ' Closed an MPA on ' + message.guild.name)
                    print('Amount of Active MPAs: ' + str(MPACount))
                    if eightMan[message.channel.id] == True:
                        eightMan[message.channel.id] = False
                    await message.channel.purge(limit=100, after=getTime, check=is_pinned)
                    participantCount[message.channel.id] = 0
                    index = ActiveMPA.index(message.channel.id)
                    ActiveMPA.pop(index)
                except KeyError:
                    pass
            else:
                await message.channel.send('There is no MPA to remove!')
        else:
            await message.channel.send('This command can only be used in a MPA channel!')
    else:
        await generateList(message, '```fix\nYou are not a manager. GTFO```')


@client.command(name='removempa')
async def cmd_removempa(ctx):
## TO DO: Allow the bot to call this command or even conver this command to it's own function so that the bot may call it to delete the mpa.
# Can pass ctx for all the information that it may need!
    await function_removempa(ctx.message)
    # global MPACount
    # if ctx.author.top_role.permissions.manage_emojis or ctx.author.id == OtherIDDict or ctx.author.top_role.permissions.administrator or ctx.author.id == client.user.id:
    #     if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
    #         if ctx.channel.id in EQTest:
    #             try:
    #                 #await ctx.message.delete()
    #                 del EQTest[ctx.channel.id]
    #                 MPACount -= 1
    #                 await client.get_channel(OtherIDDict['ControlPanel']).send('```diff\n- ' + ctx.author.name + '#' + ctx.author.discriminator + ' (ID: ' + str(ctx.author.id) + ') ' + 'Closed an MPA on ' + ctx.guild.name + '\n- Amount of Active MPAs: ' + str(MPACount) + '\nTimestamp: ' + str(datetime.now()) + '```')
    #                 print(ctx.author.name + ' Closed an MPA on ' + ctx.guild.name)
    #                 print('Amount of Active MPAs: ' + str(MPACount))
    #                 if eightMan[ctx.channel.id] == True:
    #                     eightMan[ctx.channel.id] = False
    #                 await ctx.channel.purge(limit=100, after=getTime, check=is_pinned)
    #                 participantCount[ctx.channel.id] = 0
    #                 index = ActiveMPA.index(ctx.channel.id)
    #                 ActiveMPA.pop(index)
    #             except KeyError:
    #                 pass
    #         else:
    #             await ctx.send('There is no MPA to remove!')
    #     else:
    #         await ctx.send('This command can only be used in a MPA channel!')
    # else:
    #     await generateList(ctx, '```fix\nYou are not a manager. GTFO```')

@client.command(name='add', aliases=['reserve'])
async def cmd_add(ctx, user: str = '', mpaArg: str = 'none'):
    if ctx.author.top_role.permissions.manage_emojis or ctx.author.id == OtherIDDict or ctx.guild.id == serverIDDict['RappyCasino'] or ctx.author.top_role.permissions.administrator:
        classRole = ''
        appended = False
        if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
            if ctx.channel.id in EQTest:
                if user == "":
                    await generateList(ctx, "```fix\nYou can't add nobody. Are you drunk?```")
                    appended = True
                else:
                    if mpaArg != 'none':
                        mpaClass = classMatch.findClass(mpaArg)
                        classRole += ' ' + classes[mpaClass]
                        roleAdded[ctx.channel.id] = True
                    else:
                        # As all servers share the same icons, there should always be a "class" added to each string. If there is no class, just use the no class icon.
                        mpaClass = classMatch.findClass('NoClass')
                        classRole += ' ' + classes[mpaClass]
                        roleAdded[ctx.channel.id] = True
                    if mpaArg == 'reserve' or 'reserve' in ctx.message.content:
                        if not user in EQTest[ctx.channel.id]: 
                            await generateList(ctx, "```fix\nReserve list requested. Adding...```")
                            if not user in SubDict[ctx.channel.id]:
                                SubDict[ctx.channel.id].append(user)
                                await generateList(ctx, f'```diff\n+ Added {user} to the Reserve list```')
                            else:
                                await generateList(ctx, "```diff\n+ That user is already in the Reserve List```")
                        else:
                            await generateList(ctx, "```fix\nThat user is already in the MPA```")
                        return
                    if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
                        expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
                    for word in EQTest[ctx.channel.id]:
                        if isinstance(word, PlaceHolder):
                            if not user in EQTest[ctx.channel.id]:
                                if isinstance(EQTest[ctx.channel.id][0], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(0)
                                    EQTest[ctx.channel.id].insert(0, classRole + ' ' + user)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][1], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(1)
                                    EQTest[ctx.channel.id].insert(1, classRole + ' ' + user)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][2], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(2)
                                    EQTest[ctx.channel.id].insert(2, classRole + ' ' + user)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][3], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(3)
                                    EQTest[ctx.channel.id].insert(3, classRole + ' ' + user)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][4], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(4)
                                    EQTest[ctx.channel.id].insert(4, classRole + ' ' + user)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][5], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(5)
                                    EQTest[ctx.channel.id].insert(5, classRole + ' ' + user)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][6], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(6)
                                    EQTest[ctx.channel.id].insert(6, classRole + ' ' + user)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                    appended = True
                                    break
                                elif isinstance(EQTest[ctx.channel.id][7], PlaceHolder):
                                    EQTest[ctx.channel.id].pop(7)
                                    EQTest[ctx.channel.id].insert(7, classRole + ' ' + user)
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                    appended = True
                                    break
                                if eightMan[ctx.channel.id] == False:    
                                    if isinstance(EQTest[ctx.channel.id][8], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(8)
                                        EQTest[ctx.channel.id].insert(8, classRole + ' ' + user)
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                        appended = True
                                        break
                                    elif isinstance(EQTest[ctx.channel.id][9], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(9)
                                        EQTest[ctx.channel.id].insert(9, classRole + ' ' + user)
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                        appended = True
                                        break
                                    elif isinstance(EQTest[ctx.channel.id][10], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(10)
                                        EQTest[ctx.channel.id].insert(10, classRole + ' ' + user)
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                        appended = True
                                        break
                                    elif isinstance(EQTest[ctx.channel.id][11], PlaceHolder):
                                        EQTest[ctx.channel.id].pop(11)
                                        EQTest[ctx.channel.id].insert(11, classRole + ' ' + user)
                                        participantCount[ctx.channel.id] += 1
                                        await generateList(ctx, f'```diff\n+ Added {user} to the MPA list```')
                                        appended = True
                                        break
                            if not appended:
                                await generateList(ctx, "```css\nThe MPA is full. Adding to reserve list.```")
                                SubDict[ctx.channel.id].append(user)
                                await generateList(ctx, f'```diff\n+ Added {user} to the Reserve list```')
            else:
                await ctx.send('There is no MPA.')
        else:
            await ctx.send('This command can only be used in a MPA channel!')
    else:
        await ctx.send("You don't have permissions to use this command")
    appended = False
    await ctx.message.delete()


@client.command(name='removeme')
async def cmd_removeme(ctx):
    inMPA = False
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
        if ctx.channel.id in EQTest:
            if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
                expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
            await ctx.message.delete()
            for index, item in enumerate(EQTest[ctx.channel.id]):
                if (type(EQTest[ctx.channel.id][index]) is PlaceHolder):
                    pass
                elif ctx.author.name in item:
                    EQTest[ctx.channel.id].pop(index)
                    EQTest[ctx.channel.id].insert(index, PlaceHolder(''))
                    participantCount[ctx.channel.id] -= 1
                    playerRemoved[ctx.channel.id] = True
                    await generateList(ctx, f'```diff\n- Removed {ctx.author.name} from the MPA list```')
                    if len(SubDict[ctx.channel.id]) > 0:
                        classRole = classes[10]
                        EQTest[ctx.channel.id][index] = classRole + ' ' + SubDict[ctx.channel.id].pop(0)
                        participantCount[ctx.channel.id] += 1
                        await generateList(ctx, f'```diff\n- Removed {ctx.author.name} from the MPA list and added {EQTest[ctx.channel.id][index]}```')
                    inMPA = True
                    return
            if inMPA == False:
                for index, item in enumerate(SubDict[ctx.channel.id]):
                    if ctx.author.name in item:
                        SubDict[ctx.channel.id].pop(index)
                        await generateList(ctx, f'```diff\n- Removed {ctx.author.name} from the Reserve list```')
                        return
                    else:
                        await generateList(ctx, '```fix\nYou were not in the MPA list in the first place.```')
                if len(SubDict[ctx.channel.id]) == 0:
                    await generateList(ctx, '```fix\nYou were not in the MPA list in the first place.```')

@client.command(name='changeclass')
async def cmd_changeclass(ctx, mpaArg):
    inMPA = False
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)] or ctx.author.top_role.permissions.administrator:
        if ctx.channel.id in EQTest:
            if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
                expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
            await ctx.message.delete()
            mpaClass = classMatch.findClass(mpaArg)
            newRole = classes[mpaClass]
            newRoleName = classMatch.findClassName(mpaClass)
            for index, item in enumerate(EQTest[ctx.channel.id]):
                if (type(EQTest[ctx.channel.id][index]) is PlaceHolder):
                    pass
                elif ctx.author.name in item:
                    EQTest[ctx.channel.id].pop(index)
                    EQTest[ctx.channel.id].insert(index, newRole + ' ' + ctx.author.name)
                    await generateList(ctx, f'```diff\n+ Changed {ctx.author.name}\'s class to ' + newRoleName + '```')
                    inMPA = True
                    return
            if inMPA == False:
                await generateList(ctx, '```fix\nYou are not in the MPA!```')

@client.command(name='remove')
async def cmd_remove(ctx, user):
    if ctx.author.top_role.permissions.manage_emojis or ctx.author.id == OtherIDDict or ctx.guild.id == serverIDDict['RappyCasino'] or ctx.author.top_role.permissions.administrator:
        if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
            if ctx.channel.id in EQTest:
                if len(EQTest[ctx.channel.id]):
                        for index in range(len(EQTest[ctx.channel.id])):
                            appended = False
                            if (type(EQTest[ctx.channel.id][index]) is PlaceHolder):
                                pass
                            elif user.lower() in EQTest[ctx.channel.id][index].lower():
                                toBeRemoved = EQTest[ctx.channel.id][index]
                                EQTest[ctx.channel.id][index] = user
                                EQTest[ctx.channel.id].remove(user)
                                EQTest[ctx.channel.id].insert(index, PlaceHolder(''))
                                user = user
                                participantCount[ctx.channel.id] -= 1
                                playerRemoved[ctx.channel.id] = True
                                toBeRemovedName = toBeRemoved.split()
                                toBeRemovedName2 = toBeRemovedName[1]
                                await generateList(ctx, f'```diff\n- Removed {toBeRemovedName2} from the MPA list```')
                                if len(SubDict[ctx.channel.id]) > 0:
                                    classRole = classes[10]
                                    EQTest[ctx.channel.id][index] = classRole + ' ' + SubDict[ctx.channel.id].pop(0)
                                    tobenamed = EQTest[ctx.channel.id][index].split()
                                    toBeNamed2 = tobenamed[1]
                                    participantCount[ctx.channel.id] += 1
                                    await generateList(ctx, f'```diff\n- Removed {toBeRemoved} from the MPA list and added {toBeNamed2}```')
                                appended = True
                                break
                        if not appended:
                            for index in range(len(SubDict[ctx.channel.id])):
                                appended = False
                                if user in SubDict[ctx.channel.id][index]:
                                    toBeRemoved = SubDict[ctx.channel.id][index]
                                    SubDict[ctx.channel.id][index] = user
                                    SubDict[ctx.channel.id].remove(user)
                                    user = user
                                    playerRemoved[ctx.channel.id] = True
                                    await generateList(ctx, f'```diff\n- Removed {toBeRemoved} from the Reserve list```')
                                    appended = True
                                    break
                        if not appended:    
                            await generateList(ctx, f"```fix\nPlayer {user} does not exist in the MPA list```")
                else:
                    await ctx.send("There are no players in the MPA.")
            else:
                await ctx.send('There is no MPA.')
            if ctx.channel.id in mpaExpirationConfig[str(ctx.guild.id)]:
                expirationDate[ctx.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
            await ctx.message.delete()
        else:
            await ctx.send('This command can only be used in a MPA Channel!')
    else:
        await generateList(ctx, "You don't have permissions to use this command")

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
                with open('assetsTonk/scheduledMpa.json', 'w') as fp:
                    json.dump(mpaScheduleDict, fp)
                    fp.close()
                    print (str(ctx.channel.id) + f' {scheduledTime}')
                    await ctx.send(f'Scheduled an MPA `{timeNumber} {timestat}` from now')
                return
            except Exception as e:
                await ctx.send('Error scheduling the MPA. Please see error in console')
                print (e)
                return
    else:
        await ctx.send('This is not an MPA channel! See `!help` for more information')
        return

print ('Logging into Discord...\n')        
@client.event
async def on_ready():
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
@client.event
async def on_server_join(server):
    await client.get_channel(OtherIDDict['ControlPanel']).send(f'```diff\n+ Joined {server.name} ```' + f'(ID: {str(server.id)})')
    general = find(lambda x: x.name == 'general',  server.channels)
    if general and general.permissions_for(server.me).send_messages:
        await general.send('**Greetings!**\nI am Tonk, a MPA organization bot for PSO2! Please type **!gettingstarted** to set my functions up!')
    # await client.send_message(client.get_channel(server.default_channel.id), '**Greetings!**\nI am Tonk, a MPA organization bot for PSO2! Please type **!gettingstarted** to set my functions up!')
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
    
client.run(Key)