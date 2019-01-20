# This module matches the user typed input and returns the image for the bot to send to the channel.


def get_class(userstring):
    if userstring == ' deus':
        return 'deus.jpg'
    elif userstring == ' pd':
        return 'PD.jpg'
    elif userstring == ' magatsu':
        return 'Maggy.jpg'
    elif userstring == ' td3':
        return 'MBD3.jpg'
    elif userstring == ' td4':
        return 'MBD4.jpg'
    elif userstring == ' tdvr':
        return 'MBDVR20.jpg'
    elif userstring == ' mother':
        return 'Mother.jpg'
    elif userstring == ' pi':
        return 'PI.jpg'
    elif userstring == ' trigger':
        return 'tRIGGER.jpg'
    elif userstring == ' yamato':
        return 'yamato.jpg'
    elif userstring == ' seasonal':
        return 'Season_Quest.jpg'
    elif userstring == ' pvp':
        return 'PvP.jpg'
    elif userstring == ' busterquest':
        return 'Buster_Quest.jpg'
    elif userstring == ' dragon':
        return 'Erythron-Dragon.jpg'
    elif userstring == ' cm':
        return 'Challenge_Mode.jpg'
    elif userstring == ' oloser' or userstring == ' omegaloser':
        return 'oloser.jpg'
    elif userstring == ' test':
        return 'test.png'
    elif userstring == ' goc':
        return 'GOC.png'
    elif userstring == ' 8man' or userstring == ' hachiman':
        return '8_man_eq.png'
    elif userstring == ' 12man':
        return '12_man_eq.png'
    else:
        return 'default'