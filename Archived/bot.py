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

        
print ('Logging into Discord...\n')
EQDict = {}
IDDict = {}
EQTest = {}
WBList = {}
TEList = {}
WBCount = {}
TECount = {}
SubDict = {}
EQPostDict = {}
MPACounter = {}
MPACount = 0
participantCount = {}
weakBulletCount = {}
techerCount = {}
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
	
    
#LOAD THE DOGGO MEMES
with open("doggoo.txt") as f:
    yuiMemes = f.readlines()

getTime = datetime.now()


@asyncio.coroutine
def generateList(message, inputstring):
    global MPACount
    pCount = 1
    nCount = 1
    sCount = 1
    mpaCount = 1
    wbCount = 1
    teCount = 1
    #playerlist = '**Meeting in**: Block 222 Frankas Cafe \nUse **!addme** to sign up \nUse **!removeme** to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.\n'
    playerlist = '\n'
 # This is the Ishana format
    if message.server.id == '159184581830901761':
        for member in EQTest[message.channel.name]: 
            if nCount == 1:
                playerlist += ('**Party ' + str(mpaCount) + '**\n')
                mpaCount += 1
            playerlist += (str(nCount) + ". " + member.name + '\n')
            pCount+=1
            nCount+=1
            if nCount == 5:
                playerlist += ('\n')
                nCount = 1
           
        while pCount < 13:
            if nCount == 1:
                playerlist += ('**Party ' + str(mpaCount) + '**\n')
                mpaCount += 1
            playerlist += (str(nCount) + ".\n")
            pCount+=1
            nCount +=1
            if nCount == 5:
                playerlist += ('\n')
                nCount = 1

        if len(SubDict[message.channel.name]) > 0:
            playerlist += ('\n**Reserve List**:\n')
            for member in SubDict[message.channel.name]:
                playerlist += (str(sCount) + ". " + member.name + '\n')
                sCount += 1  
        
        # if len(WBList[message.channel.name]) > 0:
            # playerlist += ('\n**Weakbulleter List**:\n')
            # for member in WBList[message.channel.name]:
                # playerlist += (str(wbCount) + ". " + member.name + '\n')
                # wbCount += 1
                
        # if len(TEList[message.channel.name]) > 0:
            # playerlist += ('\n**Techer List**:\n')
            # for member in TEList[message.channel.name]:
                # playerlist += (str(teCount) + ". " + member.name + '\n')
                # teCount += 1
        try:
            yield from client.edit_message(EQPostDict[message.channel.name], playerlist + inputstring)
            yield from client.edit_message(MPACounter[message.channel.name], '**MPA Status:** ' + str(participantCount[message.channel.name]) + '/12')
            yield from client.edit_message(WBCount[message.channel.name], '**Number of Weakbulleters:** ' + str(weakBulletCount[message.channel.name]))
            yield from client.edit_message(TECount[message.channel.name], '**Number of Techers:** ' + str(techerCount[message.channel.name]))
        except:
            print(message.author.name + ' Started an MPA on Ishana')
            MPACount += 1
            print('Amount of Active MPAs: ' + str(MPACount))
            EQPostDict[message.channel.name] = yield from client.send_message(message.channel, playerlist + inputstring)
            MPACounter[message.channel.name] = yield from client.send_message(message.channel, '**MPA Status:** ' + str(participantCount[message.channel.name]) + '/12')
            WBCount[message.channel.name] = yield from client.send_message(message.channel, '**Number of Weakbulleters:** ' + str(weakBulletCount[message.channel.name]))
            TECount[message.channel.name] = yield from client.send_message(message.channel, '**Number of Techers:** ' + str(techerCount[message.channel.name]))
    # Laplace/Any other place that it may take place in        
    else:
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
                
        if len(WBList[message.channel.name]) > 0:
            playerlist += ('\n**Weakbulleter List**:\n')
            for member in WBList[message.channel.name]:
                playerlist += (str(wbCount) + ". " + member.name + '\n')
                wbCount += 1
                
        if len(TEList[message.channel.name]) > 0:
            playerlist += ('\n**Techer List**:\n')
            for member in TEList[message.channel.name]:
                playerlist += (str(teCount) + ". " + member.name + '\n')
                teCount += 1
        try:
            yield from client.edit_message(EQPostDict[message.channel.name], playerlist + inputstring)
            yield from client.edit_message(MPACounter[message.channel.name], '**MPA Status:** ' + str(participantCount[message.channel.name]) + '/12')
        except:
            print(message.author.name + ' Started an MPA on Laplace')
            MPACount += 1
            print('Amount of Active MPAs: ' + str(MPACount))
            EQPostDict[message.channel.name] = yield from client.send_message(message.channel, playerlist + inputstring)
            MPACounter[message.channel.name] = yield from client.send_message(message.channel, '**MPA Status:** ' + str(participantCount[message.channel.name]) + '/12')
		

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
 
