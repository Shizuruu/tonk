# This module sends the contents of either the !help command or the !getting started command.

import discord
import asyncio
import traceback
client = discord.Client()

# Imports the text files that contain the help text.
with open ("assetsTonk/helpCommands.txt") as userFile:
    userCommands = userFile.read()
with open ("assetsTonk/managerCommands.txt") as managerFile:
    managerCommands = managerFile.read()
with open ("assetsTonk/adminCommands.txt") as adminFile:
    adminCommands = adminFile.read()
with open ("assetsTonk/gettingStartedHelp.txt") as gettingStartedFile:
    gettingStartedHelp = gettingStartedFile.read()
with open ("assetsTonk/ishanaExtra.txt") as ishanaExtraFile:
    ishanaExtra = ishanaExtraFile.read()


def reloadFiles():
    with open ("assetsTonk/helpCommands.txt") as userFile:
        userCommands = userFile.read()
    with open ("assetsTonk/managerCommands.txt") as managerFile:
        managerCommands = managerFile.read()
    with open ("assetsTonk/adminCommands.txt") as adminFile:
        adminCommands = adminFile.read()
    with open ("assetsTonk/gettingStartedHelp.txt") as gettingStartedFile:
        gettingStartedHelp = gettingStartedFile.read()
    with open ("assetsTonk/ishanaExtra.txt") as ishanaExtraFile:
        ishanaExtra = ishanaExtraFile.read()

supportServerInvite='https://discord.gg/7QttYRd'
async def tonk_help(arguement, message):
    global supportServerInvite
    global userCommands
    global managerCommands
    global adminCommands
    global gettingStartedHelp
    global ishanaExtra
    mainColour=0xB3ECFF
    # Calling this everytime this module is called to ensure the latest up to date help files without having to restart the bot.
    reloadFiles()
    if 'help' in arguement:
        channel = message.channel
        try:
            em = discord.Embed(description=f'{message.author.mention}, I sent you some DMs.', colour=mainColour)
            await channel.send(embed=em)
            await message.author.send(f'**User level Commands**\n\n{userCommands}')
            await message.author.send(f'\n\n**Manager Commands**\nThese commands require the user to have the **Manage Emojis** Permissions checked on their role\n\n{managerCommands}')
            await message.author.send(f'\n\n**Administrator Commands**\nThese commands require the **Administrator** Permission checked on their role.\n\n{adminCommands}\n\nDo not add <> or [] to your arguments.\nFor more help, join {supportServerInvite} and ask your question in the #support channel.')
            if 'ishana' in arguement:
                await message.author.send(f'{ishanaExtra}')
        except Exception as e:
            print (e)
            return
        return
    elif 'gettingstarted' in arguement:
        if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator:
            channel = message.channel
            em = discord.Embed(description=f'{message.author.mention}, I sent you a dm.', colour=mainColour)
            await channel.send(embed=em)
            await message.author.send(f'{gettingStartedHelp}')
        else:
            em = discord.Embed(description='Please have a server administrator use this command!', colour=0xB3ECFF)
            await message.channel.send(embed=em)
        return