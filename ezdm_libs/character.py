from util import smart_input,highlight,rolldice,load_json,inrange,say,get_user_data,price_in_copper,convert_money
import sys
import datetime
import os
from simplejson import loads,dumps
from glob import iglob
from random import randrange
from pprint import pprint
from item import Item

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
        
<<<<<<< HEAD
    def heal(self,amount):
=======
    def heal(self,amount,wsgi=False):
>>>>>>> web
        hp=int(self.json['combat']['hitpoints'])
        hp += amount
        if hp > int(self.json['combat']['max_hp']):
            self.json['combat']['hitpoints'] = int(self.json['combat']['max_hp'])
        else:
            self.json['combat']['hitpoints'] = hp
<<<<<<< HEAD
        highlight("%s receives healing. Hitpoints now %s" %(self.displayname(),self.json['combat']['hitpoints']),clear=False)
        self.save()
=======
        if not wsgi:
            highlight("%s receives healing. Hitpoints now %s" %(self.displayname(),self.json['combat']['hitpoints']),clear=False)
            self.save()
        else:
            self.save()
            return highlight("%s receives healing. Hitpoints now %s" %(self.displayname(),self.json['combat']['hitpoints']),clear=False,sayit=False)
>>>>>>> web
        
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
        base=int(ability_mods["str"][str(self.json['abilities']['str'])]['hit'])
        if len(self.weapons) > 0:
            bonus=int(self.weapons[self.weapon].json["conditionals"]["to_hit"])
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
        if not wsgi:
            say ("%s Tries to roll a saving throw against %s" %(self.displayname(),prettyname))
            say ("%s needs to roll %s" %(self.displayname(),target))
        else:
            out=["%s Tries to roll a saving throw against %s" %(self.displayname(),prettyname),"%s needs to roll %s" %(self.displayname(),target)]
        roll=rolldice(self.auto,1,20,mod,wsgi=True)
        out.append(roll[1])
        if roll[0] >= int(target):
            if not wsgi:
                say ("Saved !")
                return True
            else:
                out.append('Saved !')
                return (True,out)
        else:
            if not wsgi:
                say ("Did not save !")
                return False
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
        out=highlight("%s now has %s XP" %(self.displayname(),self.json['personal']['xp']),sayit=False)
        self.save()
        if not wsgi:
            say(out)
        else:
            return out
        
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
        return self.weapons[self.weapon].json['conditionals']['weapon_type'] == "misile"
        
    def attack_roll(self,target,mod):
        #on_use=self.weapons[self.weapon].events.OnUse(self.json,target.json)
        #self.json=on_use['character']
        #target.json=on_use['target']
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
            if not wsgi:
                say (out)
                return True
            else:
                return (True,out)
        else:
            out += highlight('Spell fails !',clear=False,sayit=False)
            self.spell_complete()
            if not wsgi:
                say (out)
                return False
            else:
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
            i=Item(load_json(get_user_data('items'),item))
            if i.json['type'] == 'weapon':
                weap.append(i)
        return weap

    def acquire_item(self,item):
        #self.json=item.events.OnPickup(self.json)
        self.json['inventory']['pack'].append(item.filename(extension=None))
        
    def equip_item(self,itemname):
        item=Item(load_json('items',itemname))
        #self.json=item.events.OnEquip(self.json)
        index=self.json['inventory']['pack'].index(itemname)
        del self.json['inventory']['pack'][index]
        self.json['inventory']['equiped'].append(itemname)

    def unequip_item(self,itemname):
        item=Item(load_json('items',itemname))
        #self.json=item.events.OnUnEquip(self.json)
        index=self.json['inventory']['equiped'].index(itemname)
        del self.json['inventory']['equiped'][index]
        self.json['inventory']['pack'].append(itemname)
        
    def drop_item(self,itemname):
        item=Item(load_json('items',itemname))
        #self.json=item.events.OnDrop(self.json)

        index=self.json['inventory']['pack'].index(itemname)
        del self.json['inventory']['pack'][index]
        
    def list_inventory(self,sections=['pack','equiped']):
        result=[]
        for section in sections:
                if type(self.json['inventory'][section]) != type([]) and type(self.json['inventory'][section]) != type({}):
                    self.json['inventory'][section] = []
                result = list(result+self.json['inventory'][section])
        return result
    
    def list_money(self):
        return "Gold: %s, Silver: %s, Copper: %s" %(self.json['inventory']['money']['gold'],self.json['inventory']['money']['silver'],self.json['inventory']['money']['copper'])

    
    
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
            i=Item(load_json(get_user_data('items'),item))
            if i.json['type'] == 'armor':
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
            if not wsgi:
                say(out)
                return True
            else:
                return (True,out)
        else:
            if not wsgi:
                say(out)
                return False
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
        out.append("    Armor class: %s" %self.armor_class())
        for key in self.json['combat']:
            if key not in ['saving_throws','level/hitdice']:
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
        out.append(line)
        out.append( "Modifiers(first weapon):")
        out.append( "Chance to hit: %s" %self.to_hit_mod())
        out.append( "     Damage: %s" %self.dmg_mod())
        out.append( "     Defense (modifies AC down): %s" %self.def_mod())
        out.append( "     PPD Save: %s" %self.ppd_mod())
        
        conditionals=self.conditionals()
        if len(conditionals) > 0:
            out.append('Thief Abilities:')
        various=load_json('adnd2e','various')
        abilities=various['abilities']

        subclass=self.json['class']['class']
        parentclass=self.json['class']['parent']
        level=self.json['combat']['level/hitdice']
    
        
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
                    if "casting_level" in spell_progression[checkclass][key]:
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
