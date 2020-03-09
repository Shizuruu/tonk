# Module classMatch
# This module matches the user input with the index of the class array for the bot.
def findClass(userstring):
    if userstring.lower() == 'hu' or userstring.lower() == 'hunter':
        return 0
    elif userstring.lower() == 'fi' or userstring.lower() == 'fighter':
        return 1
    elif userstring.lower() == 'ra' or userstring.lower() == 'ranger':
        return 2
    elif userstring.lower() == 'gu' or userstring.lower() == 'gunner':
        return 3
    elif userstring.lower() == 'fo' or userstring.lower() == 'force':
        return 4
    elif userstring.lower() == 'te' or userstring.lower() == 'techer':
        return 5
    elif userstring.lower() == 'bo' or userstring.lower() == 'bouncer':
        return 6
    elif userstring.lower() == 'br' or userstring.lower() == 'braver':
        return 7
    elif userstring.lower() == 'su' or userstring.lower() == 'summoner':
        return 8
    elif userstring.lower() == 'hr' or userstring.lower() == 'hero':
        return 9
    elif userstring.lower() == 'ph' or userstring.lower() == 'phantom':
        return 10
    elif userstring.lower() == 'et' or userstring.lower() == 'etoile':
        return 11
    else:
        return 12

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
        return "None"