import discord
import asyncio
import aiohttp
import traceback
import sys
import os
import re
import datetime
import json
import time

client = discord.Client()

KeyFile = open('assetsTonk/TonkConfig.json')
KeyRead = KeyFile.read()
KeyDict = json.loads(KeyRead)
Key = KeyDict['APIKEY']

with open(os.path.join("assetsTonk","grayServerSlots.txt"),'r') as e:
    iassRead = e.readlines()
    inactiveServerIcons = []
    for i in iassRead:
        inactiveServerIcons.append(i.strip())
with open(os.path.join('assetsTonk',"activeServerSlots.txt"),'r') as e:
    assRead = e.readlines()
    activeServerIcons = []
    for i in assRead:
        activeServerIcons.append(i.strip())

@client.event
async def on_message(message):
    global inactiveServerIcons
    if message.content.lower().startswith('!startmpa'):
        em = discord.Embed(description='Use `!addme` to sign up \nOptionally you can add your class after addme. Example. `!addme br` \nUse `!removeme` to remove yourself from the mpa \nIf the MPA list is full, signing up will put you in the reserve list.', colour=0xcc0000)
        em.add_field(name='Party Status', value='`' + '1' + '/' + '4' + '`', inline=False)
        playerlist = '\n'
        i = 0
        while i < 4:
            if i == 0:
                playerlist += (activeServerIcons[2] + ' ' + message.author.name + '\n')
            playerlist += (inactiveServerIcons[2] + '\n')
            i += 1
        em.add_field(name='Participant List', value=playerlist, inline=True)
        inputstring = f'```diff\n+ {message.author.name} needs more people for Kirin farming. Anyone up?```'
        em.add_field(name='Last Action', value=inputstring, inline=False)
        em.set_author(name='An Kiring farming party is starting!', icon_url=message.guild.icon_url)
        await message.channel.send('', embed=em)
        return

@client.event
async def on_ready():
    game = discord.Game(name='just tonk things')
    await client.change_presence(activity=game, status=discord.Status.online)
    print ('Moms spaghetti. Its ready')

client.run(Key)