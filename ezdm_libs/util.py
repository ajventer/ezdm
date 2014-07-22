import sys
import datetime
import os
from ezdm_libs import get_sys_data, get_user_data
from simplejson import loads, dumps
from glob import iglob, glob
from random import randrange
from pprint import pprint


def readkey(key, json, default=None):
    if not json or not isinstance(json, dict):
        raise ValueError("%s must be a dict" % repr(json))
    key = key.strip('/')
    keylist = key.split('/')
    for k in keylist:
        k = k.replace('/', '')
        if not k in json:
            if default:
                return default
            else:
                raise KeyError("Key %s from path %s not found in %s" % (k, key, json))
        if keylist.index(k) == len(keylist) - 1:
            return json[k]
        else:
            ks = '/'.join(keylist[keylist.index(k) + 1:])
            return json_readkey(ks, json[k])


def writekey(key, value, json):
    parse = 'json'
    for k in key.strip('/').split('/'):
        k = k.replace('/', '')
        parse = '%s[%s]' % (parse, k)
    parse = '%s = %s' % (parse, value)
    exec parse


def load_icon(icon='blank.png'):
    syspath=get_sys_data('icons')
    userpath=get_user_data('icons')
    path=''
    if os.path.exists(os.path.join(syspath,icon)):
        path=os.path.join(syspath,icon)
    if os.path.exists(os.path.join(userpath,icon)):
        path=os.path.join(userpath,icon) #User data overwrites system data if the same file exists in both
    if path=='':
        path=os.path.join(syspath,'blank.png')
    return path

def find_files(source, needle=None, basename=False, strip=''):
    matches =  glob(os.path.join(get_user_data(source), needle))
    matches += glob(os.path.join(get_sys_data(source), needle))
    if basename:
        matches = [os.path.basename(match) for match in matches]
    if strip:
        matches = [match.replace(strip,'') for match in matches]
    return list(set(matches))


def readfile(source, name, json=False):
    filenames = find_files(source, name)
    if filenames:
        filename = filenames[0]
    if not json:
        return open(filename,'r').read()
    return loads(open(filename,'r').read())


def smart_input(*args):
    print "Smart_input: %s%s" %( args, kwargs)
    pass

def say(*args):
    print "Say: %s%s" %( args, kwargs)

    
def attack_mods():
    return loads(open(os.path.join(get_user_data('adnd2e'),"attack_mods.json")).read())

    

def price_in_copper(gold,silver,copper):
    s=gold*10 + silver
    c=s*10+copper
    return c

def convert_money(copper):
    money={"gold":0,"silver":0,"copper":copper}
    while money['copper'] > 10:
        money['silver'] += 1
        money['copper'] -= 10
    while money['silver'] > 10:
        money['gold'] += 1
        money['silver'] -= 10
    return money
        

        
def heal_dice(auto=True):
        sides=smart_input('Healing dice sides',validentries=dice_list(),integer=True)
        num=smart_input('Number of healing dice to roll',integer=True)
        return rolldice(auto,num,sides)        



def highlight(out,clear=False,sayit=True):
    if clear:
        clearscr()
    bar=''
    output=[]
    if not web:
        output.append("# %s #" %(out))
    else:
        output.append('<center><table border=10 cellpadding=0 cellspacing=0><tr><td align=center valign=center bgcolor=darkgray>')
        output.append("<b> %s </b>" %(out))
        output.append('</td></tr></table></center>')
    if sayit:
        say(output)
    else:
        return output
    
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
            
def rolldice(auto=True,numdice=1,numsides=20,modifier=0,quiet=False,wsgi=False):
    output=[]
    if not auto:
        return smart_input("Roll a %sd%s dice:" %(numdice,numsides),integer=True)
    else:
            total=0
            for I in range(1,numdice +1):
                    roll=randrange(1,numsides,1)
                    output.append("Rolled %s %s-sided dice: %s" %(I,numsides,roll))
                    total=total+roll
            
            total+=modifier       
            output.append("Total rolled: %s (modifier %s)" % (total,modifier))
            if not quiet:
                say(output)
            if wsgi:
                return (total,'<br>'.join(output))
            return total


