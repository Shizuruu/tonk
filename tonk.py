import discord
import asyncio
import traceback
import sys
import os
import re
import shutil
import datetime
import json
import shlex
import time
import logging
from datetime import datetime
from discord.utils import find
from discord.ext import commands
from assetsTonk import tonkHelper
from assetsTonk import tonkDB
from assetsTonk import utils
from assetsTonk import mpaControl
from assetsTonk import parseDB
from assetsTonk import sendErrorMessage
from assetsTonk import mpaChannel
from assetsTonk import mpaConfig

# Set the logger file
logging.basicConfig(filename='tonk.log',level=logging.INFO,format='%(asctime)s %(name)-4s %(levelname)-4s %(message)s',datefmt='%m-%d %H:%M')

# These are all the constants that will be used throughout the bot. Most if not all of these are dictionaries that allow for different settings per server/channel to be used.
print ('Beginning bot startup process...\n')

# Reads the config file and load it into memory
ConfigFile = open('assetsTonk/configs/TonkConfig.json')
ConfigDict = json.loads(ConfigFile.read())
APIKey = ConfigDict['APIKEY']

start = time.time()

commandPrefix = f"{ConfigDict['COMMAND_PREFIX']}"
client = commands.Bot(command_prefix=commandPrefix)
# Remove the default help command
client.remove_command('help')
lastRestart = str(datetime.now())

# In memory dictionary used to keep track of mpaexpiration dates.
expirationDate = {}

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

# Function that loads all the mpa expiration dates from the DB into memory.
def loadMpaExpirations():
    mpaDict = tonkDB.queryExpirationKeys()
    defaultConfigQuery = tonkDB.configDefaultQueryDB()
    for index, value in enumerate(mpaDict['Items']):
        try:
            for channelID in mpaDict['Items'][index]['activeMPAs']:
                try:
                    mpaExpirationEnabled = mpaDict['Items'][index]['mpaConfig'][channelID]['mpaExpirationEnabled']
                except KeyError:
                    mpaExpirationEnabled = defaultConfigQuery['Items'][0]['mpaConfig']['mpaExpirationEnabled']
                if mpaExpirationEnabled.lower() == 'true':
                    if len(mpaDict['Items'][index]['activeMPAs'][channelID]) > 0:
                        for messageID in mpaDict['Items'][index]['activeMPAs'][channelID]:
                            expirationDate[messageID] = {}
                            expirationDate[messageID]['channelID'] = channelID
                            expirationDate[messageID]['expirationDate'] = mpaDict['Items'][index]['activeMPAs'][channelID][messageID]['expirationDate']
                            #expirationDate[messageID]['expirationEnabled'] = mpaDict['Items'][index]['mpaConfig'][channelID]['mpaExpirationEnabled']
                    else:
                        pass
                else:
                    pass
        except KeyError:
            pass
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return None
    return True

async def isManager(ctx):
    # Administrator permissions will grant permissions regardless of role.
    # if ctx.author.top_role.permissions.administrator:
    #     return True
    dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
    mpaManagerRoles = parseDB.getMpaManagerRoles(ctx.channel.id, dbQuery)
    mpaChannelList = dbQuery['Items'][0]['mpaChannels']
    authorRoleID = str(ctx.author.top_role.id)
    if type(mpaManagerRoles) is dict:
        if mpaManagerRoles['channelManagerRoles'] is not None:
            # Return true if the user's role is in either channel OR server manager roles, else return false
            if authorRoleID in mpaManagerRoles['channelManagerRoles']:
                return True
            # User is not in channelManagerRoles and serverManagerRoles is not blank
            elif (mpaManagerRoles['serverManagerRoles']) is not None:
                if authorRoleID in mpaManagerRoles['serverManagerRoles']:
                    return True
            # These if statements should be ending the function on the return statement, if none of those conditions are met we return false.
            return False
        # Case: Channel manager roles is NOT configured, but server manager roles are
        elif mpaManagerRoles['serverManagerRoles'] is not None:
            if authorRoleID in mpaManagerRoles['serverManagerRoles']:
                return True
            else:
                return False
        # Other cases which is most likely both dictionaries are not configured at all.
        elif (str(ctx.channel.id)) in (mpaChannelList):
            return False
        else:
            return None
    return None


