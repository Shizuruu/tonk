# Module classMatch
# This module matches the user input with the index of the class array for the bot.
def findClass(userstring):
    if userstring.lower() == 'hu' or userstring.lower() == 'hunter':
        return 'hunter'
    elif userstring.lower() == 'fi' or userstring.lower() == 'fighter':
        return 'fighter'
    elif userstring.lower() == 'ra' or userstring.lower() == 'ranger':
        return 'ranger'
    elif userstring.lower() == 'gu' or userstring.lower() == 'gunner':
        return 'gunner'
    elif userstring.lower() == 'fo' or userstring.lower() == 'force':
        return 'force'
    elif userstring.lower() == 'te' or userstring.lower() == 'techer':
        return 'techer'
    elif userstring.lower() == 'bo' or userstring.lower() == 'bouncer':
        return 'bouncer'
    elif userstring.lower() == 'br' or userstring.lower() == 'braver':
        return 'braver'
    elif userstring.lower() == 'su' or userstring.lower() == 'summoner':
        return 'summoner'
    elif userstring.lower() == 'hr' or userstring.lower() == 'hero':
        return 'hero'
    elif userstring.lower() == 'ph' or userstring.lower() == 'phantom':
        return 'phantom'
    elif userstring.lower() == 'et' or userstring.lower() == 'etoile':
        return 'etoile'
    elif userstring.lower() == 'lu' or userstring.lower() == 'luster':
        return 'luster'
    else:
        return 'noclass'

def findClassName(classID):
    if classID == 0:
        return "Hunter"
    elif classID == 1:
        return "Fighter"
    elif classID == 2:
        return "Ranger"
    elif classID == 3:
        return "Gunner"
    elif classID == 4:
        return "Force"
    elif classID == 5:
        return "Techer"
    elif classID == 6:
        return "Bouncer"
    elif classID == 7:
        return "Braver"
    elif classID == 8:
        return "Summoner"
    elif classID == 9:
        return "Hero"
    elif classID == 10:
        return "Phantom"
    elif classID == 11:
        return "Etoile"
    elif classID == 12:
        return "Luster"
    elif classID == 13:
        return "None"