from util import smart_input,highlight,rolldice,load_json,inrange
import sys
import datetime
import os
from simplejson import loads,dumps
from glob import iglob
from random import randrange
from pprint import pprint

def list_chars(exclude=[],monsters=True):
    chars={}
    
    for entry in iglob("characters/*.json"):
        cname=os.path.basename(entry).rstrip('.json')
        char=Character(load_json('characters',cname),True)
        if not cname in exclude:
            if monsters:
                chars[char.displayname()]=cname
            elif not char.is_monster():
                    chars[char.displayname()]=cname
    return chars

class Character:
    removed=False
    cast_remaining=0
    spell_target=None
    json={}
    auto=False
    index=-1
    weapon=0
    def __init__(self,json,autoroll=False):
        self.json=json

        self.json['combat']['thac0']=self.__get_thac0()
        self.auto=autoroll
        self.json['combat']['saving_throws']=self.__get_saving_throws()
        if self.is_monster():
            self.json['combat']['hitpoints']=rolldice(self.auto,int(self.json['combat']["level/hitdice"]),8)
            self.json['combat']["max_hp"]=self.json['combat']['hitpoints']
    
    def remove_from_combat(self):
        self.removed = True
    
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
            self.json['combat']['hitpoints'] -= damage
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

        
           
    def save(self):
        if 'temp' in self.json:
            del self.json['temp']
        open('%s/%s.json' %('characters',self.json["personal"]["name"]["first"].upper()),'w').write(dumps(self.json,indent=4))
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
        target=self.json['combat']['saving_throws'][against]
        print "%s Tries to roll a saving throw against %s" %(self.displayname(),prettyname)
        print "%s needs to roll %s" %(self.displayname(),target)
        if rolldice(self.auto,1,20) >= target:
            print "Saved !"
            return True
        else:
            print "Did not save !"
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
        self.json['personal']['xp'] += xp
        highlight("%s now has %s XP" %(self.displayname(),self.json['personal']['xp']))
        self.save()
      
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
        print "Spell failure rate: %s percent" %failrate
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
        return self.num_weapons() *int(self.json['combat']['atacks_per_round'])
      
    def pprint(self):
        highlight("%s" %self.displayname())
        print "Alignment: %s-%s" %(self.json['personal']['alignment']['law'],self.json['personal']['alignment']['social'])
        print "Race: %s" %self.json['personal']['race']
        print "Class %s:%s" %(self.json['class']['parent'],self.json['class']['class'])
        print "XP %s/%s" %(self.json['personal']['xp'],'TODO')
        print "Combat stats:"
        for key in self.json['combat']:
            if key not in ['weapons','saving_throws']:
                print "    %s: %s" %(key,self.json['combat'][key])
        print "    Saving throws:"
        print "         ",
        for key in self.json['combat']['saving_throws']:
            prettyname=load_json('adnd2e','saving_throws')['names'][key]
            print "[%s: %s] " %(prettyname,self.json['combat']['saving_throws'][key]),
        print
        print "Ability scores:"
        for key in self.json['abilities']:
            print "     %s: %s" %(key,self.json['abilities'][key])
        print "Total attacks per round: %s" %self.num_attacks()
        print "Weapons: %s" %self.num_weapons()
        for key in self.json['combat']['weapons']:
            print "     Weapon: %s" %key
            print "         ",
            for stat in self.json['combat']['weapons'][key]:
                print "[%s: %s]" %(stat,self.json['combat']['weapons'][key][stat]),
            print
        print
        print "Modifiers(first weapon):"
        print "     Chance to hit: %s" %self.to_hit_mod()
        print "     Damage: %s" %self.dmg_mod()
        print "     Defense (modifies AC down): %s" %self.def_mod()
        print "     PPD Save: %s" %self.ppd_mod()

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
