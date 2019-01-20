import discord
import asyncio
import urllib.request
import aiohttp
import traceback
import sys
import json
import os
import urllib.parse
import re
import datetime
from datetime import datetime,tzinfo,timedelta
from random import randint
from io import BytesIO, StringIO
 
class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name
 
class FakeMember():
    def __init__(self, name):
        self.name = name
 
class PlaceHolder():
    def __init__(self, name):
        self.name = name
 
decisionbotid = '290999071592677376' #decisionbot
ITid = '296135515537932288'#Replace this string with your own ID.
EQDict = {}
IDDict = {}
EQTest = {}
SubDict = {}
EQPostDict = {}
appended = False
EST = Zone(-5,False,'EST') #Based on what timezone the majority of your team is in, you can change the format of the EST object.
JST = Zone(9,False,'JST')
date = ''
strCheck = ''
entireNotice = ''
messages = 3
output = ''
guestEnabled = False
client = discord.Client()

def is_bot(m):
	return m.author == client.user
	
    
 
getTime = datetime.now()

# Changes the currently playing status
@client.event
@asyncio.coroutine
def status_change():
    yield from client.change_presence(game=discord.Game(name='just tonk things'))

@asyncio.coroutine
def generateList(message, inputstring):
    pCount = 1
    nCount = 1
    sCount = 1
    mpaCount = 1
    #playerlist = '**Meeting in**: Block 222 Frankas Cafe \nUse **!addme** to sign up \nUse **!removeme** to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.\n'
    playerlist = '\n'
    for member in EQTest[message.channel.name]:
        if nCount == 1:
            playerlist += ('\n**Participant List** ' + '\n')
            mpaCount += 1
        playerlist += (str(nCount) + ". " + member.name + '\n')
        pCount+=1
        nCount+=1
        if nCount == 13:
            playerlist += ('\n')
            nCount = 1
       
    while pCount < 13:
        if nCount == 1:
            playerlist += ('\n**Participant List** ' + str(mpaCount) + '\n')
            mpaCount += 1
        playerlist += (str(nCount) + ".\n")
        pCount+=1
        nCount +=1
        if nCount == 13:
            playerlist += ('\n')
            nCount = 1

    if len(SubDict[message.channel.name]) > 0:
        playerlist += ('\n**Reserve List**:\n')
        for member in SubDict[message.channel.name]:
            playerlist += (str(sCount) + ". " + member.name + '\n')
            sCount += 1  
    try:
        yield from client.edit_message(EQPostDict[message.channel.name], playerlist + inputstring)
    except:
        print('Starting an MPA...')
        EQPostDict[message.channel.name] = yield from client.send_message(message.channel, playerlist + inputstring)
		

#PVP version
@asyncio.coroutine
def generatePVPList(message, inputstring):
    pCount = 1
    nCount = 1
    sCount = 1
    mpaCount = 1
    playerlist = '**PVP match list**:\n'
    for member in EQTest[message.channel.name]:
        if nCount == 1:
            playerlist += ('Team ' + str(mpaCount) + '\n')
            mpaCount += 1
        playerlist += (str(nCount) + ". " + member.name + '\n')
        pCount+=1
        nCount+=1
        if nCount == 7:
            playerlist += ('\n')
            nCount = 1
       
    while pCount < 13:
        if nCount == 1:
            playerlist += ('Party ' + str(mpaCount) + '\n')
            mpaCount += 1
        playerlist += (str(nCount) + ".\n")
        pCount+=1
        nCount +=1
        if nCount == 7:
            playerlist += ('\n')
            nCount = 1

    if len(SubDict[message.channel.name]) > 0:
        playerlist += ('\n**Reserve List**:\n')
        for member in SubDict[message.channel.name]:
            playerlist += (str(sCount) + ". " + member.name + '\n')
            sCount += 1  
    try:
        yield from client.edit_message(EQPostDict[message.channel.name], playerlist + inputstring)
    except:
        print('posting first list')
        EQPostDict[message.channel.name] = yield from client.send_message(message.channel, playerlist + inputstring)
   
#EQ parser method
#def find_between( s, first, last ):
#    try:
#        start = s.index( first ) + len( first )
#        end = s.index( last, start )
#        return s[start:end]
#    except ValueError:
#        return ""

#EQ parser method. Goes into flyergo's website and parses out the latest EQ that is updated there.

#@asyncio.coroutine
#def findEQ2():
#    global strCheck
#    global entireNotice
#    yield from client.wait_until_ready()
#    date = ('*' + str(datetime.now(EST).strftime('%H:%M %Z')) + '\n' + str(datetime.now(JST).strftime('%H:%M %Z')) + '*')
#    servers = list(client.servers)
#    channel = servers[0]
#    
#    print("default channel set to announcement. check other channels pls")
#    for x in client.get_all_channels():
#        print("Checking " + x.name)
#        if x.name == 'bot_notifications':
#            channel = x
#            print("Set announcementChannel successfully to " + x.name)
#            break
#        
#    while not client.is_closed:
#        url = 'http://pso2emq.flyergo.eu/api/v2'
#        req = urllib.request.Request(url)
#        resp = urllib.request.urlopen(req)
#        respData = resp.read()
#
#        date = ('*' + str(datetime.now(EST).strftime('%H:%M %Z')) + '\n' + str(datetime.now(JST).strftime('%H:%M %Z')) + '*')
#        timeOfNotice = find_between(str(respData), 'text":"', '\\n')
#        timeOfNotice = timeOfNotice.replace('\\', '')
#        entireNotice = find_between(str(respData), '[ ', '"}')
#
#        if 'Ship01:' in entireNotice:
#            entireNotice = find_between(entireNotice, 'Ship02', 'Ship03')
#            entireNotice = entireNotice.replace('\\n', '')
#            entireNotice = entireNotice.replace('\\', '\n')
#            entireNotice = timeOfNotice + '\nShip02' + entireNotice
#
#            if '\nShip02: -' in entireNotice:
#                if strCheck != entireNotice:
#                    noEQStr = '\nThere is no EQ going on in Ship02 at the given hour.'
#                    noEQStr = timeOfNotice + noEQStr
#                    yield from client.send_message(channel, str(date) + '\n' + noEQStr)
#                    print(str(date) + '\n' + noEQStr)
#                    strCheck = entireNotice
#            elif strCheck != entireNotice:
#                yield from client.send_message(channel, '@everyone\n' + str(date) + '\n' + entireNotice)
#                print('@everyone\n' + str(date) + entireNotice)
#                strCheck = entireNotice
#        else:
#            entireNotice = entireNotice.replace('\\n', '')
#            entireNotice = entireNotice.replace('\\', '\n')
#            entireNotice = "[ " + entireNotice
#            if strCheck !=  entireNotice:
#                yield from client.send_message(channel, '@everyone\n' + str(date) + '\n' + entireNotice)
#                print('@everyone\n' + str(date) + entireNotice)
#                strCheck = entireNotice
#        yield from asyncio.sleep(300) # task runs every 300 seconds/5 minutes
            
