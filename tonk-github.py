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


class FakeMember():
    def __init__(self, name):
        self.name = name
 
class PlaceHolder():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name)

        
print ('Logging into Discord...\n')
start = time.time()
EQTest = {}
SubDict = {}
guestEnabled = {}
EQPostDict = {}
MPACount = 0
participantCount = {}
eightMan = {}
roleAdded = {}
totalPeople = {}
appended = False
client = discord.Client()
ActiveMPA = list()
r_url = re.compile(r"^http?:")
r_image = re.compile(r".*\.(jpg|png|gif)$")


# This bot relies on Discord Emojis to properly function. Apply your custom emoji IDs here to fit the list and special arguements
# You can get the emoji ID by putting a \ before the emoji itself to get the ID.

# Show when there is no class on the player, also default for an inactive slot too.
NO_CLASS = ''

# Shows when there is no player on this slot in the list.
INACTIVE_SLOT = ''

# Class Emojis
HUNTER = ''
FIGHTER = ''
RANGER = ''
GUNNER = ''
FORCE = ''
TECHER = ''
BOUNCER = ''
BRAVER = ''
SUMMONER = ''
HERO = ''

# Your ID should go here to allow use of Administrator commands
OWNER_ID = ''

# Block or place you want the MPA to meet at. You can put anything here, really
MEETING_SPOT = ''

def is_bot(m):
	return m.author == client.user
    
def is_not_bot(m):
    return m.author != client.user
def is_pinned(m):
    return m.pinned != True
    
getTime = datetime.now()

# This function creates a list based on the information given from the commands used.
@asyncio.coroutine
def generateList(message, inputstring):
    global MPACount
    global HUNTER
    global FIGHTER
    global RANGER
    global FORCE
    global TECHER
    global SUMMONER
    global BOUNCER
    global BRAVER
    global HERO
    global NO_CLASS
    global INACTIVE_SLOT
    global MEETING_SPOT
    pCount = 1
    nCount = 1
    sCount = 1
    mpaCount = 1
    alreadyWroteList = False
    mpaFriendly = ''
    classlist = '\n'
    playerlist = '\n'
    splitstr = ''
    for word in EQTest[message.channel.id]: 
        if (type(word) is PlaceHolder):
            playerlist += (INACTIVE_SLOT + '\n')
            classlist += (NO_CLASS + '\n')
        else:
            splitstr = word.split()
            classRole = splitstr[0]
            if not classRole.startswith('<'):
                classRole = NO_CLASS
                player = splitstr[0]
                if len(splitstr) > 2:
                    for index in range(len(splitstr)):
                        if index == 0 or index == 1:
                            pass
                        else:
                            player+= ' ' + splitstr[index]
            else:
                player = splitstr[1]
                if len(splitstr) > 2:
                    for index in range(len(splitstr)):
                        if index == 0 or index == 1:
                            pass
                        else:
                            player+= ' ' + splitstr[index]
            playerlist += (ACTIVE_SLOT + ' ' + player + '\n')
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
            
            
            
    if guestEnabled[message.channel.id] == True:
        mpaFriendly = 'Yes'
    else:
        mpaFriendly = 'No'
        
                
    em = discord.Embed(description='Use `!addme` to sign up \nOptionally you can add your class after addme. Example. `!addme br` \nUse `!removeme` to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.', colour=0x0099FF)
    em.add_field(name='Meeting at', value='`' + MEETING_SPOT + '`', inline=True)
    em.add_field(name='Party Status', value='`' + str(participantCount[message.channel.id]) + '/' + str(totalPeople[message.channel.id]) + '`', inline=True)
    em.add_field(name='MPA Open?', value='`' + mpaFriendly + '`', inline=False)
    em.add_field(name='Participant List', value=playerlist, inline=True)
    em.add_field(name='Class', value=classlist, inline=True)
    em.add_field(name='Last Action', value=inputstring, inline=False)
    em.set_author(name='An MPA is starting!', icon_url=message.server.icon_url)
        
    try:
        yield from client.edit_message(EQPostDict[message.channel.id], '', embed=em)
    except:
        print(message.author.name + ' Started an MPA on ' + message.server.name)
        MPACount += 1
        print('Amount of Active MPAs: ' + str(MPACount))
        EQPostDict[message.channel.id] = yield from client.send_message(message.channel, '', embed=em)

 
