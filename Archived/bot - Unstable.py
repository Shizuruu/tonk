import discord
import asyncio
import urllib.request
import aiohttp
import traceback
import sys
import os
import urllib.parse
import re
import datetime
from datetime import datetime,tzinfo,timedelta
from random import randint
from io import BytesIO, StringIO


class FakeMember():
    def __init__(self, name):
        self.name = name
 
class PlaceHolder():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name)

        
print ('Logging into Discord...\n')
EQTest = {}
SubDict = {}
guestEnabled = {}
EQPostDict = {}
MPACount = 0
participantCount = {}
appended = False
client = discord.Client()

r_url = re.compile(r"^http?:")
r_image = re.compile(r".*\.(jpg|png|gif)$")



def is_bot(m):
	return m.author == client.user
    
def is_not_bot(m):
    return m.author != client.user
	
    
#LOAD THE DOGGO MEMES
with open("doggoo.txt") as f:
    yuiMemes = f.readlines()

getTime = datetime.now()


async def generateList(message, inputstring):
    global MPACount
    pCount = 1
    nCount = 1
    sCount = 1
    mpaCount = 1
    alreadyWroteList = False
    mpaFriendly = ''
    playerlist = '\n'
 # This is the Ishana format
    if message.server.id == '159184581830901761':
        for word in EQTest[message.channel.name]: 
            if nCount == 1:
                if alreadyWroteList == False:
                    playerlist += ('**Participant List: **\n')
                    alreadyWroteList = True
                mpaCount += 1
            if (type(word) is PlaceHolder):
                playerlist += ('**>**' + '\n')
            else:
                playerlist += ('**>**' + " " + word + '\n')
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
            for word in SubDict[message.channel.name]:
                playerlist += (str(sCount) + ". " + word + '\n')
                sCount += 1  
                
                
        if guestEnabled[message.channel.name] == True:
            mpaFriendly = 'Yes'
        else:
            mpaFriendly = 'No'
        try:
            await client.edit_message(EQPostDict[message.channel.name], playerlist + inputstring + '\n' + '**MPA Status:** ' + str(participantCount[message.channel.name]) + '/12' + '\n**Are Non-Members welcome?** ' + mpaFriendly)
        except:
            print(message.author.name + ' Started an MPA on Ishana')
            MPACount += 1
            print('Amount of Active MPAs: ' + str(MPACount))
            EQPostDict[message.channel.name] = await client.send_message(message.channel, playerlist + inputstring + '\n' + '**MPA Status:** ' + str(participantCount[message.channel.name]) + '/12' + '\n**Are Non-Members welcome?** ' + mpaFriendly)
    # Laplace/Any other place that it may take place in        
    else:
        for word in EQTest[message.channel.name]:
            if nCount == 1:
                playerlist += ('\n**Participant List** ' + '\n')
                mpaCount += 1
            if (type(word) is PlaceHolder):
                playerlist += (str(nCount) + ". " + "" + '\n')
            else:
                playerlist += (str(nCount) + ". " + word + '\n')
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
            for word in SubDict[message.channel.name]:
                playerlist += (str(sCount) + ". " + word + '\n')
                sCount += 1  
               
        try:
            await client.edit_message(EQPostDict[message.channel.name], playerlist + inputstring + '\n' + '**MPA Status:** ' + str(participantCount[message.channel.name]) + '/12')
        except:
            print(message.author.name + ' Started an MPA on Laplace')
            MPACount += 1
            print('Amount of Active MPAs: ' + str(MPACount))
            EQPostDict[message.channel.name] = await client.send_message(message.channel, playerlist + inputstring + '\n' + '**MPA Status:** ' + str(participantCount[message.channel.name]) + '/12')

 
 