# Function called if the message ID in the expirationDate dictionary does not match with the new message ID passed by the mpaControl functions
# Copies the data from the old message ID, removes old message ID entry and then readds the information with the new message ID.
def fixExpirationDict(mpaMessageID):
    if mpaMessageID['oldMessageID'] in expirationDate.keys() and mpaMessageID['newMessageID'] not in expirationDate.keys():
        expirationTime = expirationDate[mpaMessageID['oldMessageID']]['expirationDate']
        del expirationDate[mpaMessageID['oldMessageID']]
        expirationDate[mpaMessageID['newMessageID']] = {
            'channelID': mpaMessageID['newMessageID'],
            'expirationDate': expirationTime
        }

# Background task that runs every second to check if there's any MPA that will be expiring soon.
async def expiration_checker():
    await client.wait_until_ready()
    for messageID in list(expirationDate):
        nowTime = int(time.mktime(datetime.now().timetuple()))
        if (int(expirationDate[messageID]['expirationDate']) - 15) == nowTime:
            await client.get_channel(int(expirationDate[messageID]['channelID'])).send(f":warning: **Inactivity Detected! This MPA will be automatically closed in `15` seconds if no actions are taken!** :warning:")
        if expirationDate[messageID]['expirationDate'] == nowTime:
            print ("Expiration reached")
            context = await client.get_context(await client.get_channel(int(expirationDate[messageID]['channelID'])).fetch_message(id=int(messageID)))
            removeMpaID = await mpaControl.removempa(context, client)
            del expirationDate[removeMpaID]

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
    if message.content.startswith('!'):
        print (f'{message.author.name} ({message.author.id}) has called for the command {message.content}')
        # # These commands are for whoever runs this bot. 
        # if message.content.lower() == '!!shutdown':
        #     if message.author.id == ConfigDict['OWNERID']:
        #         if message.guild.id == serverIDDict['Ishana']:
        #             await message.channel.send('Shutting down. If anything goes wrong during the downtime, please blame yui.')
        #         else:
        #             await message.channel.send('DONT DO THIS TO ME MA-')
        #             shutdownRole = discord.utils.get(client.get_guild(226835458552758275).roles, id=370340076527288321)
        #             await client.get_channel(ConfigDict['ADMINCHANNELID']).send(f'Tonk is {shutdownRole.mention}')
        #         await client.logout()
        #     else:
        #         await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        # # Closes all MPAs the bot has ever known to be active at this moment. Easy to use before shutting the bot down.
        # elif message.content.lower() == '!!burnbabyburn':
        #     if message.author.id == ConfigDict['OWNERID']:
        #         if len(ActiveMPA) > 0:
        #             for index in range(len(ActiveMPA)):
        #                 await client.get_channel(ActiveMPA[index]).send('!removempa')
        #             await message.channel.send('Successfully closed all existing MPAs on all servers.')
        #         else:
        #             await message.channel.send('No MPAs currently exist.')
        #     else:
        #         await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        # elif message.content.lower().startswith('!!leaveserver'):
        #     if message.author.id == ConfigDict['OWNERID']:
        #         userstr = message.content
        #         userstr = userstr.replace("!!leaveserver", "")
        #         userstr = userstr.replace(" ", "")
        #         await client.get_guild(int(userstr)).leave()
        #     else:
        #         await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        # elif message.content.lower().startswith('!!findroleid'):
        #     if message.author.id == ConfigDict['OWNERID']:
        #         userstr = message.content
        #         userstr = userstr.replace("!!findroleid", "")
        #         userstr = userstr.replace(" ", "")
        #         foundRole = discord.utils.get(message.guild.roles, name=userstr)
        #         if foundRole is not None:
        #             em = discord.Embed(colour=foundRole.colour)
        #             em.add_field(name='Role Name:', value=foundRole.name, inline=False)
        #             em.add_field(name='Role ID', value=foundRole.id, inline=False)
        #             await message.channel.send('', embed=em)
        #         else:
        #             await message.channel.send('Unable to find a role with that name!')
        #     else:
        #         await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        # elif message.content.lower().startswith('!!announce'):
        #     if message.author.id == ConfigDict['OWNERID']:
        #         userstr = message.content
        #         if message.content.startswith('!!announce'):
        #             userstr = userstr.replace("!!announce", "")
        #         else:
        #             userstr = userstr.replace("!!announce", "")
        #         if message.guild.id == ConfigDict['EMOJISTORAGEID']:
        #             return
        #         else:
        #             for item in client.guilds:
        #                 if item.id == ConfigDict['OWNERSERVERID'] or item.id == ConfigDict['EMOJISTORAGEID']:
        #                     pass
        #                 try:
        #                     await client.get_channel(item.default_channel.id).send(f'{userstr}')
        #                     await client.get_channel(ConfigDict['ADMINCHANNELID']).send('Sent announcement to ' + item.name)
        #                 except AttributeError:
        #                     await client.get_channel(ConfigDict['ADMINCHANNELID']).send('Error trying to send announcement to ' + item.name)
        #                     pass
        #                 await client.get_channel(ConfigDict['ADMINCHANNELID']).send('All announcements sent.')
        #         # await client.send_message(client.get_channel('326883995641970689'), userstr)
        #     await message.delete()
        # elif message.content.lower() == '!!lastrestart':
        #     if message.author.id == ConfigDict['OWNERID']:
        #         await message.channel.send(str(lastRestart))
        #     else:
        #         await message.channel.send('Only Tenj may use this command.')
        # elif message.content.lower() == '!!listservers':
        #     serverlist = ''
        #     if message.author.id == ConfigDict['OWNERID']:
        #         for item in client.guilds:
        #             serverlist += (item.name + f'\n{item.id}' + '\n')
        #         em = discord.Embed(description=serverlist, colour=0x0099FF)
        #         em.set_author(name='Joined Servers')
        #         await message.channel.send('', embed=em)
        #     else:
        #         await message.channel.send('CANT LET YOU DO THAT, STARFOX.') 
        # elif message.content.lower() == '!!restart':
        #     if message.author.id == ConfigDict['OWNERID']:
        #         await message.channel.send('Tonk will now restart!')
        #         print ('The restart command was issued! Restarting Bot...')
        #         end = time.time()
        #         runTime = (end - start)
        #         restartRole = discord.utils.get(client.get_guild(226835458552758275).roles, id=370339592055947266)
        #         await client.get_channel(ConfigDict['ADMINCHANNELID']).send(f'Tonk is {restartRole.mention}' + '\nRun time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(runTime)))
        #         os.execl(sys.executable, *([sys.executable]+sys.argv))
        #     else:
        #         await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        # elif message.content.lower() == '!!clearconsole':
        #     if message.author.id == ConfigDict['OWNERID']:
        #         await message.channel.send('Clearing Console')
        #         os.system('cls' if os.name == 'nt' else 'clear')
        #     else:
        #         await message.channel.send('CANT LET YOU DO THAT, STARFOX.')
        await client.process_commands(message)