#@client.event
#@asyncio.coroutine
#def on_ready():
#    print('Logged in as')
#    print(client.user.name)
#    print(client.user.id)
#    print('------')

 
@client.event
@asyncio.coroutine
##  GENERAL COMMANDS ##
def on_message(message):
    global appended
    global guestEnabled
    if message.content.startswith('!'):
		#Debugging commands
        if message.content.lower() == '!gettime':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, getTime)
        elif message.content.lower() == '!supertest':
            yield from client.send_message(message.channel, 'Respond at ' + str(getTime))
        elif message.content.lower() == '!supertestagain':
            yield from client.send_message(message.channel, 'I am working.')
        elif message.content.lower() == '!gethighestrole':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, message.author.top_role)
        elif message.content.lower() == '!amiguest':
            if not message.channel.name.startswith('mpa'):
                isGuest = False
                for index in range(len(message.author.roles)):
                    if message.author.roles[index].name == 'Guests':
                        isGuest = True
                yield from client.send_message(message.channel, isGuest)
        elif message.content.lower() == '!listroles':
            if not message.channel.name.startswith('mpa'):
                for index in range(len(message.author.roles)):
                    if len(message.author.roles) == 0:
                        yield from client.send_message(message.channel, 'You either dont have a role, or this command is bugged.')
                    else:
                        yield from client.send_message(message.channel, message.author.roles[index])
                else:
                    yield from client.send_message(message.channel, 'No permissions!')
        elif message.content.lower() == '!numberroles':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, len(message.author.roles))
        elif message.content.lower() == '!checkmpamanagerperm':
            if not message.channel.name.startswith('mpa'):
                doIHavePermission = message.author.top_role.permissions.manage_emojis
                if doIHavePermission:
                    yield from client.send_message(message.channel, 'You have the permissions to start an MPA.')
                else:
                    yield from client.send_message(message.channel, 'You do not have the permission to start an MPA. Take a hike.')
        elif message.content.lower() == '!serverinfo':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, 'Server Name: ' + message.server.name + '\nServer ID: ' + message.server.id)
        elif message.content.lower().startswith('!testarg'):
            userstr = ''
            if not message.channel.name.startswith('mpa'):
                userstr = message.content
                userstr = userstr.replace("!testarg", "")
                userstr = userstr.replace(" ", " ")
                yield from client.send_message(message.channel, 'Responding with: ' + userstr)
        elif message.content.lower() == '!!shutdown':
            if message.author.id == '153273725666590720':
                yield from client.send_message(message.channel, 'SHUTTING ME DOWN? FINE I SEE HOW IT IS.')
                yield from client.logout()
            else:
                yield from client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
        ## MPA TRACKER COMMANDS ##
        #Starts the MPA on the current eq channel. Places the channel name into a dictionary and sets it to be a list. Then fills the list up with 12 placeholder objects.
               
        elif message.content.lower() == '!startmpa':
            print ('Starting MPA on ' + message.author.server.name)
            if message.channel.name.startswith('mpa'):
                yield from client.delete_message(message)
                if not message.channel.name in EQTest:
                   # if message.author.roles[1].permissions.manage_channels:
                    if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                        EQTest[message.channel.name] = list()
                        SubDict[message.channel.name] = list()
                        for index in range(12):
                            EQTest[message.channel.name].append(PlaceHolder(""))
                        if message.server.id == '159184581830901761':
                            em = discord.Embed(description='**Meeting in**: Block *SOMEONETELLMEWHATBLOCKYOUGUYSMEETINPLS* Frankas Cafe \nUse `!addme` to sign up \nUse `!removeme` to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.', colour=0x0099FF)
                        else:
                            em = discord.Embed(description='**Meeting in**: Block 222 Frankas Cafe \nUse `!addme` to sign up \nUse `!removeme` to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.', colour=0xFF66FF)
                        em.set_author(name='An MPA is starting!')
                        yield from client.send_message(message.channel, '', embed=em)
                        yield from generateList(message, 'Starting MPA. Please use `!addme` to sign up!')
                    else:
                        yield from client.send_message(message.channel, 'No.')
                else:
                    yield from generateList(message, 'There is already an MPA to keep track of in this channel.')
            else:
                yield from client.send_message(message.channel, 'You are unable to start a MPA on a non-EQ channel')
           
           
        elif message.content.lower() == '!openmpa':
            if message.server.id == '159184581830901761':
                yield from client.send_message(message.channel, 'This command is only available to Laplace. If you want this please contact Tenj.')
            else:
                if message.channel.name.startswith('mpa'):
                    if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                        if guestEnabled == True:
                            yield from client.send_message(message.channel, 'This MPA is already open!')
                        else:
                            guestEnabled = True
                            for index in range(len(message.server.roles)):
                                if (message.server.roles[index].id == '224757670823985152'):
                                    yield from client.send_message(message.channel, '{} can now join in the MPA!'.format(message.server.roles[index].mention))
        elif message.content.lower() == '!closempa':
            if message.server.id == '159184581830901761':
                yield from client.send_message(message.channel, 'This command is only available to Laplace. If you want this please contact Tenj.')
            else:
                if message.channel.name.startswith('mpa'):
                    if message.author.top_role.permissions.manage_emojis:
                        if guestEnabled == False:
                            yield from client.send_message(message.channel, 'This MPA is already closed!')
                        else:
                            guestEnabled = False
                            yield from client.send_message(message.channel, 'Closed MPA to Members only.')
		#Starts a PVP organization. Has the same function as the MPA organizer.
		
        elif message.content.lower() == '!startpvp':
            if message.channel.name.startswith('pvp'):
                yield from client.delete_message(message)
                if not message.channel.name in EQTest:
                    if message.author.roles[1].permissions.manage_channels or message.author.id == '153273725666590720':
                        EQTest[message.channel.name] = list()
                        SubDict[message.channel.name] = list()
                        for index in range(12):
                            EQTest[message.channel.name].append(PlaceHolder(""))
                        yield from generatePVPList(message, 'Starting an Organized PVP match! Use **!addmepvp** to sign up!')
                    else:
                        yield from client.send_message(message.channel, 'You are not a manager.')
                else:
                    yield from generatePVPList(message, 'There is already an PVP list to keep track of in this channel.')
            else:
                yield from client.send_message(message.channel, 'You are unable to start a PVP match on a non-pvp channel.')
     
        #Removes the MPA on the current eq channel. USE THIS TO CLOSE YOUR CHANNELS SO YOUR MEMORY SPACE ISN'T HOGGED UP BY THIS TINY PROGRAM.
                                 
        elif message.content.lower() == '!removempa':
            if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                if message.channel.name.startswith('mpa'):
                    if message.channel.name in EQTest:
                        try:
                            del EQTest[message.channel.name]
                            ##yield from client.send_message(message.channel, 'MPA {} is deleted.'.format(message.channel.name))
                            #yield from client.purge_from(message.channel, limit=10, check=is_bot)
                            yield from client.purge_from(message.channel, limit=100, after=getTime)
                            guestEnabled = False
                        except KeyError:
                            pass
                    else:
                        yield from client.send_message(message.channel, 'There is no existing MPA to delete.')
                else:
                    yield from client.send_message(message.channel, 'There is no existing MPA to delete in a non EQ channel.')
            else:
                yield from generateList(message, 'You are not a manager.')
                   
		#Same thing as the MPA one above, only this time for pvp.
	 
        elif message.content.lower() == '!removepvp':
            if message.author.roles[1].permissions.manage_channels or message.author.id == '153273725666590720':
                if message.channel.name.startswith('pvp'):
                    if message.channel.name in EQTest:
                        try:
                            del EQTest[message.channel.name]
                            ##yield from client.send_message(message.channel, 'PVP {} is deleted.'.format(message.channel.name))
                            yield from client.purge_from(message.channel, limit=15, after=getTime)
                        except KeyError:
                            pass
                    else:
                        yield from client.send_message(message.channel, 'There is no existing PVP match to delete.')
                else:
                    yield from client.send_message(message.channel, 'There is no existing PVP match to delete in a non PVP channel.')
            else:
                yield from generateList(message, 'You are not a manager.')
                   
            #Adds a player into the MPA list on the current eq channel. Checks for a placeholder object to remove and inserts the user's user object into the list.
        elif message.content.lower() == '!addme':
            bypassCheck = False
            if message.channel.name.startswith('mpa'):
                for index in range(len(message.author.roles)):
                    #if (message.author.roles[index] == 'Members' or message.author.roles[index] == 'Senior Members' or message.author.top_role.permissions.manage_channels or message.server.id == '159184581830901761'):
                    if message.author.roles[index].id == '154465245488742400':
                        bypassCheck = True
                    elif message.author.roles[index].id == '277639714717302793':
                        bypassCheck = True
                    elif message.author.top_role.permissions.manage_emojis:
                        bypassCheck = True
                    elif message.server.id == '159184581830901761':
                        bypassCheck = True
                if (bypassCheck == False and guestEnabled == False):
                    yield from generateList(message, '*Guests are not allowed to join this MPA.*')
                else:
                    if message.channel.name in EQTest:
                        for member in EQTest[message.channel.name]:
                            if isinstance(member, PlaceHolder):
                                if not(message.author in EQTest[message.channel.name]):
                                    if message.author.id == message.server.owner.id:
                                        EQTest[message.channel.name].pop(0)
                                        EQTest[message.channel.name].insert(0, message.author)
                                        yield from generateList(message, '*Added Lord {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    # elif message.author.roles[1].permissions.manage_channels:
                                        # if isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            # EQTest[message.channel.name].pop(4)
                                            # EQTest[message.channel.name].insert(4, message.author)
                                            # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            # appended = True
                                            # break
                                        # elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            # EQTest[message.channel.name].pop(8)
                                            # EQTest[message.channel.name].insert(8, message.author)
                                            # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            # appended = True
                                            # break
                                        # else:
                                            # if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                                # EQTest[message.channel.name].pop(1)
                                                # EQTest[message.channel.name].insert(1, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                            # elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                                # EQTest[message.channel.name].pop(2)
                                                # EQTest[message.channel.name].insert(2, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                            # elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                                # EQTest[message.channel.name].pop(3)
                                                # EQTest[message.channel.name].insert(3, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                            # elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                                # EQTest[message.channel.name].pop(5)
                                                # EQTest[message.channel.name].insert(5, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                            # elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                                # EQTest[message.channel.name].pop(6)
                                                # EQTest[message.channel.name].insert(6, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                            # elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                                # EQTest[message.channel.name].pop(7)
                                                # EQTest[message.channel.name].insert(7, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                            # elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                                # EQTest[message.channel.name].pop(9)
                                                # EQTest[message.channel.name].insert(9, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                            # elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                                # EQTest[message.channel.name].pop(10)
                                                # EQTest[message.channel.name].insert(10, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                            # elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                                # EQTest[message.channel.name].pop(11)
                                                # EQTest[message.channel.name].insert(11, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                            # elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                                # EQTest[message.channel.name].pop(0)
                                                # EQTest[message.channel.name].insert(0, message.author)
                                                # yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                                # appended = True
                                                # break
                                    else:
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                           # EQTest[message.channel.name].insert(1, message.author)
                                            EQTest[message.channel.name].insert(1, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name].insert(4, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name].insert(8, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, message.author)
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, message.author)
                                            yield from generateList(message, '*{} farted. I put him to top.*'.format(message.author.name))
                                            appended = True
                                            break
                                else:
                                    yield from generateList(message, "*You are already in the MPA*")
                                    break
                        if not appended:
                            if not(message.author in EQTest[message.channel.name]): 
                                yield from generateList(message, "*The MPA is full. Adding to reserve list.*")
                                if not(message.author in SubDict[message.channel.name]):
                                    SubDict[message.channel.name].append(message.author)
                                    yield from generateList(message, '*Added {} to the Reserve list*'.format(message.author.name))
                                else:
                                    yield from generateList(message, "*You are already in the Reserve List*")
                            else:
                                yield from generateList(message, "*You are already in the MPA*")
                        appended = False                                
                    else:
                        yield from client.send_message(message.channel, 'A manager did not start the MPA yet')
                yield from client.delete_message(message)
            else:
                yield from client.delete_message(message)

		#Literally the same thing as above. Only for pvp.
        elif message.content.lower() == '!addmepvp':
            if message.channel.name.startswith('pvp'):
                if message.channel.name in EQTest:
                    for member in EQTest[message.channel.name]:
                        if isinstance(member, PlaceHolder):
                            if not(message.author in EQTest[message.channel.name]):
                                if message.author.id == message.server.owner.id:
                                    EQTest[message.channel.name].pop(0)
                                    EQTest[message.channel.name].insert(0, message.author)
                                    yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                    appended = True
                                    break
     
                                elif message.author.roles[1].permissions.manage_channels:
                                    if isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                        EQTest[message.channel.name].pop(4)
                                        EQTest[message.channel.name].insert(4, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                        EQTest[message.channel.name].pop(8)
                                        EQTest[message.channel.name].insert(8, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    else:
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                            EQTest[message.channel.name].insert(1, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, message.author)
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                            appended = True
                                            break
                                else:
                                    if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                        EQTest[message.channel.name].pop(1)
                                        EQTest[message.channel.name].insert(1, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                        EQTest[message.channel.name].pop(2)
                                        EQTest[message.channel.name].insert(2, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                        EQTest[message.channel.name].pop(3)
                                        EQTest[message.channel.name].insert(3, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                        EQTest[message.channel.name].pop(5)
                                        EQTest[message.channel.name].insert(5, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                        EQTest[message.channel.name].pop(6)
                                        EQTest[message.channel.name].insert(6, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                        EQTest[message.channel.name].pop(7)
                                        EQTest[message.channel.name].insert(7, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                        EQTest[message.channel.name].pop(9)
                                        EQTest[message.channel.name].insert(9, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                        EQTest[message.channel.name].pop(10)
                                        EQTest[message.channel.name].insert(10, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                        EQTest[message.channel.name].pop(11)
                                        EQTest[message.channel.name].insert(11, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                        EQTest[message.channel.name].pop(4)
                                        EQTest[message.channel.name].insert(4, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                        EQTest[message.channel.name].pop(8)
                                        EQTest[message.channel.name].insert(8, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                        EQTest[message.channel.name].pop(0)
                                        EQTest[message.channel.name].insert(0, message.author)
                                        yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(message.author.name))
                                        appended = True
                                        break
                            else:
                                yield from generatePVPList(message, "*You are already in this match.*")
                                break
                    if not appended:
                        if not(message.author in EQTest[message.channel.name]): 
                            yield from generatePVPList(message, "*The PVP match is full. Adding to reserve list.*")
                            if not(message.author in SubDict[message.channel.name]):
                                SubDict[message.channel.name].append(message.author)
                                yield from generatePVPList(message, '*Added {} to the Reserve list*'.format(message.author.name))
                            else:
                                yield from generatePVPList(message, "*You are already in the Reserve List*")
                        else:
                            yield from generatePVPList(message, "*You are already in this match.*")
                    appended = False                                
                else:
                    yield from client.send_message(message.channel, 'A manager did not start the PVP list yet')
            else:
                yield from client.delete_message(message)
               
        #Adds a string/name of a player that the Manager wants into the MPA list.      
        elif message.content.lower().startswith('!add'):
            if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                userstr = ''
                if message.channel.name.startswith('mpa'):
                    if message.channel.name in EQTest:
                        userstr = message.content
                        userstr = userstr.replace("!add", "")
                        userstr = userstr.replace(" ", "")
                        if userstr == "":
                            yield from generateList(message, "You can't add nobody. Are you drunk?")
                            appended = True
                        else:
                            for member in EQTest[message.channel.name]:
                                if isinstance(member, PlaceHolder):
                                    if not(userstr in EQTest[message.channel.name]):
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                            EQTest[message.channel.name].insert(1, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name].insert(8, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name].insert(4, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, FakeMember(userstr))
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                        if not appended:
                            yield from generateList(message, "*The MPA is full. Adding to reserve list.*")
                            SubDict[message.channel.name].append(FakeMember(userstr))
                            yield from generateList(message, '*Added {} to the Reserve list*'.format(userstr))
                    else:
                        yield from client.send_message(message.channel, 'There is no MPA.')
                    yield from client.delete_message(message)
                else:
                    yield from client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
            else:
                yield from client.send_message(message.channel, "You don't have permissions to use this command")
            appended = False

			
		#PVP Version
        #Adds a string/name of a player that the Manager wants into the MPA list.      
        elif message.content.lower().startswith('!pvpadd'):
            if message.author.roles[1].permissions.manage_channels or message.author.id == '153273725666590720':
                userstr = ''
                if message.channel.name.startswith('pvp'):
                    if message.channel.name in EQTest:
                        userstr = message.content
                        userstr = userstr.replace("!add", "")
                        userstr = userstr.replace(" ", "")
                        if userstr == "":
                            yield from generatePVPList(message, "You can't add nobody. Are you drunk?")
                            appended = True
                        else:
                            for member in EQTest[message.channel.name]:
                                if isinstance(member, PlaceHolder):
                                    if not(userstr in EQTest[message.channel.name]):
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                            EQTest[message.channel.name].insert(1, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name].insert(8, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name].insert(4, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, FakeMember(userstr))
                                            yield from generatePVPList(message, '*Added {} to the PVP match list*'.format(userstr))
                                            appended = True
                                            break
                        if not appended:
                            yield from generatePVPList(message, "*The PVP match is full. Adding to reserve list.*")
                            SubDict[message.channel.name].append(FakeMember(userstr))
                            yield from generatePVPList(message, '*Added {} to the Reserve list*'.format(userstr))
                    else:
                        yield from client.send_message(message.channel, 'There is no match.')
                else:
                    yield from client.send_message(message.channel, 'There is nothing to remove in a non-pvp channel.')
            else:
                yield from client.send_message(message.channel, "You don't have permissions to use this command")
            appended = False
     
        #Removes the user object from the MPA list.
        elif message.content.lower() == '!removeme':
                if message.channel.name.startswith('mpa'):
                    if message.channel.name in EQTest:
                        if (message.author in EQTest[message.channel.name]):
                            index = EQTest[message.channel.name].index(message.author)
                            EQTest[message.channel.name].pop(index)
                            EQTest[message.channel.name].insert(index, PlaceHolder(''))
                            yield from generateList(message, '*Removed {} from the MPA list*'.format(message.author.name))
                            yield from client.delete_message(message)
                            if len(SubDict[message.channel.name]) > 0:
                                EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                yield from generateList(message, '*Removed {} from the MPA list and added {}*'.format(message.author.name, EQTest[message.channel.name][index].name))
                        elif (message.author in SubDict[message.channel.name]):
                            SubDict[message.channel.name].remove(message.author)
                            yield from generateList(message, '*Removed {} from the Reserve list*'.format(message.author.name))
                        else:
                         yield from generateList(message, 'You were not in the MPA list in the first place.')


		#PVP Version of above command
		        #Removes the user object from the MPA list.
        elif message.content.lower() == '!removemepvp':
                if message.channel.name.startswith('pvp'):
                    if message.channel.name in EQTest:
                        if (message.author in EQTest[message.channel.name]):
                            index = EQTest[message.channel.name].index(message.author)
                            EQTest[message.channel.name].pop(index)
                            EQTest[message.channel.name].insert(index, PlaceHolder(''))
                            yield from generatePVPList(message, '*Removed {} from the PVP match list*'.format(message.author.name))
                            if len(SubDict[message.channel.name]) > 0:
                                EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                yield from generatePVPList(message, '*Removed {} from the PVP match list and added {}*'.format(message.author.name, EQTest[message.channel.name][index].name))
                        elif (message.author in SubDict[message.channel.name]):
                            SubDict[message.channel.name].remove(message.author)
                            yield from generatePVPList(message, '*Removed {} from the Reserve list*'.format(message.author.name))
                        else:
                         yield from generatePVPList(message, 'You were not in the PVP match list in the first place.')
     
        #Removes the player object that matches the input string that is given.
        elif message.content.lower().startswith('!remove'):
            if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                if message.channel.name.startswith('mpa'):
                    if message.channel.name in EQTest:
                        if len(EQTest[message.channel.name]):
                                userstr = message.content
                                userstr = userstr.replace("!remove ", "")
                                for index in range(len(EQTest[message.channel.name])):
                                    appended = False
                                    if userstr == EQTest[message.channel.name][index].name:
                                        EQTest[message.channel.name][index] = userstr
                                        EQTest[message.channel.name].remove(userstr)
                                        EQTest[message.channel.name].insert(index, PlaceHolder(''))
                                        userstr = userstr
                                        yield from generateList(message, '*Removed {} from the MPA list*'.format(userstr))
                                        if len(SubDict[message.channel.name]) > 0:
                                            EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                            yield from generateList(message, '*Removed {} from the MPA list and added {}*'.format(userstr, EQTest[message.channel.name][index].name))
                                        appended = True
                                        break
                                if not appended:
                                    for index in range(len(SubDict[message.channel.name])):
                                        appended = False
                                        if userstr == SubDict[message.channel.name][index].name:
                                            SubDict[message.channel.name][index] = userstr
                                            SubDict[message.channel.name].remove(userstr)
                                            userstr = userstr
                                            yield from generateList(message, '*Removed {} from the Reserve list*'.format(userstr))
                                            appended = True
                                            break
                                if not appended:    
                                    yield from generateList(message, "Player {} does not exist in the MPA list".format(userstr))
                        else:
                            yield from client.send_message(message.channel, "There are no players in the MPA.")
                    else:
                        yield from client.send_message(message.channel, 'There is no MPA.')
                    yield from client.delete_message(message)
                else:
                    yield from client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
            else:
                yield from generateList(message, "You don't have permissions to use this command")
		
		#PVP Version
        elif message.content.lower().startswith('!pvpremove '):
            if message.author.roles[1].permissions.manage_channels or message.author.id == '153273725666590720':
                if message.channel.name.startswith('pvp'):
                    if message.channel.name in EQTest:
                        if len(EQTest[message.channel.name]):
                                userstr = message.content
                                userstr = userstr.replace("!remove ", "")
                                for index in range(len(EQTest[message.channel.name])):
                                    appended = False
                                    if userstr == EQTest[message.channel.name][index].name:
                                        EQTest[message.channel.name][index] = userstr
                                        EQTest[message.channel.name].remove(userstr)
                                        EQTest[message.channel.name].insert(index, PlaceHolder(''))
                                        userstr = userstr
                                        yield from generatePVPList(message, '*Removed {} from the PVP match list*'.format(userstr))
                                        if len(SubDict[message.channel.name]) > 0:
                                            EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                            yield from generatePVPList(message, '*Removed {} from the PVP match list and added {}*'.format(userstr, EQTest[message.channel.name][index].name))
                                        appended = True
                                        break
                                if not appended:
                                    for index in range(len(SubDict[message.channel.name])):
                                        appended = False
                                        if userstr == SubDict[message.channel.name][index].name:
                                            SubDict[message.channel.name][index] = userstr
                                            SubDict[message.channel.name].remove(userstr)
                                            userstr = userstr
                                            yield from generatePVPList(message, '*Removed {} from the Reserve list*'.format(userstr))
                                            appended = True
                                            break
                                if not appended:    
                                    yield from generatePVPList(message, "Player {} does not exist in the PVP match list".format(userstr))
                        else:
                            yield from client.send_message(message.channel, "There are no players in the PVP match.")
                    else:
                        yield from client.send_message(message.channel, 'There is no match.')
                else:
                    yield from client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
            else:
                yield from generatePVPList(message, "You don't have permissions to use this command")
            #Laplace Specific Commands
        if message.server.id == '153346891109761024':
            if message.content.lower() == '!elisu':
                if not message.channel.name.startswith('mpa'):
                    randomNumber = randint(0, 1)
                    if (randomNumber == 0):
                        yield from client.send_message(message.channel, 'Who is your waifu and why is it Elisu?')
                    elif (randomNumber == 1):
                        yield from client.send_message(message.channel, 'Who is your Elisu and why is it waifu?')
            elif message.content.lower() == '!kamui':
                if not message.channel.name.startswith('mpa'):
                    if message.author.id == '191977376039567371':
                        randomNumber = randint(0, 2)
                        if (randomNumber == 0):
                            yield from client.send_message(message.channel, 'I would make a witty comment right here for you mom, but I find myself too lazy to.')
                        elif (randomNumber == 1):
                            yield from client.send_message(message.channel, 'Send a return saying WAAAAAAAAAAAAT? Never! You can\'t tell me what to do!')
                        elif (randomNumber == 2):
                            yield from client.send_message(message.channel, 'I, Tonk, don\'t think you are waifu material mom! TRA- *shot*')
                    randomNumber = randint(0, 1)
                    if (randomNumber == 0):
                        yield from client.send_message(message.channel, 'WAAAAAAAAAAAAT')
                    elif (randomNumber == 1):
                        yield from client.send_message(message.channel, ':eyes:')
                    
            elif message.content.lower() == '!bob':
                if not message.channel.name.startswith('mpa'):
                    yield from client.send_message(message.channel, 'Don\'t be a bob. What is a bob? We don\'t know, but just don\'t be a bob.')
            
            elif message.content.lower() == '!theface':
                if not message.channel.name.startswith('mpa'):
                    randomNumber = randint(0, 3)
                    if (randomNumber == 0):
                        yield from client.send_message(message.channel, '⎛　　　　●　　ω　　●　 ⎞')
                    elif (randomNumber == 1):
                        yield from client.send_message(message.channel, '*⎛　　　　●　　ω　　●　 ⎞*')
                    elif (randomNumber == 2):
                        yield from client.send_message(message.channel, '**⎛　　　　●　　ω　　●　 ⎞**')
                    elif (randomNumber == 3):
                        yield from client.send_message(message.channel, '⎛　　●　　ω　　●　　　 ⎞')
                        

            elif message.content.lower() == '!massdestruction':
                if not message.channel.name.startswith('mpa'):
                    yield from client.send_message(message.channel, 'BABY BABY BABY BABY BABY BABY BBABY BABY BABY BABY BABY BABY')

            elif message.content.lower() == '!dog':
                if not message.channel.name.startswith('mpa'):
                    randomNumber = randInt(0, 4)
                    if randomNumber == 0:
                        yield from client.send_message(message.channel, 'A rare doggo! https://66.media.tumblr.com/988f4137285d758d567e73a27dd6d944/tumblr_nuuvidOKcH1uzkruwo1_500.jpg')
                    elif randomNumber == 1:
                        yield from client.send_message(message.channel, 'A rare doggo! https://cdn.discordapp.com/attachments/219826145825128458/301944176142974976/dog_4.jpg')
                    elif randomNumber == 2:
                        randomNumberTwo = randint(0, 1)
                        if randomNumberTwo == 0:
                           yield from client.send_message(message.channel, 'You expected me to bark or a doggo picture didn\'t you? But not today!')
                        else:
                           yield from client.send_message(message.channel, 'A rare doggo! https://cdn.discordapp.com/attachments/219826145825128458/301944457287434240/dog_5.jpg')
                    elif randomNumber == 3:
                        yield from client.send_message(message.channel, 'A rare doggo! https://cdn.discordapp.com/attachments/219826145825128458/301944731338801152/doge_corgi.jpg')
                    elif randomNumber == 4:
                        yield from client.send_message(message.channel, 'A rare doggo! https://cdn.discordapp.com/attachments/219826145825128458/301944890290470912/doge_ritual.jpg')
                    else:
                        yield from client.send_message(message.channel, 'A rare doggo! https://66.media.tumblr.com/988f4137285d758d567e73a27dd6d944/tumblr_nuuvidOKcH1uzkruwo1_500.jpg')
                    
            elif message.content.lower() == '!thicc':
                if not message.channel.name.startswith('mpa'):
                    yield from client.send_message(message.channel, 'Lolis are better than thicc. Don\'t let anyone tell you otherwise.')
            elif message.content.lower() == '!cynthia':
                if not message.channel.name.startswith('mpa'):
                    yield from client.send_message(message.channel, '*Flailing intensifies*')
        #End Laplace Specific Command List        
        #Global Commands
        if message.content.lower() == ('!help'):
            if not message.channel.name.startswith('mpa'):
                em = discord.Embed(description='Greetings! I am a majestic bot that mainly organizes the team MPAs \nMy following commands are:\n**!addme** - register yourself to the MPA. If the MPA is full, you will be automatically placed into the reserve list.\n**!removeme** - Removes yourself from the MPA. \n**!addmepvp** - Register yourself for a PVP match. Only works in the PVP channel. \n**!removemepvp** - Removes yourself from the PVP match. Only works in the PVP channel. \nUnless the commands are for the PVP channel, these will only work for the MPA organization channel. If you have any questions, please ask Tenj!', colour=0xB3ECFF)
                em.set_author(name='All Tonk Commands!', icon_url=client.user.avatar_url)
                yield from client.send_message(message.channel, embed=em)
                #yield from client.send_message(message.channel, 'Hello {}'.format(message.author.mention) + '\nI am a majestic bot that mainly organizes the team MPAs! \nMy following commands are:\n**!addme** - register yourself to the MPA. If the MPA is full, you will be automatically placed into the reserve list.\n**!removeme** - Removes yourself from the MPA. \n**!addmepvp** - Register yourself for a PVP match. Only works in the PVP channel. \n**!removemepvp** - Removes yourself from the PVP match. Only works in the PVP channel. \nUnless the commands are for the PVP channel, these will only work for the MPA organization channel. If you have any questions, please ask Tenj!')

        elif message.content.lower() == '!techhelp':
            if not message.channel.name.startswith('mpa'):
                em = discord.Embed(description='\nHidden Commands: \n**!startmpa** - Starts a team MPA. This is useable ONLY in a channel that begins with "mpa". You cannot have more than one mpa at a time in one channel. \n**!removempa** - Closes the mpa to prevent further sign ups and allows for another MPA to be started. \n**!startpvp** - Starts an organized team pvp match. Only useable in a channel that begins with "pvp". \n**!removepvp** - Same as !removempa, but for PVP channels. \n**!add <playername>** - Adds a name to the MPA list. \n**!remove <playername>** - Removes a name from the MPA list \n**!pvpadd <playername>** - PVP version of !add \n**!pvpremove <playername>** - PVP version of !remove \n**!openmpa** Opens the MPA up to Guests to join. Laplace only. \n**!closempa** - Closes MPAs to Members and above only. Laplace only. \nAny further questions should go to Tenj. Find the other hidden commands if you can...', colour=0xB3ECFF)
                em.set_author(name='All Tonk Hidden Commands!', icon_url=client.user.avatar_url)
                yield from client.send_message(message.channel, embed=em)
                #yield from client.send_message(message.channel, '{} \nHidden Commands: \n**!startmpa** - Starts a team MPA. This is useable ONLY in a channel that begins with "mpa". You cannot have more than one mpa at a time in one channel. \n**!removempa** - Closes the mpa to prevent further sign ups and allows for another MPA to be started. \n**!startpvp** - Starts an organized team pvp match. Only useable in a channel that begins with "pvp". \n**!removepvp** - Same as !removempa, but for PVP channels. \n**!add <playername>** - Adds a name to the MPA list. \n**!remove <playername>** - Removes a name from the MPA list \n**!pvpadd <playername>** - PVP version of !add \n**!pvpremove <playername>** - PVP version of !remove \nAny further questions should go to Tenj.'.format(message.author.mention))				

        elif message.content.lower() == '!hello':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, 'Hello {}.'.format(message.author.mention))
     
        elif message.content.lower() == '!test':
            if not message.channel.name.startswith('mpa'):
                randomNumber = randint(0, 17)
                if (randomNumber == 0):
                    yield from client.send_message(message.channel, 'At this point, you should just give up me, {}.'.format(message.author.mention))
                elif (randomNumber == 1):
                    yield from client.send_message(message.channel, 'You rang, {}?'.format(message.author.mention))
                elif (randomNumber == 2):
                    yield from client.send_message(message.channel, 'Please now take the time to look to the right {}. There is a wall.'.format(message.author.mention))
                elif (randomNumber == 3):
                    yield from client.send_message(message.channel, 'Did you know these responses were probably written at 3AM, {}?'.format(message.author.mention))
                elif (randomNumber == 4):
                    yield from client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know a pineapple is actually a bunch of small berries fused together in a single mass?'.format(message.author.mention))
                elif (randomNumber == 5):
                    yield from client.send_message(message.channel, 'I am working, {}. Somewhere in the world, someone else typed this same command.'.format(message.author.mention))
                elif (randomNumber == 6):
                    yield from client.send_message(message.channel, 'Reading this text probably isn\'t the best use of your time, {}.'.format(message.author.mention))
                elif (randomNumber == 7):
                    yield from client.send_message(message.channel, 'Girls are now praying. Please wait warmly and have some tea, {}.'.format(message.author.mention))
                elif (randomNumber == 8):
                    yield from client.send_message(message.channel, 'If you ask me what brand is the best for toothpaste, it would probably be Colgate, {}.'.format(message.author.mention))
                elif (randomNumber == 9):
                    yield from client.send_message(message.channel, 'I am thou. Thou art pie. But this is no social link, {}.'.format(message.author.mention))
                elif (randomNumber == 10):
                    yield from client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know the word **Underground** is the only word in english that begins with \'und and ends with \'und?'.format(message.author.mention))
                elif (randomNumber == 11):
                    yield from client.send_message(message.channel, 'It has always been a dream of mine to see a bear playing a lute. Isn\'t it the same for you, {}?'.format(message.author.mention))
                elif (randomNumber == 12):
                    yield from client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know that hippopotomonstrosesquipedaliophobia is the fear of long words?'.format(message.author.mention))
                elif (randomNumber == 13):
                    yield from client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know when Joseph Gayetty invented toilet paper in 1857, he had his name printed on each sheet?.'.format(message.author.mention))
                elif (randomNumber == 14):
                    yield from client.send_message(message.channel, 'Secret command found! Now find the others. I trust that it will be a much bigger challenge, {}.'.format(message.author.mention))
                elif (randomNumber == 15):
                    yield from client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know that bald eagles have around 7000-7200 feathers in total? That totally screams freedom!'.format(message.author.mention))
                elif (randomNumber == 16):
                    yield from client.send_message(message.channel, 'Are you being entertained by this useless information, {}?'.format(message.author.mention))
                elif (randomNumber == 17):
                    yield from client.send_message(message.channel, 'I have traveled to many places, but at the end of the day, there is no place like 127.0.0.1, {}.'.format(message.author.mention))
                else:
                    yield from client.send_message(message.channel, 'I am working, but this command is not.')
				
        elif message.content.lower() == '!pah':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, 'GTFO PAH\nT\nF\nO\n\nP\nA\nH')
				
        elif message.content.lower() == '!tink':
            if not message.channel.name.startswith('mpa'):
                randomNumber = randint(0, 1)
                if (randomNumber == 0):
                    yield from client.send_message(message.channel, '"I never die." - Tink\n http://imgur.com/a/FW4X5')
                elif (randomNumber == 1):
                    yield from client.send_message(message.channel, '*"PSO2 will never have PVP!"* - Tink 2016' )
        elif message.content.lower() == '!tenj':
            if not message.channel.name.startswith('mpa'):
                if message.author.id == '153273725666590720':
                    yield from client.send_message(message.channel, 'The one and only.')
                else:
                    yield from client.send_message(message.channel, 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        elif message.content.lower() == '!neweq':
            if not message.channel.name.startswith('mpa'):
                yield from client.send_message(message.channel, 'https://cdn.discordapp.com/attachments/142483459196190720/294317457408000001/Cryycordinanutshell.png')
		#End Global Commands
        #Ishana Specific Commands
        if message.server.id == '159184581830901761':
            if message.content.lower() == '!yuiko':
                if not message.channel.name.startswith('mpa'):
                    randomNumber = randint(0, 8)
                    if (randomNumber == 0):
                        yield from client.send_message(message.channel, 'You mean Steve.')
                    elif (randomNumber == 1):
                        yield from client.send_message(message.channel, 'You mean Bill.')
                    elif (randomNumber == 2):
                        yield from client.send_message(message.channel, 'You mean Sam.')
                    elif (randomNumber == 3):
                        yield from client.send_message(message.channel, 'You mean Ryan.')
                    elif (randomNumber == 4):
                        yield from client.send_message(message.channel, 'You mean Jake, from State Farm.')
                    elif (randomNumber == 5):
                        yield from client.send_message(message.channel, 'You mean Hank. Hank needs help.')
                    elif (randomNumber == 6):
                        yield from client.send_message(message.channel, 'You mean Daniel')
                    elif (randomNumber == 7):
                        yield from client.send_message(message.channel, 'You mean Louis.')
                    elif (randomNumber == 8):
                        yield from client.send_message(message.channel, 'You mean a not so rare doggo')
        #End Ishana Specific Commands
#        if message.channel.name.startswith('mpa'):
#            if message.author.id != decisionbotid:
#                if message.content.lower() != '!removempa':
#                    yield from client.delete_message(message)
#        
#        if message.channel.name.startswith('pvp'):
#            if message.author.id != decisionbotid:
#                if message.content.lower() != '!removepvp':
#                    yield from client.delete_message(message)
 
# @client.event
# @asyncio.coroutine
# Automiatically starts an MPA the moment the EQ channel is created.
# def on_channel_create(channel):
    # if channel.name.startswith('mpa'):
        # yield from client.send_message(channel, '!startmpa')

@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print ('Logged in to servers:')
    for item in client.servers:
        print (item)
    print('------')
    yield from client.change_presence(game=discord.Game(name='just tonk things'))


#client.loop.create_task(findEQ2())
#client.run('ruckerus@gmail.com', 'forlordluo1')
client.run('Mjk2MTM1NTE1NTM3OTMyMjg4.C7t1mg.ubVijZ2bCHeahPqYWg4H-7wOpAY')
