import discord
import asyncio
import aiohttp
import traceback
import sys
import os
import re
import datetime
import time
from datetime import datetime,tzinfo,timedelta
from random import randint
from discord.utils import find
from assetsTonk import MpaMatch
from assetsTonk import classMatch


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
participantCount = {}
eightMan = {}
roleAdded = {}
color = {}
playerRemoved = {}
totalPeople = {}
appended = False
client = discord.Client()
lastRestart = str(datetime.now())
ActiveMPA = list()
serverIDDict = {
"Ishana": "159184581830901761", 
"Okra": "153346891109761024",
"Bloop": "226835458552758275",
"RappyCasino": "410601412620320819"
}
OtherIDDict = {
"Tenj": "153273725666590720",
"ControlPanel": "322466466479734784",
"EmojiStorage": "408395363762962432"
}

ChannelIDDict = {
"IshanaQuestBoard": "206673616060940288"
}

RoleIDDict = {
"IshanaFamilia": "357155081512026125"
}


def is_bot(m):
	return m.author == client.user
    
def is_not_bot(m):
    return m.author != client.user
def is_pinned(m):
    return m.pinned != True
    

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
            if message.server.id == serverIDDict['Ishana']:
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
            if message.server.id == serverIDDict['Ishana']:
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
    if message.server.id == serverIDDict['Ishana']:
        em.add_field(name='Meeting at', value='`' + 'Block 03`', inline=True)
    if message.server.id == serverIDDict['Ishana']:
        em.add_field(name='Party Status', value='`' + str(participantCount[message.channel.id]) + '/' + str(totalPeople[message.channel.id]) + '`', inline=True)
    else:
        em.add_field(name='Party Status', value='`' + str(participantCount[message.channel.id]) + '/' + str(totalPeople[message.channel.id]) + '`', inline=False)
    if message.server.id == serverIDDict['Ishana']:
        em.add_field(name='MPA Open?', value='`' + mpaFriendly + '`', inline=False)
    if message.server.id == serverIDDict['Ishana']:
        em.add_field(name='Participant List', value=playerlist, inline=True)
    else:
        em.add_field(name='Participant List', value=playerlist, inline=True)
    em.add_field(name='Class', value=classlist, inline=True)
    em.add_field(name='Last Action', value=inputstring, inline=False)
    em.set_author(name='An MPA is starting!', icon_url=message.server.icon_url)
           
    try:
        await client.edit_message(EQPostDict[message.channel.id], '', embed=em)
    except:
        print(message.author.name + ' Started an MPA on ' + message.server.name)
        MPACount += 1
        await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), '```css\n' + message.author.name + '#' + str(message.author.discriminator) + ' (ID: ' + message.author.id + ') ' + 'Started an MPA on ' + message.server.name + '\nAmount of Active MPAs: ' + str(MPACount) + '\nTimestamp: ' + str(datetime.now()) + '```')
        print('Amount of Active MPAs: ' + str(MPACount))
        EQPostDict[message.channel.id] = await client.send_message(message.channel, '', embed=em)
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
    if message.content.startswith('!'):
        if message.server.id == '159184581830901761':
            return
		#Debugging commands
        if message.content.lower() == '!gethighestrole':
            if not message.channel.name.startswith('mpa'):
                await client.send_message(message.channel, message.author.top_role)
        elif message.content.lower() == '!listroles':
            if not message.channel.name.startswith('mpa'):
                for index in range(len(message.author.roles)):
                    if len(message.author.roles) == 0:
                        await client.send_message(message.channel, 'You either dont have a role, or w command is bugged.')
                    else:
                        await client.send_message(message.channel, message.author.roles[index].name + str(index))
        elif message.content.lower().startswith('!quickclean '):
            if message.author.top_role.permissions.manage_channels or message.author.id == OtherIDDict['Tenj']:
                userstr = message.content
                userstr = userstr.replace("!quickclean", "")
                userstr = userstr.replace(" ", "")
                toClean = int(userstr) + 1
                await client.purge_from(message.channel, limit=toClean)
            else:
                await client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
        elif message.content.lower() == '!checkmpamanagerperm':
            if not message.channel.name.startswith('mpa'):
                doIHavePermission = message.author.top_role.permissions.manage_emojis
                if doIHavePermission:
                    await client.send_message(message.channel, 'You have the permissions to start an MPA.')
                else:
                    await client.send_message(message.channel, 'You do not have the permission to start an MPA. Take a hike.')
        # Purges everything that isn't made by the bot.
        elif message.content.lower() == '!ffs':
            if message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.id == OtherIDDict['Tenj']:
                    await client.purge_from(message.channel, limit=100, after=getTime, check=is_not_bot)
                else:
                    await client.send_message(message.channel, 'You lack the permissions to use this command.')
            else:
                await client.send_message(message.channel, 'This command can only be used in a MPA channel.')
        # These commands are for Me (Tenj), or whoever runs this bot. 
        elif message.content.lower() == '!!shutdown':
            if message.author.id == OtherIDDict['Tenj']:
                if message.server.id == serverIDDict['Ishana']:
                    await client.send_message(message.channel, 'Shutting down. If anything goes wrong during the downtime, please blame yui.')
                else:
                    await client.send_message(message.channel, 'DONT DO THIS TO ME MA-')
                    await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), 'Tonk is {}'.format(client.get_server(serverIDDict['Bloop']).roles[25].mention))
                await client.logout()
            else:
                await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
        # Closes all MPAs the bot has ever known to be active at this moment. Easy to use before shutting the bot down.
        elif message.content.lower() == '!!burnbabyburn':
            if message.author.id == OtherIDDict['Tenj']:
                if len(ActiveMPA) > 0:
                    for index in range(len(ActiveMPA)):
                        await client.send_message(client.get_channel(ActiveMPA[index]), '!removempa')
                    await client.send_message(message.channel, 'Successfully closed all existing MPAs on all servers.')
                else:
                    await client.send_message(message.channel, 'No MPAs currently exist.')
            else:
                await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
        elif message.content.lower().startswith('!!leaveserver'):
            if message.author.id == OtherIDDict['Tenj']:
                userstr = message.content
                userstr = userstr.replace("!!leaveserver", "")
                userstr = userstr.replace(" ", "")
                await client.leave_server(client.get_server(userstr))
            else:
                await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
        elif message.content.lower().startswith('!!findroleid'):
            if message.author.id == OtherIDDict['Tenj']:
                userstr = message.content
                userstr = userstr.replace("!!findroleid", "")
                userstr = userstr.replace(" ", "")
                foundRole = discord.utils.get(message.server.roles, name=userstr)
                if foundRole is not None:
                    em = discord.Embed(colour=foundRole.colour)
                    em.add_field(name='Role Name:', value=foundRole.name, inline=False)
                    em.add_field(name='Role ID', value=foundRole.id, inline=False)
                    await client.send_message(message.channel, '', embed=em)
                else:
                    await client.send_message(message.channel, 'Unable to find a role with that name!')
            else:
                await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
        elif message.content.lower().startswith('!!announce'):
            if message.author.id == OtherIDDict['Tenj']:
                userstr = message.content
                if message.content.startswith('!!announce'):
                    userstr = userstr.replace("!!announce", "")
                else:
                    userstr = userstr.replace("!!announce", "")
                if message.server.id == OtherIDDict['EmojiStorage']:
                    return
                else:
                    for item in client.servers:
                        if item.id == serverIDDict['Bloop'] or item.id == OtherIDDict['EmojiStorage']:
                            pass
                        try:
                            await client.send_message(client.get_channel(item.default_channel.id), '{}'.format(userstr))
                            await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), 'Sent announcement to ' + item.name)
                        except AttributeError:
                            await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), 'Error trying to send announcement to ' + item.name)
                            pass
                        await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), 'All announcements sent.')
                # await client.send_message(client.get_channel('326883995641970689'), userstr)
            await client.delete_message(message)
        elif message.content.lower() == '!!lastrestart':
            if message.author.id == OtherIDDict['Tenj']:
                await client.send_message(message.channel, str(lastRestart))
            else:
                await client.send_message(message.channel, 'Only Tenj may use this command.')
        elif message.content.lower() == '!!listservers':
            serverlist = ''
            if message.author.id == OtherIDDict['Tenj']:
                for item in client.servers:
                    serverlist += (item.name + f'\n{item.id}' + '\n')
                em = discord.Embed(description=serverlist, colour=0x0099FF)
                em.set_author(name='Joined Servers')
                await client.send_message(message.channel, '', embed=em)
            else:
                await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.') 
        elif message.content.lower() == '!!restart':
            if message.author.id == OtherIDDict['Tenj']:
                await client.send_message(message.channel, 'Tonk will now restart!')
                print ('The restart command was issued! Restarting Bot...')
                end = time.time()
                runTime = (end - start)
                restartRole = discord.utils.get(message.server.roles, id='370339592055947266')
                await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), f'Tonk is {restartRole.mention}' + '\nRun time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(runTime)))
                os.execl(sys.executable, *([sys.executable]+sys.argv))
            else:
                await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
        elif message.content.lower() == '!!clearconsole':
            if message.author.id == OtherIDDict['Tenj']:
                await client.send_message(message.channel, 'Clearing Console')
                os.system('cls' if os.name == 'nt' else 'clear')
            else:
                await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
        elif message.content.lower().startswith('!eval'):
            if message.author.id == OtherIDDict['Tenj']:
                userstr = message.content
                userstr = userstr.replace("!eval", "")
                try:
                    result = eval(userstr)
                except Exception:
                    formatted_lines = traceback.format_exc().splitlines()
                    await client.send_message(message.channel, 'Failed to Evaluate.\n```py\n{}\n{}\n```'.format(formatted_lines[-1], '/n'.join(formatted_lines[4:-1])))
                    return

                if asyncio.iscoroutine(result):
                    result = await result

                if result:
                    await client.send_message(message.channel, 'Evaluated Successfully.\n```{}```'.format(result))
                    return
            else:
                await client.send_message(message.channel, 'No.')
        ## MPA TRACKER COMMANDS ##
        #Starts the MPA on the current eq channel. Places the channel name into a dictionary and sets it to be a list. Then fills the list up with 12 placeholder objects.
               
        elif message.content.lower().startswith('!startmpa'):
            userstr = message.content
            userstr = userstr.replace("!startmpa", "")
            userstr2 = ''
            inTesting = False
            # This checks if Tonk has the deleting permission. If it doesn't, don't run the script at all and just stop.
            try:
                await client.delete_message(message)
            except discord.Forbidden:
                print (message.author.name + f' Tried to start an MPA at {message.server.name}, but failed.')
                await client.send_message(message.author, 'I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                return
            if message.channel.name.startswith('mpa') or message.channel.id == ChannelIDDict['IshanaQuestBoard']:
                if message.server.id == serverIDDict['Ishana']:
                    mpaMap = MpaMatch.get_class(userstr)
                    inTesting = True
                    await client.send_file(message.channel, os.path.join('assetsTonk', mpaMap))
                else:
                    if userstr == ' busterquest':
                        await client.send_message(message.channel, 'Would you like to say anything else? (Yes/no)')
                        prompt = await client.wait_for_message(author=message.author, timeout=10)
                        if prompt.content.lower() != 'yes':
                            userstr2 = 'Buster Quest'
                        else:
                            await client.send_message(message.channel, 'Please enter what you want to say')
                            userstr2 = await client.wait_for_message(author=message.author, timeout=300)
                            userstr2 = userstr2.content
                            await client.purge_from(message.channel, limit=4, after=getTime)
                    else:
                        userstr2 = userstr
                if userstr == ' 8man' or userstr == ' pvp' or userstr == ' busterquest':
                    eightMan[message.channel.id] = True
                else:
                    eightMan[message.channel.id] = False
                if not message.channel.id in EQTest:
                    if message.author.top_role.permissions.manage_emojis or message.author.id == OtherIDDict or message.author.top_role.permissions.administrator:
                        try:
                            if inTesting != True:
                                await client.send_message(message.channel, f'{message.server.default_role}' + f' {userstr2}')
                            EQTest[message.channel.id] = list()
                            SubDict[message.channel.id] = list()
                            ActiveMPA.append(message.channel.id)
                            roleAdded[message.channel.id] = False
                            guestEnabled[message.channel.id] = False
                            playerRemoved[message.channel.id] = False
                            participantCount[message.channel.id] = 0
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
                            print (message.author.name + f'Tried to start an MPA at {message.server.name}, but failed.')
                            await client.send_message(message.author, 'I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                            return

                    else:
                        await client.send_message(message.channel, 'You do not have the permission to do that, starfox.')
                else:
                    await generateList(message, '```fix\nThere is already an MPA being made here!```')
            else:
                await client.send_message(message.channel, 'You can only start a MPA on a MPA channel!')
        # Opens the MPA to any role to the server if there is a lock enabled for the server.        
        elif message.content.lower() == '!openmpa':
            if message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.id == OtherIDDict or message.author.top_role.permissions.administrator:
                    if guestEnabled[message.channel.id] == True:
                        await client.send_message(message.channel, 'This MPA is already open!')
                    else:
                        guestEnabled[message.channel.id] = True
                        for index in range(len(message.server.roles)):
                            if message.server.id == serverIDDict['Okra']:
                                if (message.server.roles[index].id == '224757670823985152'):
                                    await client.send_message(message.channel, f'{message.server.roles[index].mention} can now join in the MPA!')
                                    await generateList(message, '```fix\nMPA is now open to non-members.```')
                            else:
                                await client.send_message(message.channel, 'Opened MPA to non-members!')
                                await generateList(message, '```fix\nMPA is now open to non-members.```')
                                break
        # Closes the MPA to a specific amount of roles in the server only.                         
        elif message.content.lower() == '!closempa':
            if message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.id == OtherIDDict or message.author.top_role.permissions.administrator:
                    if guestEnabled[message.channel.id] == False:
                        await client.send_message(message.channel, 'This MPA is already closed!')
                    else:
                        guestEnabled[message.channel.id] = False
                        await client.send_message(message.channel, 'Closed MPA to Members only.')
                        await generateList(message, '```fix\nMPA is now closed to non-members```')
                else:
                    await client.send_message(message.channel, 'You do not have the permission to do this.')
     
        # Removes the current MPA on the channel and cleans the channel up for the next one. Use this when the MPA is finished so the bot doesn't go insane on next MPA create.
                                 
        elif message.content.lower() == '!removempa':
            if message.author.top_role.permissions.manage_emojis or message.author.id == OtherIDDict or message.author.top_role.permissions.administrator or message.author.id == client.user.id:
                if message.channel.name.startswith('mpa') or message.channel.id == ChannelIDDict['IshanaQuestBoard']:
                    if message.channel.id in EQTest:
                        try:
                            await client.delete_message(message)
                            del EQTest[message.channel.id]
                            MPACount -= 1
                            await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), '```diff\n- ' + message.author.name + '#' + message.author.discriminator + ' (ID: ' + message.author.id + ') ' + 'Closed an MPA on ' + message.server.name + '\n- Amount of Active MPAs: ' + str(MPACount) + '\nTimestamp: ' + str(datetime.now()) + '```')
                            print(message.author.name + ' Closed an MPA on ' + message.server.name)
                            print('Amount of Active MPAs: ' + str(MPACount))
                            if eightMan[message.channel.id] == True:
                                eightMan[message.channel.id] = False
                            if message.channel.id == ChannelIDDict['IshanaQuestBoard']:
                                await client.purge_from(message.channel, limit=15, check=is_bot)
                                participantCount[message.channel.id] = 0
                            else:
                                await client.purge_from(message.channel, limit=100, after=getTime, check=is_pinned)
                                participantCount[message.channel.id] = 0
                            index = ActiveMPA.index(message.channel.id)
                            ActiveMPA.pop(index)
                        except KeyError:
                            pass
                    else:
                        await client.send_message(message.channel, 'There is no MPA to remove!')
                else:
                    await client.send_message(message.channel, 'This command can only be used in a MPA channel!')
            else:
                await generateList(message, '```fix\nYou are not a manager. GTFO```')
        # Adds the user into the EQ list in the EQ channel. Optionally takes a class as an arguement. If one is passed, add the class icon and the user's name into the EQ list.
        elif message.content.lower().startswith('!addme'):
            bypassCheck = False
            userstr = ''
            classRole = ''
            index = 0
            personInMPA = False
            personInReserve = False
            roleAdded[message.channel.id] = False
            if message.channel.name.startswith('mpa') or message.channel.id == ChannelIDDict['IshanaQuestBoard'] or message.author.top_role.permissions.administrator:
                for index in range(len(message.author.roles)):
                    if message.author.roles[index].id == RoleIDDict['IshanaFamilia']:
                        bypassCheck = True
                        break
                    elif message.author.top_role.permissions.manage_emojis:
                        bypassCheck = True
                        break
                    elif message.server.id == serverIDDict['Ishana']:
                        bypassCheck = False
                    else:
                        bypassCheck = True
                if (bypassCheck == False and guestEnabled[message.channel.id] == False):
                    await generateList(message, '```fix\nGuests are not allowed to join this MPA.```')
                    await client.delete_message(message)
                    return
                else:
                    if message.channel.id in EQTest:
                        userstr = message.content
                        userstr = userstr.replace("!addme", "")
                        userstr = userstr.replace(" ", "")
                        for index, item in enumerate(EQTest[message.channel.id]):
                            if (type(EQTest[message.channel.id][index]) is PlaceHolder):
                                pass
                            elif message.author.name in item:
                                personInMPA = True
                                break
                        for index, item in enumerate(SubDict[message.channel.id]):
                            if message.author.name in item:
                                personInReserve = True
                                break
                        mpaClass = classMatch.findClass(userstr)
                        classRole += ' ' + classes[mpaClass]
                        roleAdded[message.channel.id] = True
                        if userstr == 'reserve':
                            if personInMPA == False: 
                                await generateList(message, "```fix\nReserve list requested. Adding...```")
                                await client.delete_message(message)
                                if personInReserve == False:
                                    SubDict[message.channel.id].append(message.author.name)
                                    await generateList(message, f'```diff\n+ Added {message.author.name} to the Reserve list```')
                                else:
                                    await generateList(message, "```diff\n+ You are already in the Reserve List```")
                            else:
                                await generateList(message, "```fix\nYou are already in the MPA```")
                            return
                        await client.delete_message(message)
                        for word in EQTest[message.channel.id]:
                            if isinstance(word, PlaceHolder):
                                if personInMPA == False:
                                    if (message.author.name in SubDict[message.channel.id]):
                                        index = SubDict[message.channel.id].index(message.author.name)
                                        if isinstance(EQTest[message.channel.id][0], PlaceHolder):
                                            EQTest[message.channel.id].pop(0)
                                            EQTest[message.channel.id][0] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][1], PlaceHolder):
                                            EQTest[message.channel.id].pop(1)
                                            EQTest[message.channel.id][1] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][2], PlaceHolder):
                                            EQTest[message.channel.id].pop(2)
                                            EQTest[message.channel.id][2] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][3], PlaceHolder):
                                            EQTest[message.channel.id].pop(3)
                                            EQTest[message.channel.id][3] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][4], PlaceHolder):
                                            EQTest[message.channel.id].pop(4)
                                            EQTest[message.channel.id][4] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][5], PlaceHolder):
                                            EQTest[message.channel.id].pop(5)
                                            EQTest[message.channel.id][5] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][6], PlaceHolder):
                                            EQTest[message.channel.id].pop(6)
                                            EQTest[message.channel.id][6] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][7], PlaceHolder):
                                            EQTest[message.channel.id].pop(7)
                                            EQTest[message.channel.id][7] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                            appended = True
                                            break
                                        if eightMan[message.channel.id] == False:
                                            if isinstance(EQTest[message.channel.id][8], PlaceHolder):
                                                EQTest[message.channel.id].pop(8)
                                                EQTest[message.channel.id][8] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][9], PlaceHolder):
                                                EQTest[message.channel.id].pop(9)
                                                EQTest[message.channel.id][9] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][10], PlaceHolder):
                                                EQTest[message.channel.id].pop(10)
                                                EQTest[message.channel.id][10] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][11], PlaceHolder):
                                                EQTest[message.channel.id].pop(11)
                                                EQTest[message.channel.id][11] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {message.author.name} from the reserves to the MPA list.```')
                                                appended = True
                                                break
                                    else:
                                        if isinstance(EQTest[message.channel.id][0], PlaceHolder):
                                            EQTest[message.channel.id].pop(0)
                                            EQTest[message.channel.id].insert(0, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][1], PlaceHolder):
                                            EQTest[message.channel.id].pop(1)
                                            EQTest[message.channel.id].insert(1, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][2], PlaceHolder):
                                            EQTest[message.channel.id].pop(2)
                                            EQTest[message.channel.id].insert(2, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][3], PlaceHolder):
                                            EQTest[message.channel.id].pop(3)
                                            EQTest[message.channel.id].insert(3, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][4], PlaceHolder):
                                            EQTest[message.channel.id].pop(4)
                                            EQTest[message.channel.id].insert(4, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][5], PlaceHolder):
                                            EQTest[message.channel.id].pop(5)
                                            EQTest[message.channel.id].insert(5, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][6], PlaceHolder):
                                            EQTest[message.channel.id].pop(6)
                                            EQTest[message.channel.id].insert(6, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][7], PlaceHolder):
                                            EQTest[message.channel.id].pop(7)
                                            EQTest[message.channel.id].insert(7, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                            appended = True
                                            break
                                        if eightMan[message.channel.id] == False:
                                            if isinstance(EQTest[message.channel.id][8], PlaceHolder):
                                                EQTest[message.channel.id].pop(8)
                                                EQTest[message.channel.id].insert(8, classRole + ' ' + message.author.name)
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][9], PlaceHolder):
                                                EQTest[message.channel.id].pop(9)
                                                EQTest[message.channel.id].insert(9, classRole + ' ' + message.author.name)
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][10], PlaceHolder):
                                                EQTest[message.channel.id].pop(10)
                                                EQTest[message.channel.id].insert(10, classRole + ' ' + message.author.name)
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][11], PlaceHolder):
                                                EQTest[message.channel.id].pop(11)
                                                EQTest[message.channel.id].insert(11, classRole + ' ' + message.author.name)
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {message.author.name} to the MPA list```')
                                                appended = True
                                                break
                                else:
                                    await generateList(message, "```fix\nYou are already in the MPA```")
                                    roleAdded[message.channel.id] = False
                                    break
                        if not appended:
                            if personInMPA == False: 
                                await generateList(message, "```css\nThe MPA is full. Adding to reserve list.```")
                                if personInReserve == False:
                                    SubDict[message.channel.id].append(message.author.name)
                                    await generateList(message, f'```diff\n+ Added {message.author.name} to the Reserve list```')
                                else:
                                    await generateList(message, "```css\nYou are already in the Reserve List```")
                            else:
                                await generateList(message, "```css\nYou are already in the MPA```")
                        appended = False     
                    else:
                        await client.send_message(message.channel, 'There is no MPA to add yourself to!')
            else:
                await client.delete_message(message)
                            
        # Adds a string/name of a player that the Manager wants into the MPA list. Can also take a class role as well.
        elif message.content.lower().startswith('!add '):
            if message.author.top_role.permissions.manage_emojis or message.author.id == OtherIDDict or message.server.id == serverIDDict['RappyCasino'] or message.author.top_role.permissions.administrator:
                userstr = ''
                classRole = ''
                if message.channel.name.startswith('mpa') or message.channel.id == ChannelIDDict['IshanaQuestBoard']:
                    if message.channel.id in EQTest:
                        userstr = message.content
                        userstr = userstr.replace("!add ", "")
                        if userstr == "":
                            await generateList(message, "```fix\nYou can't add nobody. Are you drunk?```")
                            appended = True
                        else:
                            splitstr = userstr.split()
                            if len(splitstr) == 2:
                                mpaClass = classMatch.findClass(splitstr[1])
                                classRole += ' ' + classes[mpaClass]
                                roleAdded[message.channel.id] = True
                            else:
                                # As all servers share the same icons, there should always be a "class" added to each string. If there is no class, just use the no class icon.
                                mpaClass = classMatch.findClass('NoClass')
                                classRole += ' ' + classes[mpaClass]
                                roleAdded[message.channel.id] = True
                            for word in EQTest[message.channel.id]:
                                if isinstance(word, PlaceHolder):
                                    if not(str(splitstr[0]) in EQTest[message.channel.id]):
                                        if isinstance(EQTest[message.channel.id][0], PlaceHolder):
                                            EQTest[message.channel.id].pop(0)
                                            EQTest[message.channel.id].insert(0, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][1], PlaceHolder):
                                            EQTest[message.channel.id].pop(1)
                                            EQTest[message.channel.id].insert(1, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][2], PlaceHolder):
                                            EQTest[message.channel.id].pop(2)
                                            EQTest[message.channel.id].insert(2, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][3], PlaceHolder):
                                            EQTest[message.channel.id].pop(3)
                                            EQTest[message.channel.id].insert(3, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][4], PlaceHolder):
                                            EQTest[message.channel.id].pop(4)
                                            EQTest[message.channel.id].insert(4, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][5], PlaceHolder):
                                            EQTest[message.channel.id].pop(5)
                                            EQTest[message.channel.id].insert(5, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][6], PlaceHolder):
                                            EQTest[message.channel.id].pop(6)
                                            EQTest[message.channel.id].insert(6, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][7], PlaceHolder):
                                            EQTest[message.channel.id].pop(7)
                                            EQTest[message.channel.id].insert(7, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                            appended = True
                                            break
                                        if eightMan[message.channel.id] == False:    
                                            if isinstance(EQTest[message.channel.id][8], PlaceHolder):
                                                EQTest[message.channel.id].pop(8)
                                                EQTest[message.channel.id].insert(8, classRole + ' ' + splitstr[0])
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][9], PlaceHolder):
                                                EQTest[message.channel.id].pop(9)
                                                EQTest[message.channel.id].insert(9, classRole + ' ' + splitstr[0])
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][10], PlaceHolder):
                                                EQTest[message.channel.id].pop(10)
                                                EQTest[message.channel.id].insert(10, classRole + ' ' + splitstr[0])
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][11], PlaceHolder):
                                                EQTest[message.channel.id].pop(11)
                                                EQTest[message.channel.id].insert(11, classRole + ' ' + splitstr[0])
                                                participantCount[message.channel.id] += 1
                                                await generateList(message, f'```diff\n+ Added {splitstr[0]} to the MPA list```')
                                                appended = True
                                                break
                        if not appended:
                            await generateList(message, "```css\nThe MPA is full. Adding to reserve list.```")
                            SubDict[message.channel.id].append(userstr)
                            await generateList(message, f'```diff\n+ Added {userstr} to the Reserve list```')
                    else:
                        await client.send_message(message.channel, 'There is no MPA.')
                    await client.delete_message(message)
                else:
                    await client.send_message(message.channel, 'This command can only be used in a MPA channel!')
            else:
                await client.send_message(message.channel, "You don't have permissions to use this command")
            appended = False
        #Removes the user name from the MPA list.
        elif message.content.lower() == '!removeme':
            inMPA = False
            if message.channel.name.startswith('mpa') or message.channel.id == ChannelIDDict['IshanaQuestBoard']:
                if message.channel.id in EQTest:
                    await client.delete_message(message)
                    for index, item in enumerate(EQTest[message.channel.id]):
                        if (type(EQTest[message.channel.id][index]) is PlaceHolder):
                            pass
                        elif message.author.name in item:
                            EQTest[message.channel.id].pop(index)
                            EQTest[message.channel.id].insert(index, PlaceHolder(''))
                            participantCount[message.channel.id] -= 1
                            playerRemoved[message.channel.id] = True
                            await generateList(message, f'```diff\n- Removed {message.author.name} from the MPA list```')
                            if len(SubDict[message.channel.id]) > 0:
                                classRole = classes[10]
                                EQTest[message.channel.id][index] = classRole + ' ' + SubDict[message.channel.id].pop(0)
                                participantCount[message.channel.id] += 1
                                await generateList(message, f'```diff\n- Removed {message.author.name} from the MPA list and added {EQTest[message.channel.id][index]}```')
                            inMPA = True
                            return
                    if inMPA == False:
                        for index, item in enumerate(SubDict[message.channel.id]):
                            if message.author.name in item:
                                SubDict[message.channel.id].pop(index)
                                await generateList(message, f'```diff\n- Removed {message.author.name} from the Reserve list```')
                                return
                            else:
                                await generateList(message, '```fix\nYou were not in the MPA list in the first place.```')
                        if len(SubDict[message.channel.id]) == 0:
                            await generateList(message, '```fix\nYou were not in the MPA list in the first place.```')
        # Allows the player to change their class without altering their position in the MPA list.
        elif message.content.lower().startswith('!changeclass'):
            inMPA = False
            if message.channel.name.startswith('mpa') or message.channel.id == ChannelIDDict['IshanaQuestBoard'] or message.author.top_role.permissions.administrator:
                if message.channel.id in EQTest:
                    userstr = message.content
                    userstr = userstr.replace("!changeclass", "")
                    userstr = userstr.replace(" ", "")
                    await client.delete_message(message)
                    mpaClass = classMatch.findClass(userstr)
                    newRole = classes[mpaClass]
                    newRoleName = classMatch.findClassName(mpaClass)
                    for index, item in enumerate(EQTest[message.channel.id]):
                        if (type(EQTest[message.channel.id][index]) is PlaceHolder):
                            pass
                        elif message.author.name in item:
                            EQTest[message.channel.id].pop(index)
                            EQTest[message.channel.id].insert(index, newRole + ' ' + message.author.name)
                            await generateList(message, f'```diff\n+ Changed {message.author.name}\'s class to ' + newRoleName + '```')
                            inMPA = True
                            return
                    if inMPA == False:
                        await generateList(message, '```fix\nYou are not in the MPA!```')
        #Removes the player name that matches the input string that is given.
        elif message.content.lower().startswith('!remove'):
            if message.author.top_role.permissions.manage_emojis or message.author.id == OtherIDDict or message.server.id == serverIDDict['RappyCasino'] or message.author.top_role.permissions.administrator:
                if message.channel.name.startswith('mpa') or message.channel.id == ChannelIDDict['IshanaQuestBoard']:
                    if message.channel.id in EQTest:
                        if len(EQTest[message.channel.id]):
                                userstr = message.content
                                userstr = userstr.replace("!remove ", "")
                                for index in range(len(EQTest[message.channel.id])):
                                    appended = False
                                    if (type(EQTest[message.channel.id][index]) is PlaceHolder):
                                        pass
                                    elif userstr.lower() in EQTest[message.channel.id][index].lower():
                                        toBeRemoved = EQTest[message.channel.id][index]
                                        EQTest[message.channel.id][index] = userstr
                                        EQTest[message.channel.id].remove(userstr)
                                        EQTest[message.channel.id].insert(index, PlaceHolder(''))
                                        userstr = userstr
                                        participantCount[message.channel.id] -= 1
                                        playerRemoved[message.channel.id] = True
                                        toBeRemovedName = toBeRemoved.split()
                                        toBeRemovedName2 = toBeRemovedName[1]
                                        await generateList(message, f'```diff\n- Removed {toBeRemovedName2} from the MPA list```')
                                        if len(SubDict[message.channel.id]) > 0:
                                            classRole = classes[10]
                                            EQTest[message.channel.id][index] = classRole + ' ' + SubDict[message.channel.id].pop(0)
                                            tobenamed = EQTest[message.channel.id][index].split()
                                            toBeNamed2 = tobenamed[1]
                                            participantCount[message.channel.id] += 1
                                            await generateList(message, f'```diff\n- Removed {toBeRemoved} from the MPA list and added {toBeNamed2}```')
                                        appended = True
                                        break
                                if not appended:
                                    for index in range(len(SubDict[message.channel.id])):
                                        appended = False
                                        if userstr in SubDict[message.channel.id][index]:
                                            toBeRemoved = SubDict[message.channel.id][index]
                                            SubDict[message.channel.id][index] = userstr
                                            SubDict[message.channel.id].remove(userstr)
                                            userstr = userstr
                                            playerRemoved[message.channel.id] = True
                                            await generateList(message, f'```diff\n- Removed {toBeRemoved} from the Reserve list```')
                                            appended = True
                                            break
                                if not appended:    
                                    await generateList(message, f"```fix\nPlayer {userstr} does not exist in the MPA list```")
                        else:
                            await client.send_message(message.channel, "There are no players in the MPA.")
                    else:
                        await client.send_message(message.channel, 'There is no MPA.')
                    await client.delete_message(message)
                else:
                    await client.send_message(message.channel, 'This command can only be used in a MPA Channel!')
            else:
                await generateList(message, "You don't have permissions to use this command")
 ## GENERAL COMMANDS ##                      
        if message.content.lower() == ('!help'):
            if not message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator:   
                    em = discord.Embed(description='Greetings! I am a majestic bot that mainly organizes the team MPAs! \nMy following commands are:\n**!addme** - register yourself to the MPA. If the MPA is full, you will be automatically placed into the reserve list.\n**!removeme** - Removes yourself from the MPA. \n\n**Manager only commands:** \n**!startmpa *<message>*** - Starts an MPA. Whatever you type in <message> will be sent out in a @everyone tag. You may use spaces and bolds and whatnot. This is useable ONLY in a channel that begins with "mpa". You cannot have more than one mpa at a time in one channel. \n**!removempa** - Closes the mpa to prevent further sign ups and allows for another MPA to be started. \n**!add <playername>** - Adds a name to the MPA list. \n**!remove <playername>** - Removes a name from the MPA list \n**!ffs** - Cleans everything but the list in a MPA channel. Useful in case conversations start breaking out in the MPA channel.', colour=0xB3ECFF)
                    if message.server.id == serverIDDict['Ishana']:                    
                        em2 = discord.Embed(description='!startmpa also can place one of the EQ banners seen in this server. By doing **!startmpa <MPA>** Tonk can add an image of the EQ to make it look prettier. So far, the EQs available are: \n**deus** - Deus Esca \n**mother** - Esca Falz Mother \n**pd** - Profound Darkness \n**pi** - Profound Invasion \n**trigger** - A trigger run \n**td3** - Tower Defense Despair \n**td4** - Tower Defense Demise \n**tdvr** - Mining Base VR \n**yamato** - Yamato. \n**Example use:** *!startmpa deus* will call a deus MPA. Give it a try!', colour=0xB3ECFF)
                else:
                    em = discord.Embed(description='', colour=0xB3ECFF)
                em.set_author(name='All Tonk Commands!', icon_url=client.user.avatar_url)
                if message.server.id == serverIDDict['Ishana'] and message.author.top_role.permissions.manage_emojis:
                    em2.set_author(name='Startmpa special arguments', icon_url=client.user.avatar_url)
                await client.send_message(message.channel, embed=em)
                if message.server.id == serverIDDict['Ishana']:
                    await client.send_message(message.channel, embed=em2)
        elif message.content.lower() == ('!gettingstarted'):
            if not message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator:   
                    em = discord.Embed(description='Setting up Tonk is a fairly simple process.', colour=0xB3ECFF)
                    em.add_field(name='Permissions Required for Tonk to function:', value='Manage Messages\nSend Messages\nRead Text Channels & See Voice Channels\nRead Message History', inline=True)
                    em.add_field(name='Permissions Required to start an MPA (as well as all manager commands):', value='Manage Emojis', inline=True)
                    em.add_field(name='Channel Requirements', value='The Channel **MUST** start with "***mpa***" in the title. Anything past that is fine. Example name would be #mpa-organizer.\nAdditionally, only **ONE** MPA may be active in a channel. If you wish to have multiple mpas in one server, you must make new mpa channels to get this to work.', inline=False)
                    em.add_field(name='How to use command?', value='See !help', inline=False)
                else:
                    em = discord.Embed(description='Please have a server administrator use this command!', colour=0xB3ECFF)
                em.set_author(name='Getting started with Tonk', icon_url=client.user.avatar_url)
                await client.send_message(message.channel, embed=em)
        elif message.content.lower() == '!test':
            if not message.channel.name.startswith('mpa'):
                await client.send_message(message.channel, f'At this point, you should just give up me, {message.author.mention}.')  
        elif message.content.lower() == '!howtoeq':
                if not message.channel.name.startswith('mpa'):
                    await client.send_message(message.channel, 'https://cdn.discordapp.com/attachments/303811844072538114/304729244255125506/how2mpa.png')
