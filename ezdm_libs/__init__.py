import os
import sys

__gui=True
__web=False

print sys.argv[0]
if '--web' in sys.argv or sys.argv[0].endswith('.cgi') or sys.argv[0].endswith('.ezdm'):
    __gui=False
    __web=True
 
elif '--console' in sys.argv:
    __gui=False
    __web=False
else:
    try:
        import easygui as eg
    except:
        __gui=False
        
def gui():
    return __gui

def web():
    return __web

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_sys_data(path):
    datapath=os.path.join(_ROOT,path)
    if os.path.exists(datapath):
        return  datapath
    else:
        return None

