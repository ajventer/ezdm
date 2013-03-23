#!/usr/bin/env python

import sys
import os
from simplejson import loads,dumps
from ezdm_libs.util import smart_input,load_json,json_from_template,highlight,say,rolldice,heal_dice
from ezdm_libs.character import Character,list_chars

def editor(json,path=""):
    key="next"
    mydict=json
    while not key in ['quit','cancel']:
        actions=[]        
        for item in mydict.keys():
            actions.append ("%s:%s" %(item,mydict[item]))
        if path=="":
            actions.append('quit')
        else:
            actions.append('cancel')
        key=smart_input('Key to edit (%s)' %path,validentries=actions)
        if ':' in key:
            key=key.split(':')[0]
        if not key in ['quit','cancel']:
            if type(mydict[key]) == type({}):
                mydict[key]=editor(mydict[key],key)
            else:
                mydict[key]=smart_input("%s %s" %(path,key),mydict[key])
    return mydict
        

if __name__=='__main__': 
    charlist=list_chars()
    basedir='characters'
    name=smart_input("Character to edit",upper=True,validentries=charlist.keys())
    auto=True
    char=Character(load_json(basedir,charlist[name]),auto)
    updated=Character(editor(char.json),auto)
    updated.save()
    
    


        
