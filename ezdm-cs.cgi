#!/usr/bin/env python

import sys
import os
from simplejson import loads,dumps
from ezdm_libs.util import smart_input,load_json,json_from_template,highlight,say,web,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput,dictinput,hide,template_conditional,validate_json
from ezdm_libs.character import Character,list_chars

def getdata():
    characters=list_chars().keys()
    characters.append('New')
    formheader(border=3)
    webinput('Character:','character',characters)
    formfooter()


def cond(data):
    highlight('Entries specific to a given class')
    formheader(border=3) 
    if 'submit' in data:
        del data['submit']
    hide('next',data['character'])
    if 'character' in data:
        del data['character']
    template=load_json('adnd2e','template_cs')
    result=validate_json(template,data)
    
    json_from_template(template=template['core'],old=result,conditional=template['conditional'])

    result=template_conditional(result,template['conditional'])
    formfooter()
    

if __name__=='__main__': 
    if not web():
        print "Error - this interface only works via the web"
        sys.exit(1)
    cgiheader('EZDM - Character Sheets')
    data=parsecgi()
    if not 'submit' in data:
        getdata()
    elif not 'abilities::con' in data:
        formheader(border=3)  
        hide('character',data['character'])
        template=load_json('adnd2e','template_cs')
        if data['character'] == 'New':
            old={}
        else:
            old=load_json('characters',list_chars()[data['character']])            
        json_from_template(template=template['core'],old=old,conditional=template['conditional'])
        formfooter()
    elif not 'next' in data:
        cond(data)
    else:
        del data['submit']
        cname=data['next']
        del data['next']
        template=load_json('adnd2e','template_cs')
        data=validate_json(template,data)
        if cname <> 'New':
            c=Character(load_json('characters',list_chars()[cname]),True)
        else:
            c=Character(data,True)
        c.save()
        say(c.pprint())

        
    cgifooter()
        
    


        