# Gets the highesr role for the user calling this command
@client.command(name='gethighestrole')
async def cmd_gethighestrole(ctx):
    result = utils.getHighestRole(ctx)
    await ctx.send(result)

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
    hasManagerPermissions = await isManager(ctx)
    if hasManagerPermissions:
        await utils.ffs(ctx, client)
        return
    elif hasManagerPermissions is not None:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_ffs.name}")
        return
    else:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, f"cmd_{cmd_ffs.name}")
        return

# Starts an MPA with the given arguements. Message and mpaType is optional, and will just fill in with the given data if nothing was put into the command.
# Calls function_startmpa to actually do the legwork
@client.command(name='startmpa')
async def cmd_startmpa(ctx, mpaType: str = 'default', *, message: str = ''):
    hasManagerPermissions = await isManager(ctx)
    if hasManagerPermissions or ctx.author.id == client.user.id:
        # This checks if Tonk has the deleting permission. If it doesn't, don't run the script at all and just stop.
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print (ctx.author.name + f' Tried to start an MPA at {ctx.message.guild.name}, but failed.')
            await ctx.author.send('I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
            return
        startmpaResult = await mpaControl.startmpa(ctx, message, mpaType)
        if startmpaResult is not None:
            await client.get_channel(ConfigDict['ADMINCHANNELID']).send(f'```css\n{ctx.author.name}#{str(ctx.author.discriminator)} (ID: {str(ctx.author.id)}) Started an MPA on {ctx.guild.name}\nTimestamp: {str(datetime.now())}```')
            expirationDate[startmpaResult['listMessageID']] = {
                'channelID': str(ctx.channel.id),
                'expirationDate': startmpaResult['expirationDate']
            }
    elif hasManagerPermissions is not None:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_startmpa.name}")
    else:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, f"cmd_{cmd_startmpa.name}")
