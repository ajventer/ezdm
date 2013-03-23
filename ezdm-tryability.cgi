#!/usr/bin/env python

import sys
import os
from simplejson import loads,dumps
from ezdm_libs.util import select_char,smart_input,load_json,json_from_template,highlight,say,rolldice,web,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,hide
from ezdm_libs.character import Character,list_chars

def main():
    charlist=list_chars()
    basedir='characters'
    name=smart_input("Character trying",upper=True,validentries=charlist.keys())
    auto=smart_input('Use computer dice',validentries=['y','n']) == 'y'
    char=Character(load_json(basedir,charlist[name]),auto)
    ability=smart_input("Ability being tried",validentries=char.conditionals().keys())
    if char.tryability(ability):
        say("%s succeeded with %s" %(char.displayname(),ability))
    else:
        say("%s failed at %s" %(char.displayname(),ability))

def getdata():
    formheader(border=3)
    select_char(list_chars().keys())
    formfooter()

def getability(data):
    formheader(border=3)
    hide('character',data['character'])
    hide('autodice',data['autodice'])
    auto=data['autodice'] == True
    c=Character(load_json('characters',list_chars()[data['character']]),auto)
    webinput('Ability','ability',c.conditionals().keys())
    webinput('Custom modifier','modifier','0')
    formfooter()


def webmain():
    cgiheader('EZDM - Try Ability')
    data=parsecgi()
    if not 'submit' in data:
        getdata()
    elif not 'ability' in data:
        getability(data)
    else:
        c=Character(load_json('characters',list_chars()[data['character']]),True)
        if c.tryability(data['ability'],int(data['modifier'])):
            highlight("%s succeeded with %s" %(c.displayname(),data['ability']))
        else:
            highlight("%s failed at %s" %(c.displayname(),data['ability']))
            
    cgifooter()
    

if __name__=='__main__': 
    if not web():
        main()
    else:
        webmain()
