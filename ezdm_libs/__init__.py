import os
import sys

_gui=True
__web=False


if '--web' in sys.argv or sys.argv[0].endswith('.cgi'):
    __gui=False
    __web=True
 
elif '--console' in sys.argv:
    _gui=False
    _web=False
else:
    try:
        import easygui as eg
    except:
        _gui=False
        
def gui():
    return _gui

def web():
    return __web

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_sys_data(path):
    datapath=os.path.join(_ROOT,path)
    if os.path.exists(datapath):
        return  datapath
    else:
        return None

