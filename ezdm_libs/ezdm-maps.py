#!/usr/bin/env python
#First version limited automation
import sys
import os
from simplejson import loads,dumps
from ezdm_libs.util import list_icons,clearscr,smart_input,load_json,json_from_template,highlight,say,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,template_conditional,validate_json
from ezdm_libs.util import cgihide as hide
from ezdm_libs.item import Item,list_items
from ezdm_libs import web,gui
from ezdm_libs.map import Map,list_maps,MapBlock



def view_map(name):
    if name:
        mymap=Map(load_json('maps',name))
    else:
        mymap=Map()
        mymap.json['name'] = 'New Map'
    mymap.draw(border=5)

def editmapmenu():
    formheader(title='Edit Map')
    hide('mapname',data['mapname'])
    webinput('Add rows','addy',default='0')
    webinput ('Add columns','addx',default='0')
    webinput('Background fill','bgfil',default=list_icons(),selected="blank.png")
    formfooter()
    
    
def newmapmenu():
    formheader(title='New Map')
    maps=list_maps().keys()
    maps.insert(0,'New')
    if len(maps) > 1:
        webinput('Load existing map','mapname',maps)
    webinput('Name','newname','')
    formfooter()
    

def layout(data):
    print "<table border=0  height=100%>"
    print "<tr><td width=100 valign=top>"
    name=''
    if 'mapname' in data:
        name=data['mapname']
        editmapmenu()
    else:
        name=''
        newmapmenu()
    print "</td><td>"
    view_map(name)
    print "</td></tr></table>"
    

if __name__=='__main__':
    cgiheader(title='EZDM Map Editor')
    data=parsecgi()
    if 'mapname' in data and data['mapname'] <> 'New':
        data['mapname']=list_maps()[data['mapname']]   
    elif 'newname' in data:
        mymap=Map()
        mymap.json['name'] = data['newname']
        mymap.save()
        data['mapname'] = mymap.filename(None)
    if 'addy' in data:
        mymap=Map(load_json('maps',data['mapname']))
        h=int(mymap.json['size']['h'])
        h += int(data['addy'])
        w=int(mymap.json['size']['w'])
        w += int(data['addx'])
        mymap.set_size(w,h)
        block=MapBlock()
        block.json['icon'] = data['bgfil']
        mymap.fill(block)
        mymap.save()
    layout(data)    
    cgifooter()
    
    
