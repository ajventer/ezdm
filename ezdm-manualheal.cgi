#!/usr/bin/env python

import sys
import os
from ezdm_libs.util import smart_input,load_json,json_from_template,highlight,say,rolldice,heal_dice,web,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,hide,dice_list,dicthide
from ezdm_libs.character import Character,list_chars

def main():
    charlist=list_chars()
    basedir='characters'
    name=smart_input("Character trying",upper=True,validentries=charlist.keys())
    auto=smart_input('Use computer dice',validentries=['y','n']) == 'y'
    char=Character(load_json(basedir,charlist[name]),auto)
    dice=smart_input('Roll for healing',validentries=['y','n']) == 'y'
    if dice:
        char.heal(heal_dice(char.autoroll()))
    else:
        char.heal(smart_input('Heal by how much',integer=True,default=1))

def getdata():
    formdic={}
    formdic["Character"]=list_chars().keys()
    formdic["Roll for healing"]=["Yes","No"]
    formheader(border=3)
    dictinput(formdic)
    formfooter()
    
def healamount(data):
    highlight("Healing %s "%data['Character'])
    formheader(border=3)
    dicthide(data)
    hide('ready','yes')
    if data["Roll for healing"]  == 'Yes':
        webinput('Healing dice sides','sides',dice_list())
        webinput('Number of healing dice','numdice','1')
    else:
        webinput('Heal by','healby','1')
    formfooter()
    
    
def webmain():
    cgiheader('EZDM - Manual heal')
    data=parsecgi()
    if not 'submit' in data:
        getdata()
    elif not "ready" in data:
        healamount(data)
    else:
        char=Character(load_json('characters',list_chars()[data['Character']]),True)
        if data["Roll for healing"] == "Yes":
            char.heal(rolldice(True,int(data['numdice']),int(data['sides'])))
        else:
            char.heal(int(data['healby']))
    cgifooter()
    

if __name__=='__main__': 
    if web():
        webmain()
    else:
        main()
