#!/usr/bin/env python
"""Main EZDM console"""
from ezdm_libs.util import smart_input, highlight, gui, web,cgiheader,cgifooter,parsecgi,formheader,formfooter,webinput
import os
import sys

def main(ACTIONLIST):
    ACTION = ''
    while not ACTION.lower() =='quit':
        highlight('Welcome to EZDM')
        ACTIONS = sorted(ACTIONLIST.keys())
        ACTIONS.append('Quit')
        ACTION = smart_input('Please select an activity', validentries=ACTIONS)
        if ACTION.lower() != 'quit':           
            COMMAND = ACTIONLIST[ACTION]
            if not gui():
                COMMAND = "%s --console" % COMMAND
            print "Running %s" % COMMAND
            os.system(os.path.join(PATH, COMMAND))
            if not gui():
                raw_input()

def webmain(ACTIONLIST):
    cgiheader('Welcome to EZDM',False)
    data=parsecgi()
    if 'combat' in data:
        print '''
<script type="text/javascript">
<!--

window.location.port=8001
//-->
</script>        
        '''
        
    del ACTIONLIST["Edit character sheet"]
    del ACTIONLIST['Create a new character sheet']
    del ACTIONLIST['Combat !']
    ACTIONLIST['Create/Edit Character Sheet']='ezdm-cs'
    
    for key in ACTIONLIST.keys():
        print '<a href="%s.cgi">%s</a><br>' %(ACTIONLIST[key],key)
    print '<a target="_blank"  href="?combat=yes" >Combat !</a><br>'
    cgifooter(False)

if __name__ == '__main__': 
    PATH = os.path.dirname(sys.argv[0])

    ACTIONLIST = {'View a character sheet':'ezdm-viewchar', 'Create a new character sheet':'ezdm-mkcs', 'Combat !':'ezdm-quick_combat', 'Grant XP to character':'ezdm-xp_tool', 'Roll dice':'ezdm-dice_roller',"Heal character":"ezdm-manualheal","Try ability":"ezdm-tryability","Edit character sheet":"ezdm-editcs","Manage character inventory":"ezdm-inventory","Create/Edit Item":"ezdm-mkitem"}

    if not web():
        main(ACTIONLIST)
    else:
        webmain(ACTIONLIST)
