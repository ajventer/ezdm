#!/usr/bin/env python
#First version limited automation
import sys
import os
from simplejson import loads,dumps
from ezdm_libs.util import clearscr,smart_input,load_json,json_from_template,highlight,say,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,hide,template_conditional,validate_json
from ezdm_libs.item import Item,list_items
from ezdm_libs import web,gui

def main():
    save='n'
    old = {}
    while not 'y' in save.lower():
        highlight("EZDM item creator")
        template=load_json('adnd2e','template_item')
        if len(old) == 0:
            basedir="items"
            itemlist=list_items()
            if len(itemlist) >0:
                load=smart_input("Load defaults from existing item",validentries=["y","n"],default='y')
            else:
                load='n'

            if load == "y":
                name=smart_input("%s "%(basedir),upper=False,validentries=itemlist.keys())
                old=load_json(basedir,itemlist[name])
        item=Item(json_from_template(template=template['core'],old=old,conditional=template['conditional']))    
        say(item.json)
        save=smart_input("Save this %s ?" %(basedir.rstrip('s')),default="n",validentries=["y","n"],lower=True)
        if 'y' in save:
            item.save()
        else:
            old=item.json

def getdata():
    items=list_items().keys()
    items.insert(0,'New')
    formheader(border=3)
    webinput('Use defaults from item:','item',items)
    formfooter()
    
def itemsheet(data):
    formheader(border=3)
    hide('basic_sheet','yes')
    hide('item',data['item'])
    template=load_json('adnd2e','template_item')
    if data['item'] == 'New':
        old={}
    else:
        old=load_json('items',list_items()[data['item']]) 
    json_from_template(template['core'],old)
    formfooter()

def cond(data):
    highlight("Conditional entries")
    formheader(border=3) 
    hide('basic_sheet','yes')
    hide('cond_sheet','yes')
    hide('item',data['item'])
    del data['item']
    del data['basic_sheet']
    del data['submit']    
    template=load_json('adnd2e','template_item')
    result=validate_json(template,data)
   
    json_from_template(template=template['core'],old=result)
    template_conditional(result,template['conditional'])
    formfooter()    
    
def save_item(data):
    highlight('Saving item %s' %data['item'])
    del data['item']
    del data['basic_sheet']
    del data['submit']   
    template=load_json('adnd2e','template_item')
    result=validate_json(template,data)   
    item=Item(result)
    item.save()
 
        

def webmain():
    cgiheader('EZDM Item Creator')
    data=parsecgi()
    if not 'submit' in data:
        getdata()
    elif not 'basic_sheet' in data:
        itemsheet(data)
    elif not 'cond_sheet' in data:
        cond(data)
    else:
        save_item(data)
    cgifooter()
    

if __name__=='__main__': 
    if web():
        webmain()
    else:
        main()