@client.event
@asyncio.coroutine
##  GENERAL COMMANDS ##
def on_message(message):
    global appended
    global guestEnabled
    global MPACount
    global yuiMemes
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
        elif message.content.lower() == '!quickclean 15':
            if message.author.top_role.permissions.manage_channels or message.author.id == '153273725666590720':
                yield from client.purge_from(message.channel, limit=15)
            else:
                yield from client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
        elif message.content.lower() == '!quickclean 30':
            if message.author.top_role.permissions.manage_channels or message.author.id == '153273725666590720':
                yield from client.purge_from(message.channel, limit=30)
            else:
                yield from client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
        elif message.content.lower() == '!quickclean 45':
            if message.author.top_role.permissions.manage_channels or message.author.id == '153273725666590720':
                yield from client.purge_from(message.channel, limit=45)
            else:
                yield from client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
        elif message.content.lower() == '!quickclean 75':
            if message.author.top_role.permissions.manage_channels or message.author.id == '153273725666590720':
                yield from client.purge_from(message.channel, limit=75)
            else:
                yield from client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
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
                if message.server.id == '159184581830901761':
                    yield from client.send_message(message.channel, 'Shutting down. If anything goes wrong during the downtime, please blame yui.')
                else:
                    yield from client.send_message(message.channel, 'DONT DO THIS TO ME MA-')
                yield from client.logout()
            else:
                yield from client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
        ## MPA TRACKER COMMANDS ##
        #Starts the MPA on the current eq channel. Places the channel name into a dictionary and sets it to be a list. Then fills the list up with 12 placeholder objects.
               
        elif message.content.lower().startswith('!startmpa'):
            userstr = message.content
            userstr = userstr.replace("!startmpa", "")
            userstr = userstr.replace(" ", "")
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                if message.server.id == '159184581830901761':
                    if userstr == 'deus':
                        yield from client.send_file(message.channel, 'deus.jpg')
                    elif userstr == 'pd':
                        yield from client.send_file(message.channel, 'PD.jpg')
                    elif userstr == 'magatsu':
                        yield from client.send_file(message.channel, 'Maggy.jpg')
                    elif userstr == 'td3':
                        yield from client.send_file(message.channel, 'MBD3.jpg')
                    elif userstr == 'td4':
                        yield from client.send_file(message.channel, 'MBD4.jpg')
                    elif userstr == 'tdvr':
                        yield from client.send_file(message.channel, 'MBDVR20.jpg')
                    elif userstr == 'mother':
                        yield from client.send_file(message.channel, 'Mother.jpg')
                    elif userstr == 'pi':
                        yield from client.send_file(message.channel, 'PI.jpg')
                    elif userstr == 'trigger':
                        yield from client.send_file(message.channel, 'tRIGGER.jpg')
                    elif userstr == 'yamato':
                        yield from client.send_file(message.channel, 'yamato.jpg')
                yield from client.delete_message(message)
                if not message.channel.name in EQTest:
                   # if message.author.roles[1].permissions.manage_channels:
                    if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                        EQTest[message.channel.name] = list()
                        SubDict[message.channel.name] = list()
                        WBList[message.channel.name] = list()
                        TEList[message.channel.name] = list()
                        weakBulletCount[message.channel.name] = 0
                        techerCount[message.channel.name] = 0
                        participantCount[message.channel.name] = 0
                        for index in range(12):
                            EQTest[message.channel.name].append(PlaceHolder(""))
                        if message.server.id == '159184581830901761':
                            em = discord.Embed(description='**Meeting in**: Block 03 Frankas Cafe \nUse `!addme` to sign up \nUse `!removeme` to remove yourself from the mpa \nUse `!addme reserve` to sign up into the reserve list. \nUse `!addme wb` to add yourself to the weakbullet list.\n Use `!addme te` to add yourself to the techer list. \nIf the MPA list is full, signing up will put you in the reserve list.', colour=0x0099FF)
                        else:
                            em = discord.Embed(description='**Meeting in**: Block 222 Frankas Cafe \nUse `!addme` to sign up \nUse `!removeme` to remove yourself from the mpa \nUse `!addme reserve` to sign up into the reserve list.\nUse `!addme wb` to add yourself to the weakbullet list.\n Use `!addme te` to add yourself to the techer list. \nIf the MPA list is full, signing up will put you in the reserve list.', colour=0xFF66FF)
                        em.set_author(name='An MPA is starting!', icon_url=message.server.icon_url)
                        yield from client.send_message(message.channel, '', embed=em)
                        yield from generateList(message, 'Starting MPA. Please use `!addme` to sign up!')
                    else:
                        yield from client.send_message(message.channel, 'You do not have the permission to do that, starfox.')
                else:
                    yield from generateList(message, 'An MPA is already being organized here!')
            else:
                yield from client.send_message(message.channel, 'This channel does not meet the requirements to start an MPA.')
           
        elif message.content.lower() == '!currentmpa':
            if message.channel.name.startswith('mpa'):
                nCount = 1
                yield from client.send_message(message.channel, '**Current MPA List**')
                for member in EQTest[message.channel.name]:
                    yield from client.send_message(message.channel, str(nCount) + ". " + member.name + '\n')
                    nCount+=1
            else:
                yield from client.send_message(message.channel, 'This isn\'t an MPA Channel!')
                
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
                if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                    if message.channel.name in EQTest:
                        try:
                            del EQTest[message.channel.name]
                            print(message.author.name + ' Closed an MPA on ' + message.server.name)
                            MPACount -= 1
                            print('Amount of Active MPAs: ' + str(MPACount))
                            ##yield from client.send_message(message.channel, 'MPA {} is deleted.'.format(message.channel.name))
                            #yield from client.purge_from(message.channel, limit=10, check=is_bot)
                            if message.channel.id == '206673616060940288':
                                yield from client.purge_from(message.channel, limit=15, check=is_bot)
                                participantCount[message.channel.name] = 0
                            else:
                                yield from client.purge_from(message.channel, limit=30, after=getTime)
                                participantCount[message.channel.name] = 0
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
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
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
                        yield from client.delete_message(message)
                        for member in EQTest[message.channel.name]:
                            if isinstance(member, PlaceHolder):
                                if not(message.author in EQTest[message.channel.name]):
                                    if message.author.id == message.server.owner.id:
                                        EQTest[message.channel.name].pop(0)
                                        EQTest[message.channel.name].insert(0, message.author)
                                        participantCount[message.channel.name] += 1
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
                                                
                                    elif (message.author in SubDict[message.channel.name]):
                                        index = SubDict[message.channel.name].index(message.author)
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                            EQTest[message.channel.name][1] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name][2] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name][3] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name][4] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name][5] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name][6] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name][7] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name][8] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name][9] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name][10] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name][11] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name][0] = SubDict[message.channel.name].pop(index)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                    else:
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                           # EQTest[message.channel.name].insert(1, message.author)
                                            EQTest[message.channel.name].insert(1, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name].insert(4, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name].insert(8, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, message.author)
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, message.author)
                                            participantCount[message.channel.name] += 1
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
            else:
                yield from client.delete_message(message)
        # Force add the person to the reserve list if they choose
        elif message.content.lower() == '!addme reserve':
            bypassCheck = False
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
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
                    if not(message.author in EQTest[message.channel.name]): 
                        yield from generateList(message, "*Reserve list requested. Adding...*")
                        if not(message.author in SubDict[message.channel.name]):
                            SubDict[message.channel.name].append(message.author)
                            yield from generateList(message, '*Added {} to the Reserve list*'.format(message.author.name))
                        else:
                            yield from generateList(message, "*You are already in the Reserve List*")
                    else:
                        yield from generateList(message, "*You are already in the MPA*")
            yield from client.delete_message(message)
        # Adds the user to the weakbulleter list
        elif message.content.lower() == '!addme wb' or message.content.lower() == '!addme weakbullet':
            bypassCheck = False
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
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
                    if not(message.author in EQTest[message.channel.name]):
                        yield from generateList(message, '*You are not in the MPA! Sign yourself up first!*')
                    else:
                        yield from generateList(message, "*Weakbulleter Recieved. Adding WB List...*")
                        if not(message.author in WBList[message.channel.name]):
                            WBList[message.channel.name].append(message.author)
                            weakBulletCount[message.channel.name] += 1
                            yield from generateList(message, '*Added {} to the Weakbullter List*'.format(message.author.name))
                        else:
                            yield from generateList(message, "*You are already in the Weakbulleter List*")
            yield from client.delete_message(message)
        # Adds the user to the Techer list
        elif message.content.lower() == '!addme te' or message.content.lower() == '!addme techer':
            bypassCheck = False
            yield from client.delete_message(message)
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
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
                    if not(message.author in EQTest[message.channel.name]):
                        yield from generateList(message, '*You are not in the MPA! Sign yourself up first!*')
                    else:
                        yield from generateList(message, "*Techer Recieved. Adding Techer List...*")
                        if not(message.author in TEList[message.channel.name]):
                            TEList[message.channel.name].append(message.author)
                            techerCount[message.channel.name] += 1
                            yield from generateList(message, '*Added {} to the Techer List*'.format(message.author.name))
                        else:
                            yield from generateList(message, "*You are already in the Techer List*")
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
                if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
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
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name].insert(8, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name].insert(4, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
                                            yield from generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, FakeMember(userstr))
                                            participantCount[message.channel.name] += 1
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
                if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                    if message.channel.name in EQTest:
                        yield from client.delete_message(message)
                        if (message.author in EQTest[message.channel.name]):
                            index = EQTest[message.channel.name].index(message.author)
                            EQTest[message.channel.name].pop(index)
                            EQTest[message.channel.name].insert(index, PlaceHolder(''))
                            if (message.author in WBList[message.channel.name]):
                                WBList[message.channel.name].remove(message.author)
                                weakBulletCount[message.channel.name] -= 1
                            if (message.author in TEList[message.channel.name]):
                                TEList[message.channel.name].remove(message.author)
                                techerCount[message.channel.name] -= 1
                            participantCount[message.channel.name] -= 1
                            yield from generateList(message, '*Removed {} from the MPA list*'.format(message.author.name))
                            if len(SubDict[message.channel.name]) > 0:
                                EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                participantCount[message.channel.name] += 1
                                yield from generateList(message, '*Removed {} from the MPA list and added {}*'.format(message.author.name, EQTest[message.channel.name][index].name))
                        elif (message.author in SubDict[message.channel.name]):
                            SubDict[message.channel.name].remove(message.author)
                            yield from generateList(message, '*Removed {} from the Reserve list*'.format(message.author.name))
                        else:
                            yield from generateList(message, 'You were not in the MPA list in the first place.')
        # Removes the person from the weakbulleter list                 
        elif message.content.lower() == '!removeme wb' or message.content.lower() == '!removeme weakbullet':
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                if message.channel.name in EQTest:
                    yield from client.delete_message(message)
                    if (message.author in WBList[message.channel.name]):
                        WBList[message.channel.name].remove(message.author)
                        weakBulletCount[message.channel.name] -= 1
                        yield from generateList(message, '*Removed {} from the Weakbulleter list*'.format(message.author.name))
                    else:
                        yield from generateList(message, 'You were not in the MPA list in the first place.')
        # Removes the person from the techer list                 
        elif message.content.lower() == '!removeme te' or message.content.lower() == '!removeme techer':
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                if message.channel.name in EQTest:
                    yield from client.delete_message(message)
                    if (message.author in TEList[message.channel.name]):
                        TEList[message.channel.name].remove(message.author)
                        techerCount[message.channel.name] -= 1
                        yield from generateList(message, '*Removed {} from the Techer list*'.format(message.author.name))
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
                if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
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
                                        participantCount[message.channel.name] -= 1
                                        yield from generateList(message, '*Removed {} from the MPA list*'.format(userstr))
                                        if len(SubDict[message.channel.name]) > 0:
                                            EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                            participantCount[message.channel.name] += 1
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
        #Global Commands
        if message.content.lower() == ('!help'):
            if not message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis:   
                    em = discord.Embed(description='Greetings! I am a majestic bot that mainly organizes the team MPAs! \nMy following commands are:\n**!addme** - register yourself to the MPA. If the MPA is full, you will be automatically placed into the reserve list.\n**!removeme** - Removes yourself from the MPA. \n**!addmepvp** - Register yourself for a PVP match. Only works in the PVP channel. \n**!removemepvp** - Removes yourself from the PVP match. Only works in the PVP channel. \nUnless the commands are for the PVP channel, these will only work for the MPA organization channel. \n\n**Manager only commands:** \n**!startmpa** - Starts a team MPA. This is useable ONLY in a channel that begins with "mpa". You cannot have more than one mpa at a time in one channel. \n**!removempa** - Closes the mpa to prevent further sign ups and allows for another MPA to be started. \n**!startpvp** - Starts an organized team pvp match. Only useable in a channel that begins with "pvp". \n**!removepvp** - Same as !removempa, but for PVP channels. \n**!add <playername>** - Adds a name to the MPA list. \n**!remove <playername>** - Removes a name from the MPA list \n**!pvpadd <playername>** - PVP version of !add \n**!pvpremove <playername>** - PVP version of !remove \n**!openmpa** Opens the MPA up to Guests to join. Laplace only. \n**!closempa** - Closes MPAs to Members and above only. Laplace only. \nAny further questions should go to Tenj. Find the other hidden commands if you can...', colour=0xB3ECFF)
                    if message.server.id == '159184581830901761':                    
                        em2 = discord.Embed(description='!startmpa also can place one of the EQ banners seen in this server. By doing **!startmpa <MPA>** Tonk can add an image of the EQ to make it look prettier. So far, the EQs available are: \n**deus** - Deus Esca \n**mother** - Esca Falz Mother \n**pd** - Profound Darkness \n**pi** - Profound Invasion \n**trigger** - A trigger run \n**td3** - Tower Defense Despair \n**td4** - Tower Defense Demise \n**tdvr** - Mining Base VR \n**yamato** - Yamato. \n**Example use:** *!startmpa deus* will call a deus MPA. Give it a try!', colour=0xB3ECFF)
                else:
                    em = discord.Embed(description='', colour=0xB3ECFF)
                em.set_author(name='All Tonk Commands!', icon_url=client.user.avatar_url)
                if message.server.id == '159184581830901761' and message.author.top_role.permissions.manage_emojis:
                    em2.set_author(name='Startmpa special arguments', icon_url=client.user.avatar_url)
                yield from client.send_message(message.channel, embed=em)
                if message.server.id == '159184581830901761':
                    yield from client.send_message(message.channel, embed=em2)
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
            if message.content.lower() == '!yuiko' or message.content.lower() == '!yui' or message.content.lower() == '!doggo':
                if not message.channel.name.startswith('mpa'):
                    doggoIterator = len(yuiMemes)
                    randomNumber = randint(0, (doggoIterator - 1))
                    yield from client.send_message(message.channel, yuiMemes[randomNumber])
                    
            elif message.content.lower() == '!howtoeq':
                if not message.channel.name.startswith('mpa'):
                    yield from client.send_message(message.channel, 'https://cdn.discordapp.com/attachments/303811844072538114/304729244255125506/how2mpa.png')
            #Reload the doggo memes
            elif message.content.lower() == '!reload doggo':
                if message.author.id == '153273725666590720' or message.author.top_role.permissions.manage_channels:
                    if not message.channel.name.startswith('mpa'):
                        del yuiMemes[:]
                        with open("doggoo.txt") as f:
                            yuiMemes = f.readlines()
                        yield from client.send_message(message.channel, 'Reloaded the doggo memes!')
                else:
                    yield from client.send_message(message.channel, 'Only a manager (or Tenj) may use this command.')
            elif message.content.lower() == '!tsuki':
                if not message.channel.name.startswith('mpa'):
                    yield from client.send_message(message.channel, 'pls no burn Tenj')
        #End Ishana Specific Commands

@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print ('Logged in to servers:')
    for item in client.servers:
        print (item)
    print ('Tonk is now ready')
    print('------')
    yield from client.change_presence(game=discord.Game(name='just tonk things'))

client.run('Mjk2MTM1NTE1NTM3OTMyMjg4.C7t1mg.ubVijZ2bCHeahPqYWg4H-7wOpAY')
