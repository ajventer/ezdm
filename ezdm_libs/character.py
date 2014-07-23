from util import rolldice,readfile,inrange,price_in_copper,convert_money, find_files, save_json
import sys
import datetime
import os
from glob import glob
from random import randrange
from item import Item

class Character:
    removed=False
    cast_remaining=0
    spell_target=None
    json={}
    auto=False
    index=-1
    weapon=0
    weapons=[]
    armor=[]
    def __init__(self,json,autoroll=False,QuietDice=True):
        self.json=json
        self.weapons=self.load_weapons()
        self.armor=self.load_armor()
        self.json['combat']['thac0']=self.__get_thac0()
        self.auto=autoroll
        self.json['combat']['saving_throws']=self.__get_saving_throws()
        if self.is_monster():
            self.json['combat']['hitpoints']=rolldice(self.auto,int(self.json['combat']["level/hitdice"]),8,quiet=QuietDice)
            self.json['combat']["max_hp"]=self.json['combat']['hitpoints']
    
    def remove_from_combat(self):
        self.removed = True
        
    def xp_worth(self):
        xpkey=self.json['combat']['level-hitdice']
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
        

    def heal(self,amount,wsgi=False):
        hp=int(self.json['combat']['hitpoints'])
        hp += amount
        if hp > int(self.json['combat']['max_hp']):
            self.json['combat']['hitpoints'] = int(self.json['combat']['max_hp'])
        else:
            self.json['combat']['hitpoints'] = hp
        if not wsgi:
            highlight("%s receives healing. Hitpoints now %s" %(self.displayname(),self.json['combat']['hitpoints']),clear=False)
            self.save()
        else:
            self.save()
            return highlight("%s receives healing. Hitpoints now %s" %(self.displayname(),self.json['combat']['hitpoints']),clear=False,sayit=False)
        
    def take_damage(self,damage,wsgi=False):
        out=[]
        if damage >= int(self.json['combat']['hitpoints']):
            st=self.saving_throw('ppd',wsgi=True)
            out = st[1]
            if not st[0]: #Roll saving throw against death
                self.json['combat']['hitpoints'] = 0
                self.save()
                out += highlight("%s has died !" %self.displayname(),clear=False,sayit=False)
                if not wsgi:
                    say(out)
                    return False
                else:
                    return (False,out)
            else:
                self.json['combat']['hitpoints'] = 1
                self.save()
                out += highlight("%s barely survives. %s hitpoints remaining" %(self.displayname(),self.json['combat']['hitpoints']),clear=False,sayit=False)
                if not wsgi:
                    say(out)
                    return True
                else:
                    return (True,out)
        else:
            hp=int(self.json['combat']['hitpoints'])
            hp -= damage
            self.json['combat']['hitpoints'] =hp
            self.save()
            out += highlight("%s takes %s damage. %s hitpoints remaining" %(self.displayname(),damage,self.json['combat']['hitpoints']),clear=False,sayit=False)
            if not wsgi:
                say (out)
                return True
            else:
                return (True,out)
        
        
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
        
    def interrupt_cast(self,by='',wsgi=False):
        self.spell_complete()
        if not wsgi:
            highlight('%s: spell casting interrupted %s !' %(self.displayname(),by),clear=False)
        else:
            return highlight('%s: spell casting interrupted %s !' %(self.displayname(),by),clear=False,sayit=False)
    
    def spell_complete(self):
        self.cast_remaining = 0
        self.spell_target = None
        
    def spell_friendly_target(self):
        return self.is_monster() == self.spell_target.is_monster()
    
    def basename(self):
        firstname=self.json["personal"]["name"]["first"].upper()
        lastname=self.json["personal"]["name"]["last"].upper()
        return "%s_%s" %(firstname,lastname)
            
    def filename(self):
        return "%s.json" %(self.basename())
    
    def save(self):
        if 'temp' in self.json:
            del self.json['temp']
        save_json('characters', self._filename(), self.get_json())
        
    def update(self,json,save=True):
        self.json=json
        if save:
            self.save()
            
    def to_hit_mod(self):
        ability_mods=load_json('adnd2e','ability_scores')
        base=int(ability_mods["str"][str(self.json['abilities']['str'])]['hit'])
        if len(self.weapons) > 0:
            bonus=int(self.weapons[self.weapon].json.get("conditionals", {"tohit":0}).get('tohit', 0))
        else:
            bonus=0
        return base+bonus

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
                
    def saving_throw(self,against,wsgi=False):
        saving=load_json('adnd2e','saving_throws') or {}
        prettyname=saving['names'][against]
        race=self.json['personal']['race']
        con=int(self.json['abilities']['con'])
        mod=0
        if race in saving.keys():
            for key in saving[race].keys():
                if inrange(con,key):
                    mod=int(saving[race][key])
                    continue
        target=int(self.json['combat']['saving_throws'][against])
        out=["%s Tries to roll a saving throw against %s" %(self.displayname(),prettyname),"%s needs to roll %s" %(self.displayname(),target)]
        roll=rolldice(self.auto,1,20,mod,wsgi=True)
        out.append(roll[1])
        if roll[0] >= int(target):
            out.append('Saved !')
            return (True,out)
        else:
            out.append("Did not save !")
            return (False,out)
        
    def dmg(self,weapon):
        return int(self.weapons[weapon].json['conditionals']['dmg'])
    
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

    def give_xp(self,xp,wsgi=False):
        current_xp=int(self.json['personal']['xp'])
        new_xp=current_xp+int(xp)
        self.json['personal']['xp'] = str(new_xp)
        return str(new_xp)
        
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

    def is_misile(self):
        try:
            return self.weapons[self.weapon]['conditionals']['weapon_type'] == "misile"
        except IndexError:
            return False
 
    def attack_roll(self,target,mod):
        self.next_weapon() 
        roll=rolldice(self.autoroll(),1,20,mod,wsgi=True)
        if roll[0] - mod == 1:
                return ("Critical Miss !",roll[1])
        elif roll[0] - mod == 20:
            return ("Critical Hit !",roll[1])
        else:
            if roll[0] >= self.__get_thac0() - target.armor_class() - int(target.def_mod()):
                return ("Hit !",roll[1])
            else:
                return ("Miss !",roll[1])
    
    def spell_success(self,wsgi=False):
        ability_scores=load_json('adnd2e','ability_scores')
        wis=str(self.json['abilities']['wis'])
        failrate=int(ability_scores["wis"][wis]["spell_failure"].split('%')[0])
        out=["Spell failure rate: %s percent" %failrate]
        roll=rolldice(self.autoroll(),1,100,wsgi=True)
        out.append(roll[1])
        if roll[0] > failrate:
            out += highlight('Spell succeeds !',clear=False,sayit=False)
            return (True,out)
        else:
            out += highlight('Spell fails !',clear=False,sayit=False)
            self.spell_complete()
            return(False,['<br'.join(out)])
    
    def load_weapons(self):
        weap=[]
        if not "inventory" in self.json or not "equiped" in self.json["inventory"]:
            return []
        if type(self.json['inventory']['equiped']) <> type([]):
            self.json['inventory']['equiped']=[]
        if type(self.json['inventory']['pack']) <> type([]):
            self.json['inventory']['pack']=[]
        for item in self.json['inventory']['equiped']:
            i=Item(item)
            if i.json['type'] == 'weapon':
                weap.append(i)
        return weap

    def acquire_item(self,item):
        #self.json=item.events.OnPickup(self.json)
        self.json['inventory']['pack'].append(readfile('items', item, json=True))
        
    def equip_item(self,itemname):
        index = 0
        for i in readkey('/inventory/pack', self.json, []):
            if i['name'] == itemname:
                break
            else:
                index += 1
        self.json['inventory']['equiped'].append(i)
        del self.json['inventory']['pack'][index]
        

    def unequip_item(self,itemname):
        index = 0
        for i in readkey('/inventory/equiped', self.json, []):
            if i['name'] == itemname:
                break
            else:
                index += 1
        self.json['inventory']['pack'].append(i)
        del self.json['inventory']['equiped'][index]
        
    def drop_item(self,itemname):
        index=0
        for i in readkey('/inventory/pack', self.json, []):
            if i['name'] == itemname:
                break
            else:
                index += 1
        del (self.json['inventory']['pack'][index])
        
    def list_inventory(self,sections=['pack','equiped']):
        result=[]
        for section in sections:
                if type(self.json['inventory'][section]) != type([]) and type(self.json['inventory'][section]) != type({}):
                    self.json['inventory'][section] = []
                result = list(result+self.json['inventory'][section])
        return result
    
    def spend_money(self,gold=0,silver=0,copper=0):
        ihave=price_in_copper(int(self.json['inventory']['money']['gold'] or '0'),int(self.json['inventory']['money']['silver'] or '0'),int(self.json['inventory']['money']['copper'] or '0'))
        price=price_in_copper(gold,silver,copper)
        remains=ihave-price
        if remains < 0:
            return False
        else:
            self.json['inventory']['money']=convert_money(remains)
            self.save()
            return True
        
    def buy_item(self,item):
        if not 'price' in item.json.keys():
            price={"gold":0,"silver":0,"copper":0}
        else:
            price=item.json['price']
        if self.spend_money(int(price['gold']),int(price['silver']),int(price['copper'])):
            self.acquire_item(item)
            return True
        else:
            return False
        
    def gain_money(self,gold=0,silver=0,copper=0):
        total_gained=price_in_copper(gold,silver,copper)
        my_total=price_in_copper(int(self.json['inventory']['money']['gold'] or '0'),int(self.json['inventory']['money']['silver'] or '0'),int(self.json['inventory']['money']['copper'] or '0'))
        my_total += total_gained
        self.json['inventory']['money'] = convert_money(my_total)
        self.save()
        
        
    def armor_class(self):
        AC=10
        for item in self.armor:
            AC -= int(item.json["conditionals"]["ac"])
        return AC
    
    def load_armor(self):
        arm=[]
        if not "inventory" in self.json or not "equiped" in self.json["inventory"]:
            return []
        for item in self.list_inventory(['equiped']):
            if item['type'] == 'armor':
                arm.append(i)
        return arm
        
    def num_weapons(self): 
        return len(self.weapons)
        
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
    
    def tryability(self,ability,modifier=0,wsgi=False):
        out=['%s is trying to %s' %(self.displayname(),ability)]
        target_roll=int(self.conditionals()[ability])
        target_roll += int(modifier)
        out.append('%s must roll %s or lower to succeed' %(self.displayname(),target_roll))
        roll=rolldice(self.autoroll(),1,100,wsgi=True)
        out.append(roll[1])
        if roll[0] <= target_roll:
            return (True,out)
        else:
            return (False,out)

        
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
                if type(conditionals[ability]) == type('') and len(conditionals[ability]) >0:
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
        for key in conditionals:
            race=self.json['personal']['race']
            racial_bonos=0
            if "racial_bonus" in various['abilities'][key] and race in various['abilities'][key]["racial_bonus"]: 
                racial_bonus=int(various['abilities'][key]["racial_bonus"][race])
            dex=self.json['abilities']['dex']
            dex_bonus=0
            if "dexterity bonus" in various['abilities'][key]:
                for d in various['abilities'][key]["dexterity bonus"]:
                    if inrange(dex,d):
                        dex_bonus=int(various['abilities'][key]["dexterity bonus"][d])
                        continue
            if type(conditionals[key]) == type('') and len(conditionals[key]) == 0:
                conditionals[key]=0
            if int(conditionals[key]) > 0:
                conditionals[key] = int(conditionals[key]) + dex_bonus + racial_bonus
        return conditionals
      

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

