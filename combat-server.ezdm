#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()    
from ezdm_libs.util import load_icon,dice_list,rolldice,select_char,load_json,json_from_template,highlight,say,web,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,cgihide,template_conditional,validate_json
from ezdm_libs.character import Character,list_chars
import sys
import os
# pylint: disable-msg=E0611
from bottle import Bottle, run, template,route,post,get,put,request
characters=[]
initiative=[]
rounds=1
upchar=-1
player_index=-1
attack_mods={'Atacker on high ground':1,'Defender invisible':-4,'Defender off-balance':2,'Defender stunned or prone':999,'Defender surprized':+1,'Rear attack':+2}

def initialize():
    global characters
    global initiative
    global rounds
    global upchar
    characters=[]
    initiative=[]
    rounds=1
    upchar=-1
    player_index=-1
    
def turns():
    return int(rounds/10)
    
def debuglist(out):
    for line in out:
        print out.index(line),':',line

def show_in_combat():
    cl='<br>'    
    for c in in_combat():
        cl= "%s<br> %s (%s hitpoints)" %(cl,c.displayname(),c.json['combat']['hitpoints'])
    return highlight('Characters in combat: %s' %cl,sayit=False)    

def addchar(): 
    global characters
    out=[cgiheader('EZDM-Combat',wsgi=True,linkback=False)]
    out += show_in_combat()
    out.append(formheader(title="Add character to combat",action='/addchar',wsgi=True))
    clist=list_chars().keys()
    if len(characters) > 1:    
        clist.insert(0,'')
    out.append(select_char(clist,wsgi=True))    
    if len(characters) > 1:
        out.append(webinput('Add more characters ?','addmore',['No','Yes'],wsgi=True))
    
    out.append(formfooter(wsgi=True))
    out.append(cgifooter(wsgi=True,linkback=False))
    debuglist(out)
    output='\n'.join(out)
    return output

def in_combat():
    global characters
    ic=[]
    for char in characters:
        if not char.removed:
            ic.append(char)
    return ic

def roll_for_initiative():
    global initiative
    init=[]
    out=''
    for char in in_combat():
        out="%s %s" %(out,say(char.displayname(),wsgi=True))
        initroll=rolldice(char.autoroll,1,20,wsgi=True)
        out="%s: %s<br>" %(out,initroll[1])
        tup=(initroll[0],characters.index(char))
        init.append(tuple(tup))
        initiative=sorted(init)
    
    return out

def next_round(out):
    global upchar
    global rounds
    rounds +=1
    upchar=-1
    out+=highlight('End of round',sayit=False)
    out.append(formheader(action='/combat',wsgi=True))
    out.append(webinput('Fight another round','more_combat',['Yes','No'],wsgi=True))
    out.append(formfooter(wsgi=True))
    out.append(cgifooter(linkback=False,wsgi=True))
    return '\n'.join(out)

def end_combat():
    out=[cgiheader('EZDM-Combat',wsgi=True,linkback=False)]
    initialize()
    return addchar()
    
def selectlist(excl=[]):
    global characters
    s=[]
    for char in in_combat():
        name=char.displayname()
        if name not in excl:
            name="%s (%s)" %(name,characters.index(char))
            s.append(name)
    return s
    
def select_target(player_index,no_exclude=False):
    global characters
    exclude=[]
    if not no_exclude:
        exclude.append(characters[player_index].displayname())
    target_list = selectlist(exclude)
    if len(target_list) > 0:
        return webinput("%s is attacking: please select target" %characters[player_index].displayname(),'target',target_list,wsgi=True)
    else:
        return 'There are no more living targets'
  
    

def do_cast(player_index):
    global characters
    out=[formheader(title="%s casting a spell" %characters[player_index].displayname(),wsgi=True)]
    out.append(webinput('Casting time measured in','use_turns',['Turns','Rounds'],wsgi=True))
    out.append(webinput('How many does it take ?','cast_time','1',wsgi=True))
    out.append(select_target(player_index,True))
    out.append(cgihide('fromform','do_cast',wsgi=True))
    out.append(formfooter(wsgi=True))
    return out
    
