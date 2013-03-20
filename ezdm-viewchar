#!/usr/bin/env python
from ezdm_libs.util import option,load_json,smart_input,highlight,say,web,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput
from ezdm_libs.character import Character,list_chars
import sys

def viewchar(name):
    json=load_json('characters',name)
    character=Character(json,True) 
    return character.pprint()   

def main():
    highlight('EZDM - Character viewer')
    clist=list_chars()
    if len(clist) == 0:
        sys.exit()
    name=smart_input("Select Character to view",upper=True,validentries=clist.keys())    
    say(viewchar(clist[name]))

def webmain():
    cgiheader('EZDM - Character viewer')
    data=parsecgi()
    if not 'character' in data:
        formheader()
        webinput("Select character to view","character",list_chars().keys())
        formfooter()
    else:
        say(viewchar(list_chars()[data['character']]))
    cgifooter()

if __name__=='__main__': 
    if web:
        webmain()
    else:
        main()

