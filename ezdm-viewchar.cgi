#!/usr/bin/env python
from ezdm_libs.util import get_set_icon,option,load_json,smart_input,highlight,say,web,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput
from ezdm_libs.character import Character,list_chars
import sys



def main():
    highlight('EZDM - Character viewer')
    clist=list_chars()
    if len(clist) == 0:
        sys.exit()
    name=smart_input("Select Character to view",upper=True,validentries=clist.keys())  
    c=Character(load_json('characters',clist[name]),autoroll=True)  
    c.viewchar()

def webmain():
    cgiheader('EZDM - Character viewer')
    data=parsecgi()
    if not 'character' in data:
        formheader()
        webinput("Select character to view","character",list_chars().keys())
        formfooter()
    else:
        c=Character(load_json('characters',list_chars()[data['character']]),autoroll=True)  
        c.viewchar()
    cgifooter()

if __name__=='__main__': 
    if web:
        webmain()
    else:
        main()

