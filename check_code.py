#!/usr/bin/env python
from os import system
from sys import argv
from glob import glob

SCRIPTS=['ezdm-mkcs','ezdm-xp_tool','ezdm-quick_combat','ezdm','ezdm-viewchar','ezdm-dice_roller']

def script_list():
    return SCRIPTS

def check_list(LIST):
    for SCRIPT in LIST:
        print "Checking %s " % (SCRIPT)
        if system("%s %s %s 2>/dev/null" % (CMD,OPTS,SCRIPT)) != 0:
            print "Errors found in %s" % (SCRIPT)
            sys.exit(1)
    

if __name__=='__main__': 
    LIBS=glob('ezdm_libs/*.py')
    OPTS=" -E -r n -i n -f colorized "
    if len(argv) == 0:
        print "Usage check_code.py <path to pylint>"
        sys.exit(1)
    CMD=argv[1]
    check_list(SCRIPTS)
    check_list(LIBS)
    