print ('Logging into Discord...\n')        
@client.event
async def on_ready():
    connectedServers = 0
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print ('Logged in to servers:')
    for item in client.servers:
        print (item)
        connectedServers += 1
    end = time.time()
    loadupTime = (end - start)
    print ('Tonk is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)))
    print('------')
    await client.change_presence(game=discord.Game(name='just tonk things', status=discord.Status.online))
    onlineRole = discord.utils.get(client.get_server(serverIDDict['Bloop']).roles, id='370337403769978880')
    await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), f'Tonk is now {onlineRole.mention}' + '\nStartup time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nConnected to **' + str(connectedServers) + '** servers' + '\nLast Restarted: ' + lastRestart)
@client.event
async def on_server_join(server):
    await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), f'```diff\n+ Joined {server.name} ```' + f'(ID: {server.id})')
    general = find(lambda x: x.name == 'general',  server.channels)
    if general and general.permissions_for(server.me).send_messages:
        await client.send_message(general, '**Greetings!**\nI am Tonk, a MPA organization bot for PSO2! Please type **!gettingstarted** to set my functions up!')
    # await client.send_message(client.get_channel(server.default_channel.id), '**Greetings!**\nI am Tonk, a MPA organization bot for PSO2! Please type **!gettingstarted** to set my functions up!')
@client.event
async def on_server_remove(server):
    await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), f'```diff\n- Left {server.name} ```'.format(server.name) + f'(ID: {server.id})')
    

@client.event
async def on_resumed():
    connectedServers = 0
    print ('Tonk has resumed from a disconnect.')
    for item in client.servers:
        connectedServers += 1
    resumeRole = discord.utils.get(client.get_server(serverIDDict['Bloop']).roles, id='405620919541694464')
    await client.send_message(client.get_channel(OtherIDDict['ControlPanel']), f'Tonk has {resumeRole.mention}' + '\nConnected to **' + str(connectedServers) + '** servers')
    
client.run('Mjk2MTM1NTE1NTM3OTMyMjg4.C7t1mg.ubVijZ2bCHeahPqYWg4H-7wOpAY')