# Closes out the MPA and flushes related data so another MPA can be opened in the same channel at a later date.
@client.command(name='removempa')
async def cmd_removempa(ctx):
    hasManagerPermissions = await isManager(ctx)
    if hasManagerPermissions or ctx.author.id == client.user.id:
        removeMpaID = await mpaControl.removempa(ctx, client)
        if removeMpaID is not None:
            await client.get_channel(ConfigDict['ADMINCHANNELID']).send(f'```diff\n- {ctx.author.name}# {ctx.author.discriminator} (ID: {str(ctx.author.id)}) Closed an MPA on {ctx.guild.name}\nTimestamp: {str(datetime.now())}```')
            print(f'{ctx.author.name} Closed an MPA on {ctx.guild.name}')
            del expirationDate[removeMpaID]
    elif hasManagerPermissions is not None:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_removempa.name}")
    else:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, f"cmd_{cmd_removempa.name}")

# Adds the user into the EQ list in the EQ channel. Optionally takes a class as an arguement. If one is passed, add the class icon and the user's name into the EQ list.
@client.command(name='addme', aliases=['reserveme'])
async def cmd_addme(ctx, mpaArg: str = 'none'):
    mpaMessageID = await mpaControl.addme(ctx, mpaArg)
    if mpaMessageID is not None:
        fixExpirationDict(mpaMessageID)
    return

# Manager command that adds a custom name to the MPA.
@client.command(name='add', aliases=['reserve'])
async def cmd_add(ctx, user: str = '', mpaArg: str = 'none'):
    hasManagerPermissions = await isManager(ctx)
    if hasManagerPermissions:
        mpaMessageID = await mpaControl.addUser(ctx, user, mpaArg)
        if mpaMessageID is not None:
            fixExpirationDict(mpaMessageID)
        return
    elif hasManagerPermissions is not None:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_add.name}")
    else:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, f"cmd_{cmd_add.name}")

# Removes the caller from the MPA.
@client.command(name='removeme')
async def cmd_removeme(ctx):
    await mpaControl.removeme(ctx)
    return

# Manager command to remove a user from the MPA.
@client.command(name='remove')
async def cmd_remove(ctx, user):
    hasManagerPermissions = await isManager(ctx)
    if hasManagerPermissions:
        mpaMessageID = await mpaControl.removeUser(ctx, user)
        if mpaMessageID is not None:
            fixExpirationDict(mpaMessageID)
        return
    elif hasManagerPermissions is not None:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_remove.name}")
    else:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, f"cmd_{cmd_remove.name}")

# Changes the class of the caller to another one they specify. Or none if they call for none of the classes.
@client.command(name='changeclass')
async def cmd_changeclass(ctx, mpaArg: str = 'none'):
    mpaMessageID = await mpaControl.changeClass(ctx, mpaArg)
    if mpaMessageID is not None:
        fixExpirationDict(mpaMessageID)
    return

# Private messages the caller information. Special instructions are added if calling from a certain server.
@client.command(name='help')
async def cmd_help(ctx):
    await tonkHelper.tonk_help("standardhelp", ctx.message)
    return

# Private messages the caller information to help them get started with using this bot.
@client.command(name='gettingstarted')
async def cmd_gettingstarted(ctx):
    if ctx.author.top_role.permissions.administrator:
        await tonkHelper.tonk_help('gettingstarted', ctx.message)
        return
    else:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_gettingstarted.name}")

# Test if the bot works or not.
@client.command(name='test')
async def cmd_test(ctx):
    await ctx.channel.send(f'At this point, you should just give up me, {ctx.author.mention}.')  

# Enables the MPA channel so that the MPA commands can be used.
# By default, Admins need to run this command so not every channel can have MPA commands be run on it.
@client.command(name='enablempachannel')
async def cmd_enablempachannel(ctx):
    if ctx.author.top_role.permissions.administrator:
        await mpaChannel.enablempachannel(ctx)
        return
    else:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_enablempachannel.name}")
        return

# Disables the MPA functions on the channel the command is called in. Removes the channel data from all the related json files.
@client.command(name='disablempachannel')
async def cmd_disablempachannel(ctx):
    if ctx.author.top_role.permissions.administrator:
        await mpaChannel.disablempachannel(ctx)
        return
    else:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_disablempachannel.name}")
        return

@client.command(name='config')
async def cmd_config(ctx, *args):
    if ctx.author.top_role.permissions.administrator:
        await mpaConfig.cmdConfigParser(ctx, *args)
    else:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_config.name}")
        return


# Debugging command
# @client.command(name='eval')
# async def cmd_eval(ctx, *code):
#     if ctx.author.id == ConfigDict['OWNERID']:
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