@client.event
@asyncio.coroutine
##  GENERAL COMMANDS ##
def on_message(message):
    global appended
    global MPACount
    global ActiveMPA
    global HUNTER
    global FIGHTER
    global RANGER
    global FORCE
    global TECHER
    global SUMMONER
    global BOUNCER
    global BRAVER
    global HERO
    global OWNER_ID
    global NO_CLASS
    if message.content.startswith('!'):
		#Debugging commands
        if message.content.lower() == '!supertest':
            yield from client.send_message(message.channel, 'Respond at ' + str(getTime))
        elif message.content.lower() == '!gethighestrole':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, message.author.top_role)
        elif message.content.lower() == '!listroles':
            if not message.channel.name.startswith('mpa'):
                for index in range(len(message.author.roles)):
                    if len(message.author.roles) == 0:
                        yield from client.send_message(message.channel, 'You either dont have a role, or this command is bugged.')
                    else:
                        yield from client.send_message(message.channel, message.author.roles[index])
                else:
                    yield from client.send_message(message.channel, 'No permissions!')
        elif message.content.lower().startswith('!quickclean '):
            if message.author.top_role.permissions.manage_channels or message.author.id == OWNER_ID:
                userstr = message.content
                userstr = userstr.replace("!quickclean", "")
                userstr = userstr.replace(" ", "")
                toClean = int(userstr) + 1
                yield from client.purge_from(message.channel, limit=toClean)
            else:
                yield from client.send_message(message.channel, 'You lack the permissions to do this.')
        elif message.content.lower() == '!numberroles':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, len(message.author.roles))
        elif message.content.lower() == '!checkmpamanagerperm':
            if not message.channel.name.startswith('mpa'):
                doIHavePermission = message.author.top_role.permissions.manage_emojis
                if doIHavePermission:
                    yield from client.send_message(message.channel, 'You have the permissions to start an MPA.')
                else:
                    yield from client.send_message(message.channel, 'You do not have the permission to start an MPA.')
        # Purges everything that isn't made by the bot.
        elif message.content.lower() == '!clearchannel':
            if message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.id == OWNER_ID:
                    yield from client.purge_from(message.channel, limit=100, after=getTime, check=is_not_bot)
                else:
                    yield from client.send_message(message.channel, 'You lack the permissions to use this command.')
            else:
                yield from client.send_message(message.channel, 'This command can only be used in a MPA channel.')
        # These commands are for Me (Tenj), or whoever runs this bot. 
        elif message.content.lower() == '!!shutdown':
            if message.author.id == OWNER_ID:
                yield from client.send_message(message.channel, 'Shutting down...')
                yield from client.logout()
            else:
                yield from client.send_message(message.channel, 'You lack the permissions to use this command!')
        elif message.content.lower() == '!!listservers':
            serverlist = ''
            if message.author.id == OWNER_ID:
                for item in client.servers:
                    serverlist += (item.name + '\nID: ' + item.id + '\n')
                em = discord.Embed(description=serverlist, colour=0x0099FF)
                em.set_author(name='Joined Servers')
                yield from client.send_message(message.channel, '', embed=em)
            else:
                yield from client.send_message(message.channel, 'You lack the permissions to use this command!') 
        elif message.content.lower() == '!!restart':
            if message.author.id == OWNER_ID:
                yield from client.send_message(message.channel, 'Tonk will now restart!')
                print ('The restart command was issued! Restarting Bot...')
                yield from client.change_presence(game=discord.Game(name='Restarting...'), status=discord.Status.idle)
                os.execl(sys.executable, *([sys.executable]+sys.argv))
            else:
                yield from client.send_message(message.channel, 'You lack the permissions to use this command!')
        elif message.content.lower() == '!!clearconsole':
            if message.author.id == OWNER_ID:
                yield from client.send_message(message.channel, 'Clearing Console')
                os.system('cls' if os.name == 'nt' else 'clear')
            else:
                yield from client.send_message(message.channel, 'You lack the permissions to use this command!')
        elif message.content.lower().startswith('!eval'):
            if message.author.id == OWNER_ID:
                userstr = message.content
                userstr = userstr.replace("!eval", "")
                try:
                    result = eval(userstr)
                except Exception:
                    formatted_lines = traceback.format_exc().splitlines()
                    yield from client.send_message(message.channel, 'Failed to Evaluate.\n```py\n{}\n{}\n```'.format(formatted_lines[-1], '/n'.join(formatted_lines[4:-1])))
                    return

                if asyncio.iscoroutine(result):
                    result = yield from result

                if result:
                    yield from client.send_message(message.channel, 'Evaluated Successfully.\n```{}```'.format(result))
                    return
            else:
                yield from client.send_message(message.channel, 'No.')
        ## MPA TRACKER COMMANDS ##
        #Starts the MPA on the current eq channel. Places the channel name into a dictionary and sets it to be a list. Then fills the list up with 12 placeholder objects.
               
        elif message.content.lower().startswith('!startmpa'):
            userstr = message.content
            userstr = userstr.replace("!startmpa", "")
            userstr2 = ''
            if message.channel.name.startswith('mpa'):
                if userstr == ' busterquest':
                    userstr2 = 'Buster Quest'
                else:
                    userstr2 = userstr
                yield from client.send_message(message.channel, '{}'.format(message.server.roles[0]) + ' {}'.format(userstr2))
                if userstr == ' 8man' or userstr == ' pvp' or userstr == ' busterquest':
                    eightMan[message.channel.id] = True
                else:
                    eightMan[message.channel.id] = False
                try:
                    yield from client.delete_message(message)
                except discord.Forbidden:
                    print (message.author.name + ' Tried to start an MPA at {}, but failed.'.format(message.server.name))
                    yield from client.send_message(message.author, 'I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                    return
                if not message.channel.id in EQTest:
                    if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator:
                        try:
                            EQTest[message.channel.id] = list()
                            SubDict[message.channel.id] = list()
                            ActiveMPA.append(message.channel.id)
                            roleAdded[message.channel.id] = False
                            guestEnabled[message.channel.id] = False
                            participantCount[message.channel.id] = 0
                            if eightMan[message.channel.id] == True:
                                for index in range(8):
                                    EQTest[message.channel.id].append(PlaceHolder(""))
                                totalPeople[message.channel.id] = 8
                            else:
                                for index in range(12):
                                    EQTest[message.channel.id].append(PlaceHolder(""))
                                totalPeople[message.channel.id] = 12
                            yield from generateList(message, '```dsconfig\nStarting MPA. Please use !addme to sign up!```')
                        except discord.Forbidden:
                            print (message.author.name + 'Tried to start an MPA at {}, but failed.'.format(message.server.name))
                            yield from client.send_message(message.author, 'I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                            return

                    else:
                        yield from client.send_message(message.channel, 'You do not have the permission to do that, starfox.')
                else:
                    yield from generateList(message, '```fix\nThere is already an MPA being made here!```')
            else:
                yield from client.send_message(message.channel, 'You can only start a MPA on a MPA channel!')
        # Shows the current list of the MPA called in the channel.   
        elif message.content.lower() == '!currentmpa':
            if message.channel.name.startswith('mpa'):
                nCount = 1
                mpaList = ''
                yield from client.send_message(message.channel, '**Current MPA List**')
                for index, item in enumerate(EQTest[message.channel.id]):
                    if (type(EQTest[message.channel.id][index]) is PlaceHolder):
                        pass
                    else:
                        mpaList += (str(nCount) + ". " + item + '\n')
                        nCount+=1
                if nCount == 1:
                    yield from client.send_message(message.channel, 'There is no MPA!')
                else:
                    em = discord.Embed(description=mpaList, colour=0x0099FF)
                    em.set_author(name='Current MPA')
                    yield from client.send_message(message.channel, '', embed=em)
            else:
                yield from client.send_message(message.channel, 'This isn\'t an MPA Channel!')
        # Opens the MPA to any role to the server if there is a lock enabled for the server.        
        elif message.content.lower() == '!openmpa':
            if message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator:
                    if guestEnabled[message.channel.id] == True:
                        yield from client.send_message(message.channel, 'This MPA is already open!')
                    else:
                        guestEnabled[message.channel.id] = True
                        for index in range(len(message.server.roles)):
                            yield from client.send_message(message.channel, 'Opened MPA to non-members!')
                            yield from generateList(message, '```fix\nMPA is now open to non-members.```')
                            break
        # Closes the MPA to a specific amount of roles in the server only.                         
        elif message.content.lower() == '!closempa':
            if message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator:
                    if guestEnabled[message.channel.id] == False:
                        yield from client.send_message(message.channel, 'This MPA is already closed!')
                    else:
                        guestEnabled[message.channel.id] = False
                        yield from client.send_message(message.channel, 'Closed MPA to Members only.')
                        yield from generateList(message, '```fix\nMPA is now closed to non-members```')
                else:
                    yield from client.send_message(message.channel, 'You do not have the permission to do this.')
     
        # Removes the current MPA on the channel and cleans the channel up for the next one. Use this when the MPA is finished so the bot doesn't go insane on next MPA create.
                                 
        elif message.content.lower() == '!removempa':
            if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator or message.author.id == client.user.id:
                if message.channel.name.startswith('mpa'):
                    if message.channel.id in EQTest:
                        try:
                            yield from client.delete_message(message)
                            del EQTest[message.channel.id]
                            MPACount -= 1
                            print(message.author.name + ' Closed an MPA on ' + message.server.name)
                            print('Amount of Active MPAs: ' + str(MPACount))
                            if eightMan[message.channel.id] == True:
                                eightMan[message.channel.id] = False
                            yield from client.purge_from(message.channel, limit=100, after=getTime)
                            participantCount[message.channel.id] = 0
                            index = ActiveMPA.index(message.channel.id)
                            ActiveMPA.pop(index)
                        except KeyError:
                            pass
                    else:
                        yield from client.send_message(message.channel, 'There is no MPA to remove!')
                else:
                    yield from client.send_message(message.channel, 'This command can only be used in a MPA channel!')
            else:
                yield from generateList(message, '```fix\nYou are not a manager.```')
                   
        # Adds the user into the EQ list in the EQ channel. Optionally takes a class as an arguement. If one is passed, add the class icon and the user's name into the EQ list.
        elif message.content.lower().startswith('!addme'):
            bypassCheck = False
            userstr = ''
            classRole = ''
            index = 0
            personInMPA = False
            personInReserve = False
            roleAdded[message.channel.id] = False
            if message.channel.name.startswith('mpa') or message.author.top_role.permissions.administrator:
                for index in range(len(message.author.roles)):
                    if message.author.roles[index].id == MEMBER_ROLE:
                        bypassCheck = True
                        break
                    elif message.author.top_role.permissions.manage_emojis:
                        bypassCheck = True
                        break                    
                    elif message.author.top_role.permissions.administrator:
                        bypassCheck = True
                        break
                if (bypassCheck == False and guestEnabled[message.channel.id] == False):
                    yield from generateList(message, '```fix\nGuests are not allowed to join this MPA.```')
                    yield from client.delete_message(message)
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
                        if userstr.lower() == 'hu' or userstr.lower() == 'hunter':
                            classRole = HUNTER
                        elif userstr.lower() == 'fi' or userstr.lower() == 'fighter':
                            classRole = FIGHTER
                        elif userstr.lower() == 'ra' or userstr.lower() == 'ranger':
                            classRole = RANGER
                        elif userstr.lower() == 'gu' or userstr.lower() == 'gunner':
                            classRole = GUNNER
                        elif userstr.lower() == 'fo' or userstr.lower() == 'force':
                            classRole = FORCE
                        elif userstr.lower() == 'te' or userstr.lower() == 'techer':
                            classRole = TECHER
                        elif userstr.lower() == 'bo' or userstr.lower() == 'bouncer':
                            classRole = BOUNCER
                        elif userstr.lower() == 'br' or userstr.lower() == 'braver':
                            classRole = BRAVER
                        elif userstr.lower() == 'su' or userstr.lower() == 'summoner':
                            classRole = SUMMONER
                        elif userstr.lower() == 'hr' or userstr.lower() == 'hero':
                            classRole = HERO
                        else:
                            classRole = NO_CLASS
                        elif userstr == 'reserve':
                            if personInMPA == False: 
                                yield from generateList(message, "```fix\nReserve list requested. Adding...```")
                                yield from client.delete_message(message)
                                if personInReserve == False:
                                    SubDict[message.channel.id].append(message.author.name)
                                    yield from generateList(message, '```diff\n+ Added {} to the Reserve list```'.format(message.author.name))
                                else:
                                    yield from generateList(message, "```diff\n+ You are already in the Reserve List```")
                            else:
                                yield from generateList(message, "```fix\nYou are already in the MPA```")
                            return
                        yield from client.delete_message(message)
                        for word in EQTest[message.channel.id]:
                            if isinstance(word, PlaceHolder):
                                if personInMPA == False:
                                    if message.author.id == message.server.owner.id:
                                        EQTest[message.channel.id].pop(0)
                                        EQTest[message.channel.id].insert(0, classRole + ' ' + message.author.name)
                                        participantCount[message.channel.id] += 1
                                        yield from generateList(message, '```diff\n+ Added Lord {} to the MPA list```'.format(message.author.name))
                                        appended = True
                                        break
                                    elif (message.author.name in SubDict[message.channel.id]):
                                        index = SubDict[message.channel.id].index(message.author.name)
                                        if isinstance(EQTest[message.channel.id][1], PlaceHolder):
                                            EQTest[message.channel.id].pop(1)
                                            EQTest[message.channel.id][1] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][2], PlaceHolder):
                                            EQTest[message.channel.id].pop(2)
                                            EQTest[message.channel.id][2] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][3], PlaceHolder):
                                            EQTest[message.channel.id].pop(3)
                                            EQTest[message.channel.id][3] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][4], PlaceHolder):
                                            EQTest[message.channel.id].pop(4)
                                            EQTest[message.channel.id][4] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][5], PlaceHolder):
                                            EQTest[message.channel.id].pop(5)
                                            EQTest[message.channel.id][5] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][6], PlaceHolder):
                                            EQTest[message.channel.id].pop(6)
                                            EQTest[message.channel.id][6] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][7], PlaceHolder):
                                            EQTest[message.channel.id].pop(7)
                                            EQTest[message.channel.id][7] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                            appended = True
                                            break
                                        if eightMan[message.channel.id] == False:
                                            if isinstance(EQTest[message.channel.id][8], PlaceHolder):
                                                EQTest[message.channel.id].pop(8)
                                                EQTest[message.channel.id][8] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][9], PlaceHolder):
                                                EQTest[message.channel.id].pop(9)
                                                EQTest[message.channel.id][9] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][10], PlaceHolder):
                                                EQTest[message.channel.id].pop(10)
                                                EQTest[message.channel.id][10] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][11], PlaceHolder):
                                                EQTest[message.channel.id].pop(11)
                                                EQTest[message.channel.id][11] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][0], PlaceHolder):
                                                EQTest[message.channel.id].pop(0)
                                                EQTest[message.channel.id][0] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                                appended = True
                                                break
                                        elif isinstance(EQTest[message.channel.id][0], PlaceHolder):
                                            EQTest[message.channel.id].pop(0)
                                            EQTest[message.channel.id][0] = classRole + ' ' + SubDict[message.channel.id].pop(index) 
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} from the reserves to the MPA list.```'.format(message.author.name))
                                            appended = True
                                            break
                                    else:
                                        if isinstance(EQTest[message.channel.id][1], PlaceHolder):
                                            EQTest[message.channel.id].pop(1)
                                            EQTest[message.channel.id].insert(1, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][2], PlaceHolder):
                                            EQTest[message.channel.id].pop(2)
                                            EQTest[message.channel.id].insert(2, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][3], PlaceHolder):
                                            EQTest[message.channel.id].pop(3)
                                            EQTest[message.channel.id].insert(3, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][4], PlaceHolder):
                                            EQTest[message.channel.id].pop(4)
                                            EQTest[message.channel.id].insert(4, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][5], PlaceHolder):
                                            EQTest[message.channel.id].pop(5)
                                            EQTest[message.channel.id].insert(5, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][6], PlaceHolder):
                                            EQTest[message.channel.id].pop(6)
                                            EQTest[message.channel.id].insert(6, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][7], PlaceHolder):
                                            EQTest[message.channel.id].pop(7)
                                            EQTest[message.channel.id].insert(7, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                            appended = True
                                            break
                                        if eightMan[message.channel.id] == False:
                                            if isinstance(EQTest[message.channel.id][8], PlaceHolder):
                                                EQTest[message.channel.id].pop(8)
                                                EQTest[message.channel.id].insert(8, classRole + ' ' + message.author.name)
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][9], PlaceHolder):
                                                EQTest[message.channel.id].pop(9)
                                                EQTest[message.channel.id].insert(9, classRole + ' ' + message.author.name)
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][10], PlaceHolder):
                                                EQTest[message.channel.id].pop(10)
                                                EQTest[message.channel.id].insert(10, classRole + ' ' + message.author.name)
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][11], PlaceHolder):
                                                EQTest[message.channel.id].pop(11)
                                                EQTest[message.channel.id].insert(11, classRole + ' ' + message.author.name)
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][0], PlaceHolder):
                                                EQTest[message.channel.id].pop(0)
                                                EQTest[message.channel.id].insert(0, message.author.name)
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(message.author.name))
                                                appended = True
                                                break
                                        elif isinstance(EQTest[message.channel.id][0], PlaceHolder):
                                            EQTest[message.channel.id].pop(0)
                                            EQTest[message.channel.id].insert(0, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```css\n{} farted. I put him to top.```'.format(message.author.name))
                                            appended = True
                                            break
                                else:
                                    yield from generateList(message, "```fix\nYou are already in the MPA```")
                                    break
                        if not appended:
                            if personInMPA == False: 
                                yield from generateList(message, "```css\nThe MPA is full. Adding to reserve list.```")
                                if personInReserve == False:
                                    SubDict[message.channel.id].append(message.author.name)
                                    yield from generateList(message, '```diff\n+ Added {} to the Reserve list```'.format(message.author.name))
                                else:
                                    yield from generateList(message, "```css\nYou are already in the Reserve List```")
                            else:
                                yield from generateList(message, "```css\nYou are already in the MPA```")
                        appended = False                                
                    else:
                        yield from client.send_message(message.channel, 'There is no MPA to add yourself to!')
            else:
                yield from client.delete_message(message)
                            
        # Adds a string/name of a player that the Manager wants into the MPA list. Can also take a class role as well.
        elif message.content.lower().startswith('!add '):
            if message.author.top_role.permissions.manage_emojis or message.author.id == OWNER_ID or message.author.top_role.permissions.administrator:
                userstr = ''
                classRole = ''
                if message.channel.name.startswith('mpa'):
                    if message.channel.id in EQTest:
                        userstr = message.content
                        userstr = userstr.replace("!add ", "")
                        if userstr == "":
                            yield from generateList(message, "```fix\nYou can't add nobody.```")
                            appended = True
                        else:
                            splitstr = userstr.split()
                            if len(splitstr) == 2:
                                if splitstr[1].lower() == 'hu' or splitstr[1].lower() == 'hunter':
                                    classRole = HUNTER
                                elif splitstr[1].lower() == 'fi' or splitstr[1].lower() == 'fighter':
                                    classRole = FIGHTER
                                elif splitstr[1].lower() == 'ra' or splitstr[1].lower() == 'ranger':
                                    classRole = RANGER
                                elif splitstr[1].lower() == 'gu' or splitstr[1].lower() == 'gunner':
                                    classRole = GUNNER
                                elif splitstr[1].lower() == 'fo' or splitstr[1].lower() == 'force':
                                    classRole = FORCE
                                elif splitstr[1].lower() == 'te' or splitstr[1].lower() == 'techer':
                                    classRole = TECHER
                                elif splitstr[1].lower() == 'bo' or splitstr[1].lower() == 'bouncer':
                                    classRole = BOUNCER
                                elif splitstr[1].lower() == 'br' or splitstr[1].lower() == 'braver':
                                    classRole = BRAVER
                                elif splitstr[1].lower() == 'su' or splitstr[1].lower() == 'summoner':
                                    classRole = SUMMONER
                                elif splitstr[1].lower() == 'hr' or splitstr[1].lower() == 'hero':
                                    classRole = HERO
                            else:
                                classRole = NO_CLASS
                            for word in EQTest[message.channel.id]:
                                if isinstance(word, PlaceHolder):
                                    if not(str(splitstr[0]) in EQTest[message.channel.id]):
                                        if isinstance(EQTest[message.channel.id][1], PlaceHolder):
                                            EQTest[message.channel.id].pop(1)
                                            EQTest[message.channel.id].insert(1, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][2], PlaceHolder):
                                            EQTest[message.channel.id].pop(2)
                                            EQTest[message.channel.id].insert(2, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][3], PlaceHolder):
                                            EQTest[message.channel.id].pop(3)
                                            EQTest[message.channel.id].insert(3, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][4], PlaceHolder):
                                            EQTest[message.channel.id].pop(4)
                                            EQTest[message.channel.id].insert(4, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][5], PlaceHolder):
                                            EQTest[message.channel.id].pop(5)
                                            EQTest[message.channel.id].insert(5, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][6], PlaceHolder):
                                            EQTest[message.channel.id].pop(6)
                                            EQTest[message.channel.id].insert(6, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.id][7], PlaceHolder):
                                            EQTest[message.channel.id].pop(7)
                                            EQTest[message.channel.id].insert(7, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                            appended = True
                                            break
                                        if eightMan[message.channel.id] == False:    
                                            if isinstance(EQTest[message.channel.id][8], PlaceHolder):
                                                EQTest[message.channel.id].pop(8)
                                                EQTest[message.channel.id].insert(8, classRole + ' ' + splitstr[0])
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][9], PlaceHolder):
                                                EQTest[message.channel.id].pop(9)
                                                EQTest[message.channel.id].insert(9, classRole + ' ' + splitstr[0])
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][10], PlaceHolder):
                                                EQTest[message.channel.id].pop(10)
                                                EQTest[message.channel.id].insert(10, classRole + ' ' + splitstr[0])
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][11], PlaceHolder):
                                                EQTest[message.channel.id].pop(11)
                                                EQTest[message.channel.id].insert(11, classRole + ' ' + splitstr[0])
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                                appended = True
                                                break
                                            elif isinstance(EQTest[message.channel.id][0], PlaceHolder):
                                                EQTest[message.channel.id].pop(0)
                                                EQTest[message.channel.id].insert(0, classRole + ' ' + splitstr[0])
                                                participantCount[message.channel.id] += 1
                                                yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                                appended = True
                                                break
                                        elif isinstance(EQTest[message.channel.id][0], PlaceHolder):
                                            EQTest[message.channel.id].pop(0)
                                            EQTest[message.channel.id].insert(0, classRole + ' ' + splitstr[0])
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n+ Added {} to the MPA list```'.format(splitstr[0]))
                                            appended = True
                                            break
                        if not appended:
                            yield from generateList(message, "```css\nThe MPA is full. Adding to reserve list.```")
                            SubDict[message.channel.id].append(userstr)
                            yield from generateList(message, '```diff\n+ Added {} to the Reserve list```'.format(userstr))
                    else:
                        yield from client.send_message(message.channel, 'There is no MPA.')
                    yield from client.delete_message(message)
                else:
                    yield from client.send_message(message.channel, 'This command can only be used in a MPA channel!')
            else:
                yield from client.send_message(message.channel, "You don't have permissions to use this command")
            appended = False
        #Removes the user name from the MPA list.
        elif message.content.lower() == '!removeme':
            inMPA = False
            if message.channel.name.startswith('mpa'):
                if message.channel.id in EQTest:
                    yield from client.delete_message(message)
                    for index, item in enumerate(EQTest[message.channel.id]):
                        if (type(EQTest[message.channel.id][index]) is PlaceHolder):
                            pass
                        elif message.author.name in item:
                            EQTest[message.channel.id].pop(index)
                            EQTest[message.channel.id].insert(index, PlaceHolder(''))
                            participantCount[message.channel.id] -= 1
                            yield from generateList(message, '```diff\n- Removed {} from the MPA list```'.format(message.author.name))
                            if len(SubDict[message.channel.id]) > 0:
                                EQTest[message.channel.id][index] = SubDict[message.channel.id].pop(0)
                                participantCount[message.channel.id] += 1
                                yield from generateList(message, '```diff\n- Removed {} from the MPA list and added {}```'.format(message.author.name, EQTest[message.channel.id][index]))
                            inMPA = True
                            return
                    if inMPA == False:
                        for index, item in enumerate(SubDict[message.channel.id]):
                            if message.author.name in item:
                                SubDict[message.channel.id].pop(index)
                                yield from generateList(message, '```diff\n- Removed {} from the Reserve list```'.format(message.author.name))
                                return
                            else:
                                yield from generateList(message, '```fix\nYou were not in the MPA list in the first place.```')
                        if len(SubDict[message.channel.id]) == 0:
                            yield from generateList(message, '```fix\nYou were not in the MPA list in the first place.```')
        # Allows the player to change their class without altering their position in the MPA list.
        elif message.content.lower().startswith('!changeclass'):
            inMPA = False
            if message.channel.name.startswith('mpa') or message.author.top_role.permissions.administrator:
                if message.channel.id in EQTest:
                    userstr = message.content
                    userstr = userstr.replace("!changeclass", "")
                    userstr = userstr.replace(" ", "")
                    yield from client.delete_message(message)
                    if userstr == 'hu' or userstr == 'hunter':
                        newRole = HUNTER
                        newRoleName = 'Hunter'
                    elif userstr == 'fi' or userstr == 'fighter':
                        newRole = FIGHTER
                        newRoleName = 'Fighter'
                    elif userstr == 'ra' or userstr == 'ranger':
                        newRole = RANGER
                        newRoleName = 'Ranger'
                    elif userstr == 'gu' or userstr == 'gunner':
                        newRole = GUNNER
                        newRoleName = 'Gunner'
                    elif userstr == 'fo' or userstr == 'force':
                        newRole = FORCE
                        newRoleName = 'Force'
                    elif userstr == 'te' or userstr == 'techer':
                        newRole = TECHER
                        newRoleName = 'Techer'
                    elif userstr == 'bo' or userstr == 'bouncer':
                        newRole = BOUNCER
                        newRoleName = 'Bouncer'
                    elif userstr == 'br' or userstr == 'braver':
                        newRole = BRAVER
                        newRoleName = 'Braver'
                    elif userstr == 'su' or userstr == 'summoner':
                        newRole = SUMMONER
                        newRoleName = 'Summoner'
                    elif userstr == 'hr' or userstr == 'hero':
                        newRole = HERO
                        newRoleName = 'Hero'
                    else:
                        newRole = NO_CLASS
                        newRoleName = 'None'
                    for index, item in enumerate(EQTest[message.channel.id]):
                        if (type(EQTest[message.channel.id][index]) is PlaceHolder):
                            pass
                        elif message.author.name in item:
                            EQTest[message.channel.id].pop(index)
                            EQTest[message.channel.id].insert(index, newRole2 + ' ' + message.author.name)
                            yield from generateList(message, '```diff\n+ Changed {}\'s class to '.format(message.author.name) + newRoleName + '```')
                            inMPA = True
                            return
                    if inMPA == False:
                        yield from generateList(message, '```fix\nYou are not in the MPA!```')
        #Removes the player name that matches the input string that is given.
        elif message.content.lower().startswith('!remove'):
            if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator:
                if message.channel.name.startswith('mpa'):
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
                                        yield from generateList(message, '```diff\n- Removed {} from the MPA list```'.format(toBeRemoved))
                                        if len(SubDict[message.channel.id]) > 0:
                                            EQTest[message.channel.id][index] = SubDict[message.channel.id].pop(0)
                                            participantCount[message.channel.id] += 1
                                            yield from generateList(message, '```diff\n- Removed {} from the MPA list and added {}```'.format(toBeRemoved, EQTest[message.channel.id][index]))
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
                                            yield from generateList(message, '```diff\n- Removed {} from the Reserve list```'.format(toBeRemoved))
                                            appended = True
                                            break
                                if not appended:    
                                    yield from generateList(message, "```fix\nPlayer {} does not exist in the MPA list```".format(userstr))
                        else:
                            yield from client.send_message(message.channel, "There are no players in the MPA.")
                    else:
                        yield from client.send_message(message.channel, 'There is no MPA.')
                    yield from client.delete_message(message)
                else:
                    yield from client.send_message(message.channel, 'This command can only be used in a MPA Channel!')
            else:
                yield from generateList(message, "You don't have permissions to use this command")
 ## GENERAL COMMANDS ##               
        #Global Commands
        if message.content.lower() == ('!help'):
            if not message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator:   
                    em = discord.Embed(description='Greetings! I am a majestic bot that mainly organizes the team MPAs! \nMy following commands are:\n**!addme** - register yourself to the MPA. If the MPA is full, you will be automatically placed into the reserve list.\n**!removeme** - Removes yourself from the MPA. \n\n**Manager only commands:** \n**!startmpa** - Starts a team MPA. This is useable ONLY in a channel that begins with "mpa". You cannot have more than one mpa at a time in one channel. \n**!removempa** - Closes the mpa to prevent further sign ups and allows for another MPA to be started. \n**!add <playername>** - Adds a name to the MPA list. \n**!remove <playername>** - Removes a name from the MPA list \n**!ffs** - Cleans everything but the list in a MPA channel. Useful in case conversations start breaking out in the MPA channel.', colour=0xB3ECFF)
     
        elif message.content.lower() == '!test':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, 'I am working.')
@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print ('Logged in to servers:')
    for item in client.servers:
        print (item)
    end = time.time()
    loadupTime = (end - start)
    print ('Tonk is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)))
    print('------')
#Run the bot
client.run('key')