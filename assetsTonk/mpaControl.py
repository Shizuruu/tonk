import asyncio
import tonkDB

# Function to start an MPA. The message arguement takes the Discord Message object instead of a string. The string is passed to the broadcast arguement
async def function_startmpa(message, broadcast, mpaType):
    maxParticipant = 12
    try:
        # Query the DB to see if there is an MPA and query for the configuration items
        dbQuery = tonkDB.gidQueryDB(ctx.guild.id)
        mpaChannelList = dbQuery['Items'][0]['mpaChannels']
        activeMPAList = dbQuery['Items'][0]['activeMPAs'][f'{str(message.channel.id)}']
        try:
            guestEnabled = dbQuery['Items'][0]['mpaConfig'][f'{str(message.channel.id)}']['guestEnabled']
    except KeyError:
        await message.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    except IndexError:
        await message.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
        return
    if (str(message.channel.id)) in (mpaChannelList):
        mpaMap = MpaMatchDev.get_class(mpaType)
        try:
            if mpaMap == 'default':
                pass
            else:
                # CHANGE: Convert to upload from AWS S3
                await message.channel.send(file=discord.File(mpaMap))
        except FileNotFoundError as e:
            await message.channel.send('Unable to find a file with that name! Please check your spelling.')    
            return
        if mpaType == '8man' or mpaType == 'pvp' or mpaType == 'busterquest' or mpaType == 'hachiman':
            maxParticipant = 8
        if not str(message.channel.id) in activeMPAList:
            if message.author.top_role.permissions.manage_emojis or message.author.top_role.permissions.administrator or message.author == client.user:
                try:
                    if message != '' and message != '|':
                        if broadcast == 'ouEPO*#T*#$TH(QETH(PHFGWOUDT#PWIJOYAYAYAYYAYAYAYYAYAYAYAYYAYAYAYYAYAA{IOUHIJ(*)YH#RIOjewfO*HEFU(*Y#@R':
                            pass
                        else:
                            await message.channel.send(f' {broadcast}')
                    else:
                        pass
                    EQTest = list()
                    SubDict = list()
                    #ActiveMPA.append(message.channel.id)
                   # roleAdded[message.channel.id] = False
                    #guestEnabled[message.channel.id] = False
                    #playerRemoved[message.channel.id] = False
                    participantCount[message.channel.id] = 0
                    if message.channel.id in mpaExpirationConfig[str(message.guild.id)]:
                        expirationDate[message.channel.id] = (int(time.mktime(datetime.now().timetuple())) + mpaExpirationCounter)
                        mpaRemoved[message.channel.id] = False
                        print (expirationDate[message.channel.id])
                    # if eightMan[message.channel.id] == True:
                    #     for index in range(8):
                    #         EQTest[message.channel.id].append(PlaceHolder(""))
                    #     totalPeople[message.channel.id] = 8
                    # else:
                    for indexEQTest in range(maxParticipant):
                        EQTest.append(PlaceHolder(""))
                    await generateList(message, dbQuery, EQTest, SubDict, '```dsconfig\nStarting MPA. Please use !addme to sign up!```')
                except discord.Forbidden:
                    print (message.author.name + f'Tried to start an MPA at {message.guild.name}, but failed.')
                    await message.author.send('I lack permissions to set up an MPA! Did you make sure I have the **Send Messages** and **Manage Messages** permissions checked?')
                    return

            else:
                await message.channel.send('You do not have the permission to do that, starfox.')
        else:
            await generateList(message, dbQuery, EQTest, SubDict, '```fix\nThere is already an MPA being made here!```')
    else:
        await message.channel.send('This channel is not an MPA Channel. You can enable the MPA features for this channel with `!enablempachannel`. Type `!help` for more information.')