# Opens the MPA to non-approved roles.
@client.command(name='openmpa')
async def cmd_openmpa(ctx):
    hasManagerPermissions = await isManager(ctx)
    if hasManagerPermissions:
        await mpaControl.openmpa(ctx)
    elif hasManagerPermissions is not None:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_openmpa.name}")
    else:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, f"cmd_{cmd_openmpa.name}")
    return

# Closes the MPA to only approved roles.
@client.command(name='closempa')
async def cmd_closempa(ctx):
    hasManagerPermissions = await isManager(ctx)
    if hasManagerPermissions:
        await mpaControl.closempa(ctx)
    elif hasManagerPermissions is not None:
        await sendErrorMessage.noCommandPermissions(ctx, f"cmd_{cmd_openmpa.name}")
    else:
        await sendErrorMessage.mpaChannelNotEnabled(ctx, f"cmd_{cmd_openmpa.name}")
    return

# Schedules an MPA for to be made at a later time. This converts a time in hours/minutes/seconds and converts it into seconds, which will then put it in a dictionary
# and a function that runs every second will check to see if it's time to start an MPA with the arguements provided in this command.
@client.command(name='schedulempa')
async def cmd_schedulempa(ctx, requestedTime, message: str = '', mpaType: str = 'default'):
    await ctx.send('This command is currently disabled. Stay tuned for more details!')
    return
    if ctx.channel.id in mpaChannels[str(ctx.guild.id)]:
        if ctx.author.top_role.permissions.manage_emojis or ctx.author.top_role.permissions.administrator or ctx.author.id == ConfigDict['OWNERID']:
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

# Finishing bootup, prints uptime/status information to the control channel
print ('Logging into Discord...\n')
@client.event
async def on_ready():
    FreshStart = False
    connectedServers = 0
    mpaExpirationLoad = loadMpaExpirations()
    if mpaExpirationLoad is None:
        await client.logout()
    # Flush tmp cache
    try:
        shutil.rmtree('tmp')
        os.makedirs('tmp')
    except FileNotFoundError:
        os.makedirs('tmp')
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
    reconnectRole = discord.utils.get(client.get_guild(ConfigDict['OWNERSERVERID']).roles, id=ConfigDict['RECONNECTEDROLEID'])
    print ('Tonk is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)))
    print('------')
    game = discord.Game(name='just tonk things')
    await client.change_presence(activity=game, status=discord.Status.online)
    onlineRole = discord.utils.get(client.get_guild(ConfigDict['OWNERSERVERID']).roles, id=ConfigDict['ONLINEROLEID'])
    if FreshStart == True:
        await client.get_channel(ConfigDict['ADMINCHANNELID']).send(f'Tonk is now {onlineRole.mention}' + '\nStartup time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nConnected to **' + str(connectedServers) + '** servers' + '\nLast Restarted: ' + lastRestart)
    else:
        await client.get_channel(ConfigDict['ADMINCHANNELID']).send(f'Tonk has {reconnectRole.mention}')
    while True:
        await expiration_checker()
      #  await mpa_schedulerclock()
        await asyncio.sleep(1)

# Global command handler
#@client.event
#async def on_command_error(ctx, error):
#    print (error)
    #print ('...but that command was not found.')
#    return

# Behavior every time this bot joins another server. Tries to send a message to the general channel as well as logging the join event to the control panel server.
@client.event
async def on_guild_join(server):
    await client.get_channel(ConfigDict['ADMINCHANNELID']).send(f'```diff\n+ Joined {server.name} ```' + f'(ID: {str(server.id)})')
    general = find(lambda x: x.name == 'general',  server.channels)
    if general and general.permissions_for(server.me).send_messages:
        await general.send('**Greetings!**\nI am Tonk, a MPA organization bot for PSO2! Please type **!gettingstarted** to set my functions up!')

# Logs the leave event on the control panel server.
@client.event
async def on_guild_remove(server):
    await client.get_channel(ConfigDict['ADMINCHANNELID']).send(f'```diff\n- Left {server.name} ```'.format(server.name) + f'(ID: {str(server.id)})')
    

@client.event
async def on_resumed():
    connectedServers = 0
    print ('Tonk has resumed from a disconnect.')
    for item in client.guilds:
        connectedServers += 1
    resumeRole = discord.utils.get(client.get_guild(ConfigDict['OWNERSERVERID']).roles, id=ConfigDict['RESUMEROLEID'])
    await client.get_channel(ConfigDict['ADMINCHANNELID']).send(f'Tonk has {resumeRole.mention}' + '\nConnected to **' + str(connectedServers) + '** servers')
# WOOHOO    
client.run(APIKey)
