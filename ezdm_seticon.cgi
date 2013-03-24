#!/usr/bin/env python
#First version limited automation
import sys
import os
from simplejson import loads,dumps
from ezdm_libs.util import clearscr,smart_input,load_json,json_from_template,highlight,say,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,template_conditional,validate_json
from ezdm_libs.util import cgihide as hide
from ezdm_libs.item import Item,list_items
from ezdm_libs import web,gui
from ezdm_libs.character import Character
from ezdm_libs.item import Item
import cgi


def save(source,base,icon):
    OutData=None
    json=load_json(source,base)
    json['icon'] = icon
    if source == 'characters':
        OutData=Character(json,autoroll=True)
    elif source == 'items':
        OutData=Item(json)
    highlight("%s icon updated to %s" %(OutData.displayname(),icon))
    print "<center><img src=ezdm-iconview.cgi?icon=%s></center>" %icon
    OutData.save()

if __name__ == "__main__":
    cgiheader('EZDM - Icon tool')
    data=parsecgi()

    save(data['source'],data['base'],data['selected'])
    cgifooter()

