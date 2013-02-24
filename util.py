import sys
import datetime
#import envoy
import syslog
import os
from pwd import getpwnam
from grp import getgrnam
from simplejson import loads,dumps
from glob import iglob
from random import randrange
from pprint import pprint

def clearscr():
    os.system('clear')
    
def threelines():
    print "\n\n\n"

def highlight(out,clear=True):
    if clear:
        clearscr()
    bar=''
    for I in range(0,len(out) +4):
        bar="%s#" %bar
    print bar
    print "# %s #" %out
    print bar
    
def dice_list():
    return ['4','6','8','10','100','12','20']

def inrange(key1,key2):
        if '-' in key2:
            minimum=int(key2.split('-')[0])
            maximum=int(key2.split('-')[1])
        else:
            minimum=int(key2)
            maximum=minimum
        if int(key1) >= minimum and int(key1) <= maximum:
            return True
        else:
            return False

def list_chars(exclude=[]):
    chars=[]
    for entry in iglob("characters/*.json"):
        chars.append(os.path.basename(entry).rstrip('.json'))
    return list(set(chars) - set(exclude))

def load_json(source=None,base=None,filename=None):
    if not filename:
        return loads(open("%s/%s.json" %(source,base),'r').read())
    else:
        return loads(open(filename,'r').read())


def json_from_template(template={},old={},keypath=""):    
    def realkeys(template):
        rk=[]
        for key in template.keys():
            if key.startswith('__'):
                rk.append(key[3:])
            else:
                rk.append(key)
        return rk
    
    mydict={}
    for key in old.keys():
        if not key in realkeys(template):
            mydict[key]=old[key]
            
    for key in sorted(template.keys()):
        upper=False
        lower=False
        integer=False
        decimal=False
        validentries=[]
        if key.startswith('__'):
            realkey=key[3:]
        else:
            realkey=key
        if keypath == "":
            showpath=realkey
        else:
            showpath="%s:%s" %(keypath,realkey)

        if key.startswith("__U"):
            upper=True
        if key.startswith("__L"):
            lower=True
        if key.startswith("__I"):
            integer=True
        if key.startswith("__D"):
            decimal=True            
               
        if str(template[key]).startswith("__["):
            validentries=str(template[key]).lstrip('__[').rstrip(']').split(',')
        if key.startswith("__#"):
            if realkey in old:
                x=len(old[realkey])
            else:
                x=1
            numentries=smart_input("How many %s entries ?" %realkey,default=x,integer=True)
            print numentries
            subdic={}
            for I in range(0,numentries):
                try:
                    oldx=old[realkey][str(I)]
                except KeyError:
                    oldx={}
                subdic[str(I)]=json_from_template(template[key],oldx,"%s:%s" %(realkey,I))
            mydict[realkey]=subdic
        elif type(template[key]) == type({}):
            if realkey in old:
                mydict[realkey]=json_from_template(template[key],old[realkey],realkey)
            else:
                mydict[realkey]=json_from_template(template[key],{},realkey)
        elif realkey in old:
            mydict[realkey]=smart_input(showpath,old[realkey],validentries=validentries,upper=upper,lower=lower,decimal=decimal,integer=integer)
        else:
            mydict[realkey]=smart_input(showpath,validentries=validentries,upper=upper,lower=lower,decimal=decimal,integer=integer)
    return mydict
        
            

def rolldice(auto=True,numdice=1,numsides=20,modifier=0):
        print
        if not auto:
                while True:
                        print "Roll a %sd%s dice:" %(numdice,numsides)
                        try:
                                return int(raw_input())
                        except:
                                print "Error you must enter a number"
        else:
                total=0
                for I in range(1,numdice +1):
                        roll=randrange(1,numsides,1)
                        print "Rolled %s %s-sided dice: %s" %(I,numsides,roll)
                        total=total+roll
                
                total+=modifier       
                print "Total rolled: %s (modifier %s)" % (total,modifier)
                print
                return total
                


def smart_input(message='',default=None,integer=False,decimal=False,validentries=[],indent=0,lower=False,upper=False,confirm=''):
    if len(validentries) == 1:
        return validentries[0]
    print
    error="no input"
    istr=""
    for I in range(0,indent):
        istr=" %s" %istr
    istr=''
    while error <> '':
        if error <> '' and error <> "no input":
            print "%s%s%s" %(istr,istr,error)
            print "\n\n"
        error=''
        printmessage=message
        printmessage="%s%s" %(istr,printmessage)
        if default:
            printmessage="%s (%s)" %(printmessage,default)
        if len(validentries) > 0:
            for entry in validentries:
                print "%s%s (%s): %s" %(istr,istr,validentries.index(entry)+1,entry)       
        print "%s ?" %printmessage,
        user_input=raw_input()     
        if len(validentries) > 0:
            try:
                select=validentries[int(user_input) -1]
            except:
                select=user_input
            user_input=select          
            if not user_input in validentries:
                error='Error: entry not in list'        
        if lower:
            user_input=user_input.lower()
        if upper:
            user_input=user_input.upper()
        if default and user_input == '':
            user_input=default
        if integer:
            try:
                user_input = int(user_input)
            except Exception as E:
                error='Error:  %s' %E
        elif decimal:
            try:
                user_input = float(user_input)
            except Exception as E:
                error='Error:  %s' %E

        if len(confirm) > 0:
            if smart_input(confirm.replace('%I',user_input),default='n',validentries=['y','n'],indent=indent,lower=True) == 'y':
                return user_input
            else:
                error="Not confirmed - retrying"
        else:
            return user_input
 
