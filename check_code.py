#!/usr/bin/env python
from os import system,path,symlink
from sys import argv,exit
from glob import glob

SCRIPTS=['ezdm-cs.cgi','ezdm-xp_tool.cgi','ezdm-quick_combat.cgi','ezdm.cgi','ezdm-viewchar.cgi','ezdm-dice_roller.cgi','ezdm-tryability.cgi','ezdm-manualheal.cgi','ezdm-mkitem.cgi','ezdm-inventory','cgi-server.ezdm','ezdm-cs.cgi','combat-server.ezdm']

def script_list():
    return SCRIPTS


def check_list(LIST,try_import=False):
    for SCRIPT in LIST:
        print

        print "Checking %s " % (SCRIPT)
        if system("%s %s %s 2>/dev/null" % (CMD,OPTS,SCRIPT)) != 0:
            print "Errors found in %s" % (SCRIPT)
            if try_import:
                system('(cd %s ; python -c "import %s")' %(path.dirname(SCRIPT),path.basename(SCRIPT).rstrip('.py')))
            print
            print
            print
            sys.exit(1)
    

if __name__=='__main__': 
    LIBS=glob('ezdm_libs/*.py')
    OPTS=" -E -r n -i n -f colorized "
    if len(argv) == 0:
        print "Usage check_code.py <path to pylint>"
        exit(1)
    CMD=argv[1]
    check_list(LIBS,True)
    check_list(SCRIPTS)
    link()
    
    

