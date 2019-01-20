import discord
import os
import asyncio
import sys
import traceback
from random import randint
from discord.ext import commands



class Tonk(discord.Client):
    def __init__(self):
        self.EQList = {}
        self.reserveList = {}
        self.appended = False
        self.MPACount = 0
        self.guestEnabled = {}
        
    # End of init
    async def cmd_startmpa(self, EQType):
        if message.channel.name.startswith('mpa') or message.channel.id == '206673616060940288':
            if EQType == 'deus':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'deus.jpg')
            elif EQType == 'pd':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'PD.jpg')
            elif EQType == 'magatsu':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'Maggy.jpg')
            elif EQType == 'td3':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'MBD3.jpg')
            elif EQType == 'td4':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'MBD4.jpg')
            elif EQType == 'tdvr':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'MBDVR20.jpg')
            elif EQType == 'mother':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'Mother.jpg')
            elif EQType == 'pi':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'PI.jpg')
            elif EQType == 'trigger':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'tRIGGER.jpg')
            elif EQType == 'yamato':
                await self.send_message(message.channel, '{}'.format(message.server.roles[0]))
                await self.send_file(message.channel, 'yamato.jpg')
        await self.delete_message(message)
        if not message.channel.name in self.EQList:
            self.EQList[message.channel.name] = list()
            self.reserveList[message.channel.name] = list()
            guestEnabled[message.channel.name] = False
            participantCount[message.channel.name] = 0
            