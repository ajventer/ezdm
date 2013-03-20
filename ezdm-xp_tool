#!/usr/bin/env python
from ezdm_libs.character import Character,list_chars
from ezdm_libs.util import highlight,smart_input,load_json,rolldice,say,web,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput

def give_xp(character,xp):
    character.give_xp(int(xp))
    if character.current_xp() >= character.next_level():
        highlight('Character has levelled up',False)
        level=int(character.json['combat']['level/hitdice'])
        level += 1
        character.json['combat']['level/hitdice']=str(level)
        highlight('%s is now level %s' %(character.displayname(),character.json['combat']['level/hitdice']),False)
        con_bonus=int(load_json('adnd2e','ability_scores')['con'][str(character.json['abilities']['con'])]['hit'])
        hitdice=load_json('adnd2e','xp_levels')[character.json['class']['parent']][str(level)]['hit_dice']
        say ("Constitution bonus: %s" %con_bonus)
        if not '+' in hitdice:
            if not web():
                auto=smart_input('Use computer dice to roll hitpoints ?',validentries=['Y','N'],lower=True) == 'y'
            else:
                auto=True
            dice=int(load_json('adnd2e','xp_levels')[character.json['class']['parent']]['dice'])
            more_hp=rolldice(auto,1,dice,con_bonus)
        else:
            more_hp=int(hitdice.split('+')[1])
        say ("Character hitpoints increasing by %s" %more_hp)
        current_max=int(character.json['combat']['max_hp'])
        current_hp=int(character.json['combat']['hitpoints'])
        character.json['combat']['max_hp'] = str(current_max+more_hp)
        character.json['combat']['hitpoints']=str(current_hp+more_hp)
        highlight ("Character hitpoints now: %s / %s" %(character.json['combat']['hitpoints'],character.json['combat']['max_hp']),False)
        highlight('Remember to check what other stats go up in the paper sheet !',False)
        character.save()

def main():
    highlight('EZDM - XP tool')
    chars=list_chars(monsters=False)
    selected=smart_input('Character to give XP to',validentries=sorted(chars.keys()))
    character=Character(load_json('characters',chars[selected]),True)
    highlight('EZDM - XP tool')
    highlight(character.displayname(),False)
    xp=(smart_input('How much XP',integer=True))
    give_xp(character,xp)


def getdata():
    formdic={}
    formdic["Select character"]=list_chars(monsters=False).keys()
    formdic["XP to grant"]='0'
    formheader(border=3)
    dictinput(formdic)
    formfooter()
        
def webmain():
    cgiheader('EZDM - XP Tool')
    data=parsecgi()
    if not 'submit' in data:
        getdata()
    else:
        character=Character(load_json('characters',list_chars()[data["Select character"]]))
        give_xp(character,data["XP to grant"])

    
    cgifooter()        

if __name__=='__main__': 
    if not web():
        main()
    else:
        webmain()
 