def strtodic(s):
    """ Turns strings in format k1:v1,k2:v2,k3:v3 into dictionaries """
    D={}
    s = s.lstrip('{').rstrip('}') #If there are outer brackets, ignore them
    for pair in s.split(','):
        if ':' in pair: 
            K,V=pair.partition(':')[0],pair.partition(':')[2]
            D[K] = V
    return D
        

def option(optionx,expect=None):
    """ return an option from the parameter list if it exists """
    value = None
    paramlist=sys.argv
    if type(optionx) == int:
        # numbered parameter - return if available
        if len(paramlist) > optionx:
            value = paramlist[optionx]
    elif type(optionx) == str:
        # look for a string named optionx and pop it if found
        for p in range(len(paramlist)):
            if paramlist[p].lower().startswith(optionx.lower()):
                if len(paramlist[p]) > len(optionx) and paramlist[p][len(optionx)] == '=':
                    value = paramlist.pop(p)[len(optionx)+1:]
                else:
                    value = paramlist.pop(p) and True
                break
    if expect and expect == 'json' and value:
        try:
            value = loads(value)
        except Exception,e:
            print "util.option: invalid json format"
            value = None
    return value


class Character:
    cast_remaining=0
    spell_target=None
    json={}
    auto=False
    weapon=0
    def __init__(self,json,autoroll=False):
        self.json=json
        self.json['combat']['thac0']=self.__get_thac0()
        self.auto=autoroll
        self.json['combat']['saving_throws']=self.__get_saving_throws()
        if self.is_monster():
            self.json['combat']['hitpoints']=rolldice(self.auto,int(self.json['combat']["level/hitdice"]),8)
            self.json['combat']["max_hp"]=self.json['combat']['hitpoints']
        
    def get_json(self):
        return self.json
        
    def heal(self,amount):
        self.json['combat']['hitpoints'] += amount
        if amount > self.json['combat']['max_hp']:
            self.json['combat']['hitpoints'] = self.json['combat']['max_hp']
        highlight("%s receives healing. Hitpoints now %s" %(self.firstname(),self.json['combat']['hitpoints']),clear=False)
        self.save()
        
    def take_damage(self,damage):
        if damage >= int(self.json['combat']['hitpoints']):
            if not self.saving_throw('ppd'): #Roll saving throw against death
                self.json['combat']['hitpoints'] = 0
                self.save()
                highlight("%s has died !" %self.firstname(),clear=False)
                return False
        else:
            self.json['combat']['hitpoints'] -= damage
            self.save()
            highlight("%s takes %s damage. %s hitpoints remaining" %(self.firstname(),damage,self.json['combat']['hitpoints']),clear=False)
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
        highlight('%s: spell casting interrupted %s !' %(self.firstname(),by),clear=False)
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
        highlight('%s status saved to disk' %self.firstname(),clear=False)
        
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
        print "%s Tries to roll a saving throw against %s" %(self.firstname(),prettyname)
        print "%s needs to roll %s" %(self.firstname(),target)
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

      
    def is_misile(self,weaponidx):
        return self.json['combat']['weapons'][str(weaponidx)]['type'] == "misile"
        
    def attack_roll(self,target,mod):
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
        print "Name: %s %s" %(self.json['personal']['name']['first'],self.json['personal']['name']['last'])
        print "Alignment: %s-%s" %(self.json['personal']['alignment']['law'],self.json['personal']['alignment']['social'])
        print "Race: %s" %self.json['personal']['race']
        print "Class %s:%s" %(self.json['class']['parent'],self.json['class']['class'])
        print "XP %s/%s" %(self.json['personal']['xp'],'TODO')
        print "Combat stats:"
        for key in self.json['combat']:
            if key not in ['weapons','saving_throws']:
                print "    %s: %s" %(key,self.json['combat'][key])
        print "     Saving throws:"
        for key in self.json['combat']['saving_throws']:
            prettyname=load_json('adnd2e','saving_throws')['names'][key]
            print "         %s: %s" %(prettyname,self.json['combat']['saving_throws'][key])
            
        print "Ability scores:"
        for key in self.json['abilities']:
            print "     %s: %s" %(key,self.json['abilities'][key])
        print "Total attacks per round: %s" %self.num_attacks()
        print "Weapons: %s" %self.num_weapons()
        for key in self.json['combat']['weapons']:
            print "     Weapon: %s" %key
            for stat in self.json['combat']['weapons'][key]:
                print "         %s: %s" %(stat,self.json['combat']['weapons'][key][stat])
        print "Modifiers(first weapon):"
        print "     Chance to hit: %s" %self.to_hit_mod()
        print "     Damage: %s" %self.dmg_mod()
        print "     Defense (modifies AC down): %s" %self.def_mod()
        print "     PPD Save: %s" %self.ppd_mod()

    def firstname(self):
        return self.json['personal']['name']['first']
         
    def __get_thac0(self):
        if self.json['personal']['race'] == "creature":
            key="creature"
        else:
            key=self.json['class']['parent']
        thac0s=load_json("adnd2e","thac0")[key]
        for key2 in thac0s.keys():
            if inrange(self.json['combat']["level/hitdice"],key2):
                return int(thac0s[key2])

