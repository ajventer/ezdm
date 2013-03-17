from util import smart_input,highlight,rolldice,load_json,inrange,say,get_user_data
import sys
import datetime
import os
from simplejson import loads,dumps
from glob import iglob
from random import randrange
from pprint import pprint

def list_chars(exclude=[],monsters=True):
    chars={}
    for entry in iglob(os.path.join(get_user_data('characters'),"*.json")):
        cname=os.path.basename(entry).rstrip('.json')
        char=Character(load_json('characters',cname),True)
        if not cname in exclude:
            if monsters:
                chars[char.displayname()]=cname
            elif not char.is_monster():
                    chars[char.displayname()]=cname
    if len(chars) == 0:
        say('Note: you have not created any characters yet')
    return chars

class Character:
    removed=False
    cast_remaining=0
    spell_target=None
    json={}
    auto=False
    index=-1
    weapon=0
    def __init__(self,json,autoroll=False,QuietDice=True):
        self.json=json

        self.json['combat']['thac0']=self.__get_thac0()
        self.auto=autoroll
        self.json['combat']['saving_throws']=self.__get_saving_throws()
        if self.is_monster():
            self.json['combat']['hitpoints']=rolldice(self.auto,int(self.json['combat']["level/hitdice"]),8,quiet=QuietDice)
            self.json['combat']["max_hp"]=self.json['combat']['hitpoints']
    
    def remove_from_combat(self):
        self.removed = True
        
    def xp_worth(self):
        xpkey=self.json['combat']['level/hitdice']
        xpvalues=load_json('adnd2e','creature_xp') or {}
        if str(xpkey) in xpvalues.keys():
            xp=xpvalues[str(xpkey)]
        elif int(xpkey) > 12:
            xp=3000+((int(xpkey)-13)*1000)
        return int(xp)
            
    
    def set_index(self,index):
        self.index=index
        
    def get_json(self):
        return self.json
        
    def heal(self,amount):
        self.json['combat']['hitpoints'] += amount
        if amount > self.json['combat']['max_hp']:
            self.json['combat']['hitpoints'] = self.json['combat']['max_hp']
        highlight("%s receives healing. Hitpoints now %s" %(self.displayname(),self.json['combat']['hitpoints']),clear=False)
        self.save()
        
    def take_damage(self,damage):
        if damage >= int(self.json['combat']['hitpoints']):
            if not self.saving_throw('ppd'): #Roll saving throw against death
                self.json['combat']['hitpoints'] = 0
                self.save()
                highlight("%s has died !" %self.displayname(),clear=False)
                return False
            else:
                self.json['combat']['hitpoints'] = 1
                self.save()
                highlight("%s barely survives. %s hitpoints remaining" %(self.displayname(),self.json['combat']['hitpoints']),clear=False)
                return True
        else:
            hp=int(self.json['combat']['hitpoints'])
            hp -= damage
            self.json['combat']['hitpoints'] =hp
            self.save()
            highlight("%s takes %s damage. %s hitpoints remaining" %(self.displayname(),damage,self.json['combat']['hitpoints']),clear=False)
            return True
        
        
    def is_monster(self):
        return self.json["personal"]['race'] in ['creature','monster']
        
    def start_casting(self,rounds,target):
        self.cast_remaining=rounds
        self.spell_target=target
    
    def continue_casting(self):
        self.cast_remaining -= 1
        return self.is_casting()
    
    def is_casting(self):
        return self.cast_remaining > 0
        
    def interrupt_cast(self,by=''):
        highlight('%s: spell casting interrupted %s !' %(self.displayname(),by),clear=False)
        self.spell_complete()
    
    def spell_complete(self):
        self.cast_remaining = 0
        self.spell_target = None
        
    def spell_friendly_target(self):
        return self.is_monster() == self.spell_target.is_monster()
    
    def filename(self):
        firstname=self.json["personal"]["name"]["first"].upper()
        lastname=self.json["personal"]["name"]["last"].upper()
        return "%s_%s.json" %(firstname,lastname)
    
    def save(self):
        if 'temp' in self.json:
            del self.json['temp']
        open(os.path.join(get_user_data('characters'),self.filename()),'w').write(dumps(self.json,indent=4))
        highlight('%s status saved to disk' %self.displayname(),clear=False)
        
    def update(self,json,save=True):
        self.json=json
        if save:
            self.save()
            
    def to_hit_mod(self):
        ability_mods=load_json('adnd2e','ability_scores')
        return int(ability_mods["str"][str(self.json['abilities']['str'])]['hit'])

    def ppd_mod(self):
        ability_mods=load_json('adnd2e','ability_scores')
        return int(ability_mods["con"][str(self.json['abilities']['con'])]['ppd'])
    
    def dmg_mod(self):
        ability_mods=load_json('adnd2e','ability_scores')
        return int(ability_mods["str"][str(self.json['abilities']['str'])]['dmg'])
    
    def def_mod(self):
        ability_mods=load_json('adnd2e','ability_scores')
        return int(ability_mods["dex"][str(self.json['abilities']['dex'])]['defense'])
        
    def __get_saving_throws(self):
        key=self.json['class']['parent']
        sts=load_json("adnd2e","saving_throws")[key]
        for key2 in sts.keys():
            if inrange(self.json['combat']["level/hitdice"],key2):
                st=sts[key2]
                st['ppd']=int(st['ppd']) + self.ppd_mod()
                return(st)
                
    def saving_throw(self,against):
        prettyname=load_json('adnd2e','saving_throws')['names'][against]
        target=int(self.json['combat']['saving_throws'][against])
        say ("%s Tries to roll a saving throw against %s" %(self.displayname(),prettyname))
        say ("%s needs to roll %s" %(self.displayname(),target))
        if int(rolldice(self.auto,1,20)) >= int(target):
            say ("Saved !")
            return True
        else:
            say ("Did not save !")
            return False
        
    def dmg(self,weapon):
        return int(self.json['combat']['weapons'][str(weapon)]['dmg'])
    
    def hit_dice(self):
        if self.is_monster():
            return int(self.json['combat']['level/hitdice'])
        else:
            return 1
        
    def autoroll(self):
        return self.auto
            
    def current_weapon(self):
        return self.weapon
        
    def reset_weapon(self):
        self.weapon=0
        
    def next_weapon(self):
        self.weapon += 1
        if self.weapon > self.num_weapons() -1:
            self.weapon = 0

    def give_xp(self,xp):
        current_xp=int(self.json['personal']['xp'])
        new_xp=current_xp+int(xp)
        self.json['personal']['xp'] = str(new_xp)
        highlight("%s now has %s XP" %(self.displayname(),self.json['personal']['xp']))
        self.save()
        
    def next_level(self):
        parentclass=self.json['class']['parent']
        childclass=self.json['class']['class']
        nl=int(self.json['combat']['level/hitdice'])+1
        xp_levels=load_json('adnd2e','xp_levels')[parentclass][str(nl)]
        if 'all' in xp_levels:
            next_xp=int(xp_levels['all'])
        else:
            next_xp=int(xp_levels[childclass])
        return next_xp
    
        
      
    def is_misile(self,weaponidx):
        return self.json['combat']['weapons'][str(weaponidx)]['type'] == "misile"
        
    def attack_roll(self,target,mod):
        self.next_weapon() 
        roll=rolldice(self.autoroll(),1,20,mod)
        if roll - mod == 1:
            return "Critical Miss !"
        elif roll - mod == 20:
            return "Critical Hit !"
        else:
            if roll >= self.__get_thac0() - (int(target.json['combat']['armor_class']) - target.def_mod()):
                return "Hit !"
            else:
                return "Miss !"
    
    def spell_success(self):
        ability_scores=load_json('adnd2e','ability_scores')
        wis=str(self.json['abilities']['wis'])
        failrate=int(ability_scores["wis"][wis]["spell_failure"].split('%')[0])
        say ("Spell failure rate: %s percent" %failrate)
        roll=rolldice(self.autoroll(),1,100)
        if roll > failrate:
            highlight('Spell succeeds !',clear=False)
            return True
        else:
            highlight('Spell fails !',clear=False)
            self.spell_complete()
            return False

    def num_weapons(self): 
        return len(self.json['combat']['weapons'])
        
    def num_attacks(self):
        atr=load_json('adnd2e','various')['various']['attacks_per_round']
        parentclass=self.json['class']['parent']
        if not parentclass in atr:
            ATR=1
        else:
            for key in atr[parentclass].keys():
                if inrange(self.json['combat']['level/hitdice'],key):
                   ATR=int(atr[parentclass][key])
        return self.num_weapons() *int(ATR)
    
    def current_xp(self):
        return int(self.json['personal']['xp'])
    
    def tryability(self,ability):
        target_roll=int(self.conditionals()[ability])
        roll=rolldice(self.autoroll(),1,100)
        if roll >= target_roll:
            return True
        else:
            return False
        
    def conditionals(self):
        subclass=self.json['class']['class']
        parentclass=self.json['class']['parent']
        level=self.json['combat']['level/hitdice']        
        various=load_json('adnd2e','various')
        abilities=various['abilities']
        if not 'conditionals' in self.json:
            self.json['conditionals'] = {}
        conditionals={}    
        for conditional in self.json['conditionals'].keys():
            conditionals[conditional] = self.json['conditionals'][conditional]
        for ability in abilities.keys():
            base=0
            if ability in conditionals:
                base=int(conditionals[ability])               
            if subclass in abilities[ability]:
                for key in abilities[ability][subclass].keys():
                    if inrange(level,key):
                        base += int(abilities[ability][subclass][key])
                        continue
            elif parentclass in abilities[ability]:
                for key in abilities[ability][parentclass].keys():
                    if inrange(level,key):
                        base += int(abilities[ability][parentclass][key])
                        continue
            if base > 0:
                race=self.json['personal']['race']
                if race in abilities[ability]:
                    base += int(abilities[ability][race])
                conditionals[ability] = base  
        return conditionals
      
    def pprint(self):
        out =highlight(self.displayname(),sayit=False)
        out.append("Level: %s " %self.json['combat']['level/hitdice'])
        out.append( "XP %s/%s" %(self.current_xp(),self.next_level()))
        out.append( "Class %s:%s" %(self.json['class']['parent'],self.json['class']['class']))
        out.append( "Alignment: %s-%s" %(self.json['personal']['alignment']['law'],self.json['personal']['alignment']['social']))
        out.append( "Race: %s" %self.json['personal']['race'])
        if self.is_monster():
            out.append( "XP Worth: %s" %self.xp_worth())
        out.append( "Combat stats:")
        for key in self.json['combat']:
            if key not in ['weapons','saving_throws','level/hitdice']:
                out.append("    %s: %s" %(key,self.json['combat'][key]))
        out.append( "    Saving throws:")
        line='      '
        for key in self.json['combat']['saving_throws']:
            prettyname=load_json('adnd2e','saving_throws')['names'][key]
            line="%s [%s: %s] " %(line,prettyname,self.json['combat']['saving_throws'][key])
        out.append(line)
        out.append( "Ability scores:")
        
        for key in self.json['abilities']:
            out.append( "   %s: %s" %(key,self.json['abilities'][key]))
        out.append( "Total attacks per round: %s" %self.num_attacks())
        out.append( "Weapons: %s" %self.num_weapons())
        line='      '
        for key in self.json['combat']['weapons']:
            out.append( "Weapon: %s" %key)
            for stat in self.json['combat']['weapons'][key]:
                line="%s[%s: %s]" %(line,stat,self.json['combat']['weapons'][key][stat])
        out.append(line)
        out.append( "Modifiers(first weapon):")
        out.append( "Chance to hit: %s" %self.to_hit_mod())
        out.append( "     Damage: %s" %self.dmg_mod())
        out.append( "     Defense (modifies AC down): %s" %self.def_mod())
        out.append( "     PPD Save: %s" %self.ppd_mod())
        
        out.append('Abilities:')
        various=load_json('adnd2e','various')
        abilities=various['abilities']

        subclass=self.json['class']['class']
        parentclass=self.json['class']['parent']
        level=self.json['combat']['level/hitdice']
    
        conditionals=self.conditionals()
        for con in conditionals.keys():
            out.append('    %s:%s percent' %(con,conditionals[con]))
        out.append('Spell capability:')
        spell_progression=various["spell progression"]
        checkclass=None
        if subclass in spell_progression:
            checkclass=subclass
        elif parentclass in spell_progression:
            checkclass=parentclass
        if checkclass:
            for key in spell_progression[checkclass].keys():
                if inrange(level,key):
                    out.append('   Casting Level: %s' %(spell_progression[checkclass][key]["casting_level"]))
                    if "priest spells" in spell_progression[checkclass][key]:
                        line='   Priest spells:'
                        for spell_level in sorted(spell_progression[checkclass][key]["priest spells"].keys()):
                            line=line+' level %s - number %s ' %(spell_level,spell_progression[checkclass][key]["priest spells"][spell_level])
                        out.append(line)
                    if "wizard spells" in spell_progression[checkclass][key]:
                        line='   Wizard spells:'
                        for spell_level in sorted(spell_progression[checkclass][key]["wizard spells"].keys()):
                            line=line+' level %s - number %s ' %(spell_level,spell_progression[checkclass][key]["wizard spells"][spell_level])
                        out.append(line)
                    
        return(out)


    def displayname(self):
        out="%s %s" %(self.json['personal']['name']['first'],self.json['personal']['name']['last'])
        if self.index > -1:
            out="%s (%s)" %(out,self.index)
        out="[%s]" %out
        return out
         
    def __get_thac0(self):
        if self.json['personal']['race'] == "creature":
            key="creature"
        else:
            key=self.json['class']['parent']
        thac0s=load_json("adnd2e","thac0")[key]
        for key2 in thac0s.keys():
            if inrange(self.json['combat']["level/hitdice"],key2):
                return int(thac0s[key2])