def do_spell_complete(player_index):
    global characters
    out=[]
    spell_actions=['Other (DM to handle)']
    success=characters[player_index].spell_success(wsgi=True)
    if not success[0]:
        return (False,success[1])
    if characters[player_index].spell_friendly_target():
        spell_actions.append('Heal')
    else:
        throw=characters[player_index].spell_target.saving_throw('spell',wsgi=True)
        if throw[0]:
            return (False,['<br>'.join(throw[1])])
        spell_actions.append('Damage')  
    out.append(formheader(title='%s Has finished casting the spell !' %characters[player_index].displayname(),wsgi=True))
    out.append(webinput('Spell action','spell_action',spell_actions,wsgi=True))
    out.append(cgihide('fromform','spell_complete',wsgi=True))
    out.append(formfooter(wsgi=True))
    return (True,out)

def dicemenu(dicetype):
    return [webinput('%s dice sides' %dicetype,'sides',dice_list(),wsgi=True),webinput('Number of %s dice' %dicetype.lower(),'numdice','1',wsgi=True),webinput('%s modifier' %dicetype.lower(),'mod','0',wsgi=True)]

def spell_complete_menu(action,player_index):
    global characters
    out=[formheader(title='%s completing spell' %characters[player_index].displayname(),wsgi=True)]
    if action == 'Heal':
        out += dicemenu('Healing')
    else:
        out += dicemenu('Damage')
    out.append(cgihide('fromform','spell_complete_menu',wsgi=True))
    out.append(cgihide('spell_action',action,wsgi=True))
    out.append(formfooter(wsgi=True))
    debuglist(out)
    return '\n'.join(out)
    
def flee_menu(player_index):
    out = [formheader(title="%s attempts to run away" %characters[player_index].displayname(),wsgi=True)]
    out.append(webinput('Does %s get away ?' %characters[player_index].displayname(),'success',['Yes','No'],wsgi=True))
    out.append(cgihide('fromform','flee_menu',wsgi=True))
    out.append(formfooter(wsgi=True))
    return out

def tryability(player_index):
    global characters
    out = [formheader(title="%s tries a special ability" %characters[player_index].displayname(),wsgi=True)]
    out.append(webinput('Ability:','ability',characters[player_index].conditionals().keys(),wsgi=True))
    out.append(webinput('Custom modifier:','modifier','0',wsgi=True))
    out.append(cgihide('fromform','tryability',wsgi=True))
    out.append(formfooter(wsgi=True))
    return out
    
def do_attack(player_index):
    global characters
    characters[player_index].reset_weapon()
    out = [formheader(title="%s is attacking" %characters[player_index].displayname(),wsgi=True)]

    out.append(select_target(player_index,True))
    out.append(webinput('Custom attack modifier','custom_mod','0',wsgi=True))
    out.append('<tr><td bgcolor=lightgray align=left valign=center><b>Attack modifiers:</b></td>')
    out.append( "<td align=center valign=center>")
    for key in attack_mods.keys():
        out.append('<input type=checkbox name="attack_mods[]" value="%s">%s<br>' %(key,key))
    out.append('</td></tr>')
    if characters[player_index].is_misile():
        out.append(webinput('Using a misile weapon - please specify range:','mrange',['Long','Medium','Close'],wsgi=True))
    out.append(cgihide('fromform','do_attack',wsgi=True))
    out.append(formfooter(wsgi=True))
    debuglist(out)
    return '\n'.join(out)
    
def do_damage(player_index,target_index):
    global characters
    dmg_mod=characters[player_index].dmg_mod()
    weapon=characters[player_index].current_weapon()
    hit_dice=characters[player_index].hit_dice()
    dmg=characters[player_index].dmg(weapon)
    save=characters[player_index].weapons[weapon].json['conditionals']['save_against']
    if save != "none":
        throw=characters[player_index].spell_target.saving_throw(save,wsgi=True)
        if throw[0]:
            return (True,throw[1])
    damage=rolldice(characters[player_index].autoroll(),1,dmg,dmg_mod,wsgi=True)
    out=[damage[1]]
    taken=characters[target_index].take_damage(damage[0],wsgi=True)
    out += taken[1]
    return (taken[0],out)
    