@client.event
##  GENERAL COMMANDS ##
async def on_message(message):
    global appended
    global MPACount
    global yuiMemes
    if message.content.startswith('!'):
		#Debugging commands
        if message.content.lower() == '!gettime':
            if not message.channel.name.startswith('mpa'):
                await client.send_message(message.channel, getTime)
        elif message.content.lower() == '!supertest':
            await client.send_message(message.channel, 'Respond at ' + str(getTime))
        elif message.content.lower() == '!supertestagain':
            await client.send_message(message.channel, 'I am working.')
        elif message.content.lower() == '!gethighestrole':
            if not message.channel.name.startswith('mpa'):
                await client.send_message(message.channel, message.author.top_role)
        elif message.content.lower() == '!amiguest':
            if not message.channel.name.startswith('mpa'):
                isGuest = False
                for index in range(len(message.author.roles)):
                    if message.author.roles[index].name == 'Guests':
                        isGuest = True
                await client.send_message(message.channel, isGuest)
        elif message.content.lower() == '!listroles':
            if not message.channel.name.startswith('mpa'):
                for index in range(len(message.author.roles)):
                    if len(message.author.roles) == 0:
                        await client.send_message(message.channel, 'You either dont have a role, or this command is bugged.')
                    else:
                        await client.send_message(message.channel, message.author.roles[index])
                else:
                    await client.send_message(message.channel, 'No permissions!')
        elif message.content.lower() == '!quickclean 15':
            if message.author.top_role.permissions.manage_channels or message.author.id == '153273725666590720':
                await client.purge_from(message.channel, limit=15)
            else:
                await client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
        elif message.content.lower() == '!quickclean 30':
            if message.author.top_role.permissions.manage_channels or message.author.id == '153273725666590720':
                await client.purge_from(message.channel, limit=30)
            else:
                await client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
        elif message.content.lower() == '!quickclean 45':
            if message.author.top_role.permissions.manage_channels or message.author.id == '153273725666590720':
                await client.purge_from(message.channel, limit=45)
            else:
                await client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
        elif message.content.lower() == '!quickclean 75':
            if message.author.top_role.permissions.manage_channels or message.author.id == '153273725666590720':
                await client.purge_from(message.channel, limit=75)
            else:
                await client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
        elif message.content.lower() == '!numberroles':
            if not message.channel.name.startswith('mpa'):
                await client.send_message(message.channel, len(message.author.roles))
        elif message.content.lower() == '!checkmpamanagerperm':
            if not message.channel.name.startswith('mpa'):
                doIHavePermission = message.author.top_role.permissions.manage_emojis
                if doIHavePermission:
                    await client.send_message(message.channel, 'You have the permissions to start an MPA.')
                else:
                    await client.send_message(message.channel, 'You do not have the permission to start an MPA. Take a hike.')
        elif message.content.lower() == '!serverinfo':
            if not message.channel.name.startswith('mpa'):
                await client.send_message(message.channel, 'Server Name: ' + message.server.name + '\nServer ID: ' + message.server.id)
        elif message.content.lower() == '!ffs':
            if message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                    await client.purge_from(message.channel, limit=100, after=getTime, check=is_not_bot)
                else:
                    await client.send_message(message.channel, 'You lack the permissions to use this command.')
            else:
                await client.send_message(message.channel, 'This command can only be used in a MPA channel.')
        elif message.content.lower().startswith('!testarg'):
            userstr = ''
            if not message.channel.name.startswith('mpa'):
                userstr = message.content
                userstr = userstr.replace("!testarg", "")
                userstr = userstr.replace(" ", " ")
                await client.send_message(message.channel, 'Responding with: ' + userstr)
        elif message.content.lower() == '!!shutdown':
            if message.author.id == '153273725666590720':
                if message.server.id == '159184581830901761':
                    await client.send_message(message.channel, 'Shutting down. If anything goes wrong during the downtime, please blame yui.')
                else:
                    await client.send_message(message.channel, 'DONT DO THIS TO ME MA-')
                await client.logout()
            else:
                await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
        ## MPA TRACKER COMMANDS ##
        #Starts the MPA on the current eq channel. Places the channel name into a dictionary and sets it to be a list. Then fills the list up with 12 placeholder objects.
               
        elif message.content.lower().startswith('!startmpa'):
            userstr = message.content
            userstr = userstr.replace("!startmpa", "")
            userstr = userstr.replace(" ", "")
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                if message.server.id == '159184581830901761':
                    if userstr == 'deus':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'deus.jpg')
                    elif userstr == 'pd':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'PD.jpg')
                    elif userstr == 'magatsu':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'Maggy.jpg')
                    elif userstr == 'td3':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'MBD3.jpg')
                    elif userstr == 'td4':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'MBD4.jpg')
                    elif userstr == 'tdvr':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'MBDVR20.jpg')
                    elif userstr == 'mother':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'Mother.jpg')
                    elif userstr == 'pi':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'PI.jpg')
                    elif userstr == 'trigger':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'tRIGGER.jpg')
                    elif userstr == 'yamato':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'yamato.jpg')
                    elif userstr == 'seasonal':
                        await client.send_message(message.channel, '{}'.format(message.server.roles[0]))
                        await client.send_file(message.channel, 'Season_Quest.jpg')
                await client.delete_message(message)
                if not message.channel.name in EQTest:
                    if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                        EQTest[message.channel.name] = list()
                        SubDict[message.channel.name] = list()
                        guestEnabled[message.channel.name] = False
                        participantCount[message.channel.name] = 0
                        for index in range(12):
                            EQTest[message.channel.name].append(PlaceHolder(""))
                        if message.server.id == '159184581830901761':
                            em = discord.Embed(description='**Meeting in**: Block 03 Frankas Cafe \nUse `!addme` to sign up. \nOptionally you can add your class after addme. Example. `!addme br` \nUse `!removeme` to remove yourself from the mpa \nUse `!addme reserve` to sign up into the reserve list. \nIf the MPA list is full, signing up will put you in the reserve list.', colour=0x0099FF)
                        else:
                            em = discord.Embed(description='**Meeting in**: Block 222 Frankas Cafe \nUse `!addme` to sign up \nOptionally you can add your class after addme. Example. `!addme br` \nUse `!removeme` to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.', colour=0xFF66FF)
                        em.set_author(name='An MPA is starting!', icon_url=message.server.icon_url)
                        await client.send_message(message.channel, '', embed=em)
                        await generateList(message, 'Starting MPA. Please use `!addme` to sign up!')
                    else:
                        await client.send_message(message.channel, 'You do not have the permission to do that, starfox.')
                else:
                    await generateList(message, 'An MPA is already being organized here!')
            else:
                await client.send_message(message.channel, 'This channel does not meet the requirements to start an MPA.')
        #Dangerous to use if you are not careful.   
        elif message.content.lower() == '!currentmpa':
            if message.channel.name.startswith('mpa'):
                nCount = 1
                await client.send_message(message.channel, '**Current MPA List**')
                for member in EQTest[message.channel.name]:
                    await client.send_message(message.channel, str(nCount) + ". " + member.name + '\n')
                    nCount+=1
            else:
                await client.send_message(message.channel, 'This isn\'t an MPA Channel!')
                
        elif message.content.lower() == '!openmpa':
            if message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                    if guestEnabled[message.channel.name] == True:
                        await client.send_message(message.channel, 'This MPA is already open!')
                    else:
                        guestEnabled[message.channel.name] = True
                        for index in range(len(message.server.roles)):
                            if message.server.id == '153346891109761024':
                                if (message.server.roles[index].id == '224757670823985152'):
                                    await client.send_message(message.channel, '{} can now join in the MPA!'.format(message.server.roles[index].mention))
                            elif message.server.id == '159184581830901761':
                                await client.send_message(message.channel, 'Opened MPA to non-members!')
                                await generateList(message, '*MPA is now open to non-members.*')
                                break
        elif message.content.lower() == '!closempa':
            if message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                    if guestEnabled[message.channel.name] == False:
                        await client.send_message(message.channel, 'This MPA is already closed!')
                    else:
                        guestEnabled[message.channel.name] = False
                        await client.send_message(message.channel, 'Closed MPA to Members only.')
                        await generateList(message, '*MPA is now closed to non-members*')
                else:
                    await client.send_message(message.channel, 'You do not have the permission to do this.')
     
        #Removes the MPA on the current eq channel. PLEASE USE THIS BEFORE STARTING A NEW ONE OTHERWISE THINGS WILL BREAK AAAAAAAAAAAAAAAA
                                 
        elif message.content.lower() == '!removempa':
            if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                    if message.channel.name in EQTest:
                        try:
                            del EQTest[message.channel.name]
                            print(message.author.name + ' Closed an MPA on ' + message.server.name)
                            MPACount -= 1
                            print('Amount of Active MPAs: ' + str(MPACount))
                            if message.channel.id == '206673616060940288':
                                await client.purge_from(message.channel, limit=15, check=is_bot)
                                participantCount[message.channel.name] = 0
                            else:
                                await client.purge_from(message.channel, limit=30, after=getTime)
                                participantCount[message.channel.name] = 0
                        except KeyError:
                            pass
                    else:
                        await client.send_message(message.channel, 'There is no existing MPA to delete.')
                else:
                    await client.send_message(message.channel, 'There is no existing MPA to delete in a non EQ channel.')
            else:
                await generateList(message, 'You are not a manager.')
                   
            #Adds a player into the MPA list on the current eq channel. Checks for a placeholder object to remove and inserts the user's user object into the list.
        elif message.content.lower().startswith('!addme'):
            bypassCheck = False
            userstr = ''
            classRole = ''
            index = 0
            personInMPA = False
            personInReserve = False
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                for index in range(len(message.author.roles)):
                    if message.author.roles[index].id == '154465245488742400':
                        bypassCheck = True
                    elif message.author.roles[index].id == '277639714717302793':
                        bypassCheck = True
                    elif message.author.roles[index].id == '191162764033523712':
                        bypassCheck = True
                    elif message.author.top_role.permissions.manage_emojis:
                        bypassCheck = True
                if (bypassCheck == False and guestEnabled[message.channel.name] == False):
                    await generateList(message, '*Guests are not allowed to join this MPA.*')
                    await client.delete_message(message)
                else:
                    if message.channel.name in EQTest:
                        userstr = message.content
                        userstr = userstr.replace("!addme", "")
                        userstr = userstr.replace(" ", "")
                        for index, item in enumerate(EQTest[message.channel.name]):
                            if (type(EQTest[message.channel.name][index]) is PlaceHolder):
                                pass
                            elif message.author.name in item:
                                personInMPA = True
                                break
                        for index, item in enumerate(SubDict[message.channel.name]):
                            if message.author.name in item:
                                personInReserve = True
                                break
                        if message.server.id == '159184581830901761':
                            if userstr == 'hu' or userstr == 'hunter':
                                classRole = '<:hu:232420435663388672>'
                            elif userstr == 'fi' or userstr == 'fighter':
                                classRole = '<:fi:232420436393197568>'
                            elif userstr == 'ra' or userstr == 'ranger':
                                classRole = '<:ra:232420437466939392>'
                            elif userstr == 'gu' or userstr == 'gunner':
                                classRole = '<:gu:232420435671777310>'
                            elif userstr == 'fo' or userstr == 'force':
                                classRole = '<:fo:232420436389003264>'
                            elif userstr == 'te' or userstr == 'techer':
                                classRole = '<:te:232420436850245632>'
                            elif userstr == 'bo' or userstr == 'bouncer':
                                classRole = '<:bo:232420435331907585>'
                            elif userstr == 'br' or userstr == 'braver':
                                classRole = '<:br:232420436053458955>'
                            elif userstr == 'su' or userstr == 'summoner':
                                classRole = '<:su:232420436787462144>'
                            else:
                                classRole = '<:wcl:314632680132050947>'
                        elif message.server.id == '153346891109761024':
                            if userstr == 'hu' or userstr == 'hunter':
                                classRole = '<:hu:231873747290816512>'
                            elif userstr == 'fi' or userstr == 'fighter':
                                classRole = '<:fi:231873708552224769>'
                            elif userstr == 'ra' or userstr == 'ranger':
                                classRole = '<:ra:231873762474196993>'
                            elif userstr == 'gu' or userstr == 'gunner':
                                classRole = '<:gu:231873733298487297>'
                            elif userstr == 'fo' or userstr == 'force':
                                classRole = '<:fo:231873719755079682>'
                            elif userstr == 'te' or userstr == 'techer':
                                classRole = '<:te:231873778500632577>'
                            elif userstr == 'bo' or userstr == 'bouncer':
                                classRole = '<:bo:231874759439286272>'
                            elif userstr == 'br' or userstr == 'braver':
                                classRole = '<:br:231873692190244864>'
                            elif userstr == 'su' or userstr == 'summoner':
                                classRole = '<:su:262276895427657729>'
                        if userstr == 'reserve':
                            if personInMPA == False: 
                                await generateList(message, "*Reserve list requested. Adding...*")
                                await client.delete_message(message)
                                if personInReserve == False:
                                    SubDict[message.channel.name].append(message.author.name)
                                    await generateList(message, '*Added {} to the Reserve list*'.format(message.author.name))
                                else:
                                    await generateList(message, "*You are already in the Reserve List*")
                            else:
                                await generateList(message, "*You are already in the MPA*")
                            return
                        await client.delete_message(message)
                        if message.server.id == '159184581830901761':
                            if message.author.id == '162533764206034944':
                                message.author.name = message.author.name + ' <:yuipls:232420444844720128>'
                        for word in EQTest[message.channel.name]:
                            if isinstance(word, PlaceHolder):
                                if personInMPA == False:
                                    if message.author.id == message.server.owner.id:
                                        EQTest[message.channel.name].pop(0)
                                        EQTest[message.channel.name].insert(0, classRole + ' ' + message.author.name)
                                        participantCount[message.channel.name] += 1
                                        await generateList(message, '*Added Lord {} to the MPA list*'.format(message.author.name))
                                        appended = True
                                        break
                                    elif (message.author.name in SubDict[message.channel.name]):
                                        index = SubDict[message.channel.name].index(message.author.name)
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                            EQTest[message.channel.name][1] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name][2] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name][3] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name][4] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name][5] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name][6] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name][7] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name][8] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name][9] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name][10] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name][11] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name][0] = classRole + ' ' + SubDict[message.channel.name].pop(index) 
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} from the reserves to the MPA list.*'.format(message.author.name))
                                            appended = True
                                            break
                                    else:
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                            EQTest[message.channel.name].insert(1, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name].insert(4, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name].insert(8, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(message.author.name))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, classRole + ' ' + message.author.name)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*{} farted. I put him to top.*'.format(message.author.name))
                                            appended = True
                                            break
                                else:
                                    await generateList(message, "*You are already in the MPA*")
                                    break
                        if not appended:
                            if personInMPA == False: 
                                await generateList(message, "*The MPA is full. Adding to reserve list.*")
                                if personInReserve == False:
                                    SubDict[message.channel.name].append(message.author.name)
                                    await generateList(message, '*Added {} to the Reserve list*'.format(message.author.name))
                                else:
                                    await generateList(message, "*You are already in the Reserve List*")
                            else:
                                await generateList(message, "*You are already in the MPA*")
                        appended = False                                
                    else:
                        await client.send_message(message.channel, 'A manager did not start the MPA yet')
            else:
                await client.delete_message(message)
                            
        #Adds a string/name of a player that the Manager wants into the MPA list.      
        elif message.content.lower().startswith('!add '):
            if message.author.top_role.permissions.manage_emojis or message.author.id == '153273725666590720':
                userstr = ''
                if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                    if message.channel.name in EQTest:
                        userstr = message.content
                        userstr = userstr.replace("!add ", "")
                        userstr = userstr.replace(" ", "")
                        if userstr == "":
                            await generateList(message, "You can't add nobody. Are you drunk?")
                            appended = True
                        else:
                            for word in EQTest[message.channel.name]:
                                if isinstance(word, PlaceHolder):
                                    if not(userstr in EQTest[message.channel.name]):
                                        if isinstance(EQTest[message.channel.name][1], PlaceHolder):
                                            EQTest[message.channel.name].pop(1)
                                            EQTest[message.channel.name].insert(1, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][2], PlaceHolder):
                                            EQTest[message.channel.name].pop(2)
                                            EQTest[message.channel.name].insert(2, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][3], PlaceHolder):
                                            EQTest[message.channel.name].pop(3)
                                            EQTest[message.channel.name].insert(3, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][5], PlaceHolder):
                                            EQTest[message.channel.name].pop(5)
                                            EQTest[message.channel.name].insert(5, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][6], PlaceHolder):
                                            EQTest[message.channel.name].pop(6)
                                            EQTest[message.channel.name].insert(6, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][7], PlaceHolder):
                                            EQTest[message.channel.name].pop(7)
                                            EQTest[message.channel.name].insert(7, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][9], PlaceHolder):
                                            EQTest[message.channel.name].pop(9)
                                            EQTest[message.channel.name].insert(9, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][10], PlaceHolder):
                                            EQTest[message.channel.name].pop(10)
                                            EQTest[message.channel.name].insert(10, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][11], PlaceHolder):
                                            EQTest[message.channel.name].pop(11)
                                            EQTest[message.channel.name].insert(11, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][8], PlaceHolder):
                                            EQTest[message.channel.name].pop(8)
                                            EQTest[message.channel.name].insert(8, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][4], PlaceHolder):
                                            EQTest[message.channel.name].pop(4)
                                            EQTest[message.channel.name].insert(4, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                                        elif isinstance(EQTest[message.channel.name][0], PlaceHolder):
                                            EQTest[message.channel.name].pop(0)
                                            EQTest[message.channel.name].insert(0, userstr)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Added {} to the MPA list*'.format(userstr))
                                            appended = True
                                            break
                        if not appended:
                            await generateList(message, "*The MPA is full. Adding to reserve list.*")
                            SubDict[message.channel.name].append(userstr)
                            await generateList(message, '*Added {} to the Reserve list*'.format(userstr))
                    else:
                        await client.send_message(message.channel, 'There is no MPA.')
                    await client.delete_message(message)
                else:
                    await client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
            else:
                await client.send_message(message.channel, "You don't have permissions to use this command")
            appended = False
        #Removes the user object from the MPA list.
        elif message.content.lower() == '!removeme':
            inMPA = False
            if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
                if message.channel.name in EQTest:
                    await client.delete_message(message)
                    for index, item in enumerate(EQTest[message.channel.name]):
                        if (type(EQTest[message.channel.name][index]) is PlaceHolder):
                            pass
                        elif message.author.name in item:
                            EQTest[message.channel.name].pop(index)
                            EQTest[message.channel.name].insert(index, PlaceHolder(''))
                            participantCount[message.channel.name] -= 1
                            await generateList(message, '*Removed {} from the MPA list*'.format(message.author.name))
                            if len(SubDict[message.channel.name]) > 0:
                                EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                participantCount[message.channel.name] += 1
                                await generateList(message, '*Removed {} from the MPA list and added {}*'.format(message.author.name, EQTest[message.channel.name][index].name))
                            inMPA = True
                            break
                        else:
                            await generateList(message, 'You were not in the MPA list in the first place.')
                    if inMPA == False:
                        for index, item in enumerate(SubDict[message.channel.name]):
                            if message.author.name in item:
                                SubDict[message.channel.name].pop(index)
                                await generateList(message, '*Removed {} from the Reserve list*'.format(message.author.name))
                            else:
                                await generateList(message, 'You were not in the MPA list in the first place.')
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
                                    if (type(EQTest[message.channel.name][index]) is PlaceHolder):
                                        pass
                                    elif userstr.lower() in EQTest[message.channel.name][index].lower():
                                        toBeRemoved = EQTest[message.channel.name][index]
                                        EQTest[message.channel.name][index] = userstr
                                        EQTest[message.channel.name].remove(userstr)
                                        EQTest[message.channel.name].insert(index, PlaceHolder(''))
                                        userstr = userstr
                                        participantCount[message.channel.name] -= 1
                                        await generateList(message, '*Removed {} from the MPA list*'.format(toBeRemoved))
                                        if len(SubDict[message.channel.name]) > 0:
                                            EQTest[message.channel.name][index] = SubDict[message.channel.name].pop(0)
                                            participantCount[message.channel.name] += 1
                                            await generateList(message, '*Removed {} from the MPA list and added {}*'.format(toBeRemoved, EQTest[message.channel.name][index].name))
                                        appended = True
                                        break
                                if not appended:
                                    for index in range(len(SubDict[message.channel.name])):
                                        appended = False
                                        if userstr in SubDict[message.channel.name][index]:
                                            toBeRemoved = SubDict[message.channel.name][index]
                                            SubDict[message.channel.name][index] = userstr
                                            SubDict[message.channel.name].remove(userstr)
                                            userstr = userstr
                                            await generateList(message, '*Removed {} from the Reserve list*'.format(toBeRemoved))
                                            appended = True
                                            break
                                if not appended:    
                                    await generateList(message, "Player {} does not exist in the MPA list".format(userstr))
                        else:
                            await client.send_message(message.channel, "There are no players in the MPA.")
                    else:
                        await client.send_message(message.channel, 'There is no MPA.')
                    await client.delete_message(message)
                else:
                    await client.send_message(message.channel, 'There is nothing to remove in a non-EQ channel.')
            else:
                await generateList(message, "You don't have permissions to use this command")
 ## GENERAL COMMANDS ##
      #Laplace Specific Commands
        if message.server.id == '153346891109761024':           
            if message.content.lower() == '!bob':
                if not message.channel.name.startswith('mpa'):
                    await client.send_message(message.channel, 'Don\'t be a bob. What is a bob? We don\'t know, but just don\'t be a bob.')
            
            elif message.content.lower() == '!theface':
                if not message.channel.name.startswith('mpa'):
                    randomNumber = randint(0, 3)
                    if (randomNumber == 0):
                        await client.send_message(message.channel, '⎛　　　　●　　ω　　●　 ⎞')
                    elif (randomNumber == 1):
                        await client.send_message(message.channel, '*⎛　　　　●　　ω　　●　 ⎞*')
                    elif (randomNumber == 2):
                        await client.send_message(message.channel, '**⎛　　　　●　　ω　　●　 ⎞**')
                    elif (randomNumber == 3):
                        await client.send_message(message.channel, '⎛　　●　　ω　　●　　　 ⎞')
                        

            elif message.content.lower() == '!massdestruction':
                if not message.channel.name.startswith('mpa'):
                    await client.send_message(message.channel, 'BABY BABY BABY BABY BABY BABY BBABY BABY BABY BABY BABY BABY')

            elif message.content.lower() == '!dog':
                if not message.channel.name.startswith('mpa'):
                    randomNumber = randint(0, 4)
                    if randomNumber == 0:
                        await client.send_message(message.channel, 'A rare doggo! https://66.media.tumblr.com/988f4137285d758d567e73a27dd6d944/tumblr_nuuvidOKcH1uzkruwo1_500.jpg')
                    elif randomNumber == 1:
                        await client.send_message(message.channel, 'A rare doggo! https://cdn.discordapp.com/attachments/219826145825128458/301944176142974976/dog_4.jpg')
                    elif randomNumber == 2:
                        randomNumberTwo = randint(0, 1)
                        if randomNumberTwo == 0:
                           await client.send_message(message.channel, 'You expected me to bark or a doggo picture didn\'t you? But not today!')
                        else:
                           await client.send_message(message.channel, 'A rare doggo! https://cdn.discordapp.com/attachments/219826145825128458/301944457287434240/dog_5.jpg')
                    elif randomNumber == 3:
                        await client.send_message(message.channel, 'A rare doggo! https://cdn.discordapp.com/attachments/219826145825128458/301944731338801152/doge_corgi.jpg')
                    elif randomNumber == 4:
                        await client.send_message(message.channel, 'A rare doggo! https://cdn.discordapp.com/attachments/219826145825128458/301944890290470912/doge_ritual.jpg')
                    else:
                        await client.send_message(message.channel, 'A rare doggo! https://66.media.tumblr.com/988f4137285d758d567e73a27dd6d944/tumblr_nuuvidOKcH1uzkruwo1_500.jpg')
                    
        #End Laplace Specific Command List                       
        #Global Commands
        if message.content.lower() == ('!help'):
            if not message.channel.name.startswith('mpa'):
                if message.author.top_role.permissions.manage_emojis:   
                    em = discord.Embed(description='Greetings! I am a majestic bot that mainly organizes the team MPAs! \nMy following commands are:\n**!addme** - register yourself to the MPA. If the MPA is full, you will be automatically placed into the reserve list.\n**!removeme** - Removes yourself from the MPA. \nUnless the commands are for the PVP channel, these will only work for the MPA organization channel. \n\n**Manager only commands:** \n**!startmpa** - Starts a team MPA. This is useable ONLY in a channel that begins with "mpa". You cannot have more than one mpa at a time in one channel. \n**!removempa** - Closes the mpa to prevent further sign ups and allows for another MPA to be started. \n**!add <playername>** - Adds a name to the MPA list. \n**!remove <playername>** - Removes a name from the MPA list \n**!openmpa** Opens the MPA up to Guests to join. Laplace only. \n**!closempa** - Closes MPAs to Members and above only. Laplace only. \n**!ffs** - Cleans everything but the list in a MPA channel. Useful in case conversations start breaking out in the MPA channel. \nAny further questions should go to Tenj. Find the other hidden commands if you can...', colour=0xB3ECFF)
                    if message.server.id == '159184581830901761':                    
                        em2 = discord.Embed(description='!startmpa also can place one of the EQ banners seen in this server. By doing **!startmpa <MPA>** Tonk can add an image of the EQ to make it look prettier. So far, the EQs available are: \n**deus** - Deus Esca \n**mother** - Esca Falz Mother \n**pd** - Profound Darkness \n**pi** - Profound Invasion \n**trigger** - A trigger run \n**td3** - Tower Defense Despair \n**td4** - Tower Defense Demise \n**tdvr** - Mining Base VR \n**yamato** - Yamato. \n**Example use:** *!startmpa deus* will call a deus MPA. Give it a try!', colour=0xB3ECFF)
                else:
                    em = discord.Embed(description='', colour=0xB3ECFF)
                em.set_author(name='All Tonk Commands!', icon_url=client.user.avatar_url)
                if message.server.id == '159184581830901761' and message.author.top_role.permissions.manage_emojis:
                    em2.set_author(name='Startmpa special arguments', icon_url=client.user.avatar_url)
                await client.send_message(message.channel, embed=em)
                if message.server.id == '159184581830901761':
                    await client.send_message(message.channel, embed=em2)
     
        elif message.content.lower() == '!test':
            if not message.channel.name.startswith('mpa'):
                randomNumber = randint(0, 17)
                if (randomNumber == 0):
                    await client.send_message(message.channel, 'At this point, you should just give up me, {}.'.format(message.author.mention))
                elif (randomNumber == 1):
                    await client.send_message(message.channel, 'You rang, {}?'.format(message.author.mention))
                elif (randomNumber == 2):
                    await client.send_message(message.channel, 'Please now take the time to look to the right {}. There is a wall.'.format(message.author.mention))
                elif (randomNumber == 3):
                    await client.send_message(message.channel, 'Did you know these responses were probably written at 3AM, {}?'.format(message.author.mention))
                elif (randomNumber == 4):
                    await client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know a pineapple is actually a bunch of small berries fused together in a single mass?'.format(message.author.mention))
                elif (randomNumber == 5):
                    await client.send_message(message.channel, 'I am working, {}. Somewhere in the world, someone else typed this same command.'.format(message.author.mention))
                elif (randomNumber == 6):
                    await client.send_message(message.channel, 'Reading this text probably isn\'t the best use of your time, {}.'.format(message.author.mention))
                elif (randomNumber == 7):
                    await client.send_message(message.channel, 'Girls are now praying. Please wait warmly and have some tea, {}.'.format(message.author.mention))
                elif (randomNumber == 8):
                    await client.send_message(message.channel, 'If you ask me what brand is the best for toothpaste, it would probably be Colgate, {}.'.format(message.author.mention))
                elif (randomNumber == 9):
                    await client.send_message(message.channel, 'I am thou. Thou art pie. But this is no social link, {}.'.format(message.author.mention))
                elif (randomNumber == 10):
                    await client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know the word **Underground** is the only word in english that begins with \'und and ends with \'und?'.format(message.author.mention))
                elif (randomNumber == 11):
                    await client.send_message(message.channel, 'It has always been a dream of mine to see a bear playing a lute. Isn\'t it the same for you, {}?'.format(message.author.mention))
                elif (randomNumber == 12):
                    await client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know that hippopotomonstrosesquipedaliophobia is the fear of long words?'.format(message.author.mention))
                elif (randomNumber == 13):
                    await client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know when Joseph Gayetty invented toilet paper in 1857, he had his name printed on each sheet?.'.format(message.author.mention))
                elif (randomNumber == 14):
                    await client.send_message(message.channel, 'Secret command found! Now find the others. I trust that it will be a much bigger challenge, {}.'.format(message.author.mention))
                elif (randomNumber == 15):
                    await client.send_message(message.channel, 'I am working, {}. While I have your attention, did you know that bald eagles have around 7000-7200 feathers in total? That totally screams freedom!'.format(message.author.mention))
                elif (randomNumber == 16):
                    await client.send_message(message.channel, 'Are you being entertained by this useless information, {}?'.format(message.author.mention))
                elif (randomNumber == 17):
                    await client.send_message(message.channel, 'I have traveled to many places, but at the end of the day, there is no place like 127.0.0.1, {}.'.format(message.author.mention))
                else:
                    await client.send_message(message.channel, 'I am working, but this command is not.')
				
        elif message.content.lower() == '!pah':
            await client.send_message(message.channel, 'GTFO PAH\nT\nF\nO\n\nP\nA\nH')
				
        elif message.content.lower() == '!tink':
            if not message.channel.name.startswith('mpa'):
                randomNumber = randint(0, 3)
                if (randomNumber == 0):
                    await client.send_message(message.channel, '"I never die." - Tink\n http://imgur.com/a/FW4X5')
                elif (randomNumber == 1):
                    await client.send_message(message.channel, '*"PSO2 will never have PVP!"* - Tink 2016' )
                elif (randomNumber == 2):
                    await client.send_message(message.channel, 'http://i.imgur.com/t7g1GLM.jpg')
                elif (randomNumber == 3):
                    await client.send_message(message.channel, 'http://i.imgur.com/4ZecDSf.png')
        elif message.content.lower() == '!tenj':
            if not message.channel.name.startswith('mpa'):
                if message.author.id == '153273725666590720':
                    await client.send_message(message.channel, 'The one and only.')
                else:
                    await client.send_message(message.channel, 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        elif message.content.lower() == '!neweq':
            if not message.channel.name.startswith('mpa'):
                await client.send_message(message.channel, 'https://cdn.discordapp.com/attachments/142483459196190720/294317457408000001/Cryycordinanutshell.png')
                
		#End Global Commands
        #Ishana Specific Commands
        if message.server.id == '159184581830901761':
            if message.content.lower() == '!yuiko' or message.content.lower() == '!yui' or message.content.lower() == '!doggo':
                if not message.channel.name.startswith('mpa'):
                    doggoIterator = len(yuiMemes)
                    randomNumber = randint(0, (doggoIterator - 1))
                    await client.send_message(message.channel, yuiMemes[randomNumber])
                    
            elif message.content.lower() == '!howtoeq':
                if not message.channel.name.startswith('mpa'):
                    await client.send_message(message.channel, 'https://cdn.discordapp.com/attachments/303811844072538114/304729244255125506/how2mpa.png')
            #Reload the doggo memes
            elif message.content.lower() == '!reload doggo':
                if message.author.id == '153273725666590720' or message.author.top_role.permissions.manage_channels:
                    if not message.channel.name.startswith('mpa'):
                        del yuiMemes[:]
                        with open("doggoo.txt") as f:
                            yuiMemes = f.readlines()
                        await client.send_message(message.channel, 'Reloaded the doggo memes!')
            #Add a doggo meme
            elif message.content.startswith('!loaddoggo'):
                if message.author.id == '153273725666590720' or message.author.top_role.permissions.manage_channels:
                    if not message.channel.name.startswith('mpa'):
                        userstr = message.content
                        userstr = userstr.replace("!loaddoggo ", "")
                        if r_image.match(userstr):
                            with open("doggoo.txt", 'a') as f:
                                f.write('\n' + userstr)
                            del yuiMemes[:]
                            with open("doggoo.txt") as f:
                                yuiMemes = f.readlines()
                            await client.send_message(message.channel, 'Loaded the doggo meme!')
                        else:
                            await client.send_message(message.channel, 'Must be an image to add!')

                else:
                    await client.send_message(message.channel, 'Only a manager (or Tenj) may use this command.')
            elif message.content.lower() == '!tsuki':
                if not message.channel.name.startswith('mpa'):
                    await client.send_message(message.channel, 'pls no burn Tenj')
            elif message.content.lower() == '!purge':
                if message.channel.id == '311924651247009792':
                    if (message.author.top_role.permissions.manage_channels or message.author.id == '153273725666590720' or message.author.id == '176707140101210121'):
                        await client.purge_from(message.channel, limit=200, after=getTime )
                else:
                    await client.send_message(message.channel, 'http://i.imgur.com/FnKySHo.png')
        #End Ishana Specific Commands

@client.event
async def on_ready():
    global isReady
    global bootTimer
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print ('Logged in to servers:')
    for item in client.servers:
        print (item)
    print ('Tonk is now ready')
    print('------')
    await client.change_presence(game=discord.Game(name='just tonk things'))

client.run('Mjk2MTM1NTE1NTM3OTMyMjg4.C7t1mg.ubVijZ2bCHeahPqYWg4H-7wOpAY')
