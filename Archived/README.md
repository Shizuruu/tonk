#Decision-Bot.py

##01/09/2016 Update
This is a bot for a Discord server. This bot has functions that cater mainly to PSO2. It has the ability to shout at everyone whenever an EQ is coming up and it has the ability to organize multi-parties.

I do not know if this bot is heroku-compatible. I haven't tried it and will not try it. If you do try it though, get back to me about it and do tell me how it works out.

There are several base commands that the bot has. Any command listed with the markdown **[M]** means that it can only be used by a user with a role that can manage channels. 

**BASIC COMMANDS:**
```
!help - spits out a wall of text that tells the users what the bot is capable of and what commands users are allowed to use
!hello - replies to the user with a simple hello.
!eq - posts the current EQ(Emergency Quest) status that comes straight from Flyergo's API.
```

**EQ COMMANDS:**
```
!startmpa [M] - Starts an MPA in the channel it is called in. Usually called by the bot automatically.
!removempa [M] - Frees the MPA list from memory and deletes the channel.
!addme - adds the user who calls this command into the MPA.
!removeme - removes the user who calls this command from the MPA.
!addplayer [M] - adds the string that is specified within the call to the MPA list.
!removeplayer [M] - removes the string OR user that is specified within the call from the MPA list.
```

**DEBUG COMMANDS:**
```
!id - gives the user it's unique ID that is assigned to their account.
!startparse - Called automatically once the bot has started. But starts the EQ-notification function.
```

To get the bot to do it's autonomous methods, there are simple conditions that must be met:
* There has to be a bot_notifications channel for the bot to post in, or the bot will proceed to post EQ notifications in the default channel.
* Emergency Quest channels must start with an **eq** tag in order for the bot to keep track of MPAs. An example of such channel name can be *eq_pd_11pm*.

That's about it. Make sure you update infos.txt and read through the first few lines of code to replace some of the ID strings so your bot can fully function.

You will need the following API to get the bot working: https://github.com/Rapptz/discord.py

MUCH LOVE TO RAPPTZ FOR THE WONDERFUL API.

MUCH LOVE TO ACF FOR POINTING ME AT THE RIGHT DIRECTION.

MUCH LOVE TO FLYERGO FOR THE WEBAPI THAT HE IS RUNNING.