@get ('/combat')
@post ('/combat')
def do_round():
    if request.forms.get('more_combat') == 'No':
        return end_combat()
    action=request.forms.get('action')
    fromform=request.forms.get('fromform')
    global player_index
    global characters
    if len(characters) == 0:
        return addchar()
    global rounds
    global upchar
    out=[cgiheader('EZDM-Combat',wsgi=True,linkback=False)]
    if action == "Heal":
        if characters[player_index].is_casting():
            out += characters[player_index].interrupt_cast(wsgi=True)         
        out.append(formheader(title='%s recieves healing' %characters[player_index].displayname,wsgi=True))
        out += dicemenu('Healing')
        out.append(cgihide('fromform','selfheal',wsgi=True))
        out.append(formfooter(wsgi=True))
        return out
    if action == "Cast" or action == "Interrupt spell and cast another":
        if characters[player_index].is_casting():
            out += characters[player_index].interrupt_cast(wsgi=True)                 
        out += do_cast(player_index)
        out.append(cgifooter(wsgi=True))
        debuglist(out)
        return '\n'.join(out)
    
    if action == "Attack":
        if characters[player_index].is_casting():
            out += characters[player_index].interrupt_cast(wsgi=True)
        return do_attack(player_index)
                   
    if action == "Other ability":
        if characters[player_index].is_casting():
            out += characters[player_index].interrupt_cast(wsgi=True) 
        if len(characters[player_index].conditionals()) == 0:
            out += highlight('%s has no special abilities' %characters[player_index].displayname(),sayit=False)
        else:
            return '\n'.join(tryability(player_index))
                
    if action == 'Continue casting spell':
            if not characters[player_index].continue_casting():
                spc=do_spell_complete(player_index)
                if not spc[0]:
                    out += spc[1]
                else:
                    return spc[1]
    if action == "Flee":
            if characters[player_index].is_casting():
               out += characters[player_index].interrupt_cast()     
            out += flee_menu(player_index)
            return '\n'.join(out)
            
    if fromform == "do_attack":
        target=request.forms.get('target')
        target_index=int(target.split(']')[1].split('(')[1].rstrip(')'))
        target_alive=True
        attack_number=1
        mrange=request.forms.get('mrange')
        num_attacks=characters[player_index].num_attacks()
        modifier=int(request.forms.get('custom_mod'))
        out.append('Applying custom modifier %s<br>' %modifier)
        for mod in request.forms.getall('attack_mods[]'):
            imod=int(attack_mods[mod])
            modifier += imod
            out.append('Applying modifier %s (%s), total modifiers now %s<br>' %(mod,imod,modifier))
        if mrange:
            range_mods={'Long':-5,'Medium':-2,'Close':0}
            modifier += int(range_mods[mrange])
            out.append('Applying missile %s-range modifier %s. Modifiers now %s<br>' %(mrange.lower(),range_mods[mrange],modifier))
        while attack_number <= num_attacks and target_alive:
            weapon=characters[player_index].weapons[characters[player_index].weapon].displayname()
            out += highlight("%s is attacking %s with %s! <br> Attack %s of %s" %(characters[player_index].displayname(),characters[target_index].displayname(),weapon,attack_number,num_attacks),sayit=False)
            attack_number += 1
            out.append('Applying weapon/personal modifier %s. '%characters[player_index].to_hit_mod())
            modifier += characters[player_index].to_hit_mod()
            out.append('Modifier now %s' %modifier)
            attack_roll=characters[player_index].attack_roll(characters[target_index],modifier)
            out += highlight("%s<br>%s"%(attack_roll[1],attack_roll[0]),sayit=False)
            if  attack_roll[0]=="Critical Hit !":
                out+=highlight('Critical hit, %s gets an extra attack' %characters[player_index].displayname(),sayit=False)
                num_attacks += 1 #Bonus attack on critical hit
            if "hit" in attack_roll[0].lower():
                if characters[target_index].is_casting():
                    out += characters[target_index].interrupt_cast('by successfull hit')
                damage_result=do_damage(player_index,target_index)
                target_alive=damage_result[0]
                out += damage_result[1]
                if not target_alive:
                    for char in characters:
                        if not char.is_monster():
                            out += char.give_xp(characters[target_index].xp_worth(),wsgi=True)
                    characters[target_index].remove_from_combat()
       
    if fromform == 'flee_menu':
        if request.forms.get('success') == 'Yes':
            characters[player_index].remove_from_combat()
            out += highlight("%s escapes !" %characters[player_index].displayname(),sayit=False)
        else:
            out += highlight("%s does not get away !" %characters[player_index].displayname(),sayit=False)
    
    if fromform == 'selfheal':
        numdice=int(request.forms.get('numdice'))
        sides=int(request.forms.get('sides'))
        mod=int(request.forms.get('mod'))
        amount=rolldice(auto=True,numdice=numdice,numsides=sides,modifier=mod,wsgi=True)
        out.append(amount[1])
        out += characters[player_index].heal(amount[0],wsgi=True)        
            
    if fromform == 'tryability':
        ability=request.forms.get('ability')
        modifier=int(request.forms.get('modifier'))
        attempt=characters[player_index].tryability(ability,modifier,wsgi=True)
        out.append("%s<br>" %('<br>'.join(attempt[1])))
        if attempt[0]:
            out.append("%s succeeded with %s" %(characters[player_index].displayname(),ability))
        else:
            out.append("%s failed at %s" %(characters[player_index].displayname(),ability))
    if fromform == 'spell_complete':
        spell_action=request.forms.get('spell_action')
        if spell_action == 'Other (DM to handle)':
            out += highlight('Spell action unknown: DM to handle please',sayit=False)
        else:
            return spell_complete_menu(request.forms.get('spell_action'),player_index)
    if fromform == 'spell_complete_menu':
        spell_action=request.forms.get('spell_action')
        out += highlight('%s spell completed' %characters[player_index].displayname(),sayit=False)
        numdice=int(request.forms.get('numdice'))
        sides=int(request.forms.get('sides'))
        mod=int(request.forms.get('mod'))
        print "Numdice: %s, Sides: %s, Modifier: %s" %(numdice,sides,mod)
        if spell_action == 'Heal':
            amount=rolldice(auto=True,numdice=numdice,numsides=sides,modifier=mod,wsgi=True)
            out.append(amount[1])
            out += characters[player_index].spell_target.heal(amount[0],wsgi=True)
        else:
            damage=rolldice(auto=True,numdice=numdice,numsides=sides,modifier=mod,wsgi=True)
            out.append(damage[1])
            damage_result=characters[player_index].spell_target.take_damage(damage[0],wsgi=True)
            out += damage_result[1]
            if not damage_result[0]:
                characters[player_index].spell_target.remove_form_combat()
            
    if fromform == 'do_cast':
        num=int(request.forms.get('cast_time'))
        if request.forms.get('use_turns') == 'Turns':
            num *= 10
        target=request.forms.get('target')
        target_index=int(target.split(']')[1].split('(')[1].rstrip(')'))
        characters[player_index].start_casting(num,characters[target_index])
        out.append('%s has started casting a spell on %s' %(characters[player_index].displayname(),characters[target_index].displayname()))

    out+=highlight('Entering combat turn: %s round: %s' %(turns(),rounds),sayit=False)
    if upchar == -1:
        out+=highlight('Rolling for initiative',sayit=False)
        out.append(roll_for_initiative())
    print initiative        
    print "Last Upchar:",upchar
    upchar += 1
    if len(in_combat()) == 1:
        out += highlight('Combat completed<br>%s was last man standing' %in_combat()[0].displayname(),sayit=False)
        out.append('<a href="/">Home</a>')
        initialize()
        return out
    if len(in_combat()) < 1:
        out += highlight('Combat completed',sayit=False)
        out.append('<a href="/">Home</a>')
        initialize()
        return out
    
    if upchar > len(initiative)-1:
        return next_round(out)
    print "Next Upchar:",upchar
    out += show_in_combat()
    player_index=initiative[upchar][1]
    out.append("%s goes next" %(characters[player_index].displayname()))
    actionlist=["Attack","Flee","Cast","Heal","Other ability"]
    if characters[player_index].is_casting():
        out += highlight('Warning %s is casting a spell. %s rounds left.' %(characters[player_index].displayname(),characters[player_index].cast_remaining),clear=False,sayit=False)
        del actionlist[2]
        actionlist.append('Continue casting spell')
        actionlist.append('Interrupt spell and cast another')    
    out.append(formheader(action='/combat',wsgi=True))
    out.append(webinput('What happens','action',actionlist,wsgi=True))
    out.append(formfooter(wsgi=True))
    out.append(cgifooter(linkback=False,wsgi=True))
    debuglist(out)
    return out


@get('/testserver')
def testserver():
    return 
    
@get ('/ezdm.cgi')
@get ('/addchar')
@post ('/addchar')
def addchar_submit():
    out=[]
    addmore=request.forms.get('addmore')
    if addmore == 'No':
        return do_round()
    name=request.forms.get('character')
    if not name or len(name) == 0:
        return addchar()
    autodice=request.forms.get('autodice') == 'Yes'
    clist=list_chars()
    out+=highlight('Adding %s to combat' %name,sayit=False)
    c=Character(load_json('characters',clist[name]),autodice,QuietDice=False)
    characters.append(c)
    c.set_index(characters.index(characters[-1]))
    out.append(addchar())
    return '\n'.join(out)

@route('/')
def main():
    global characters
    if len(characters) == 0:
        return addchar()
    else:
        return cgiheader('EZDM-Combat',wsgi=True,linkback=False)

run(host='',port=8001,server='gevent')


