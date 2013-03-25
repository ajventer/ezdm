#!/usr/bin/env python
#First version limited automation
import sys
import os
from simplejson import loads,dumps
from ezdm_libs.util import clearscr,smart_input,load_json,json_from_template,highlight,say,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,template_conditional,validate_json
from ezdm_libs.util import cgihide as hide
from ezdm_libs.item import Item,list_items
from ezdm_libs import web,gui
from ezdm_libs.map import Map,list_maps



def view_map(name):
    if name:
        mymap=Map(load_json('maps',name))
    else:
        mymap=Map()
        mymap.json['name'] = 'New Map'
    mymap.draw(border=5)

def editmapmenu():
    print "blah"
    
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
    if 'newname' in data:
        mymap=Map()
        mymap.json['name'] = data['newname']
        mymap.save()
        data['name'] = data['newname']
    layout(data)    
    cgifooter()
    
    